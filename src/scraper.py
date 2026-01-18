import asyncio
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional, AsyncGenerator
from contextlib import asynccontextmanager

from telethon import TelegramClient, functions
from telethon.tl.types import (
    Message, 
    MessageMediaPhoto, 
    MessageMediaDocument,
    Channel,
    User
)
from telethon.errors import (
    FloodWaitError,
    ChannelPrivateError,
    ChatAdminRequiredError,
    UsernameNotOccupiedError
)
import aiofiles

from src.common.config import config
from src.common.logger import (
    logger,
    get_task_logger,
    log_scraping_start,
    log_scraping_complete,
    log_error_with_context
)

class TelegramScraper:
    """Production-grade Telegram scraper with error handling and rate limiting"""
    
    def __init__(self, max_messages_per_channel: int = 1000):
        """
        Initialize Telegram scraper
        
        Args:
            max_messages_per_channel: Maximum number of messages to scrape per channel
        """
        self.client = None
        self.max_messages = max_messages_per_channel
        self.scraper_logger = get_task_logger("scraping")
        
        # Setup paths
        self.raw_data_path = Path(config.RAW_DATA_PATH)
        self.messages_path = self.raw_data_path / "telegram_messages"
        self.images_path = self.raw_data_path / "images"
        
        # Create directories
        self.messages_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        self.scraper_logger.info(
            "Initialized Telegram scraper",
            extra={
                "max_messages_per_channel": max_messages_per_channel,
                "raw_data_path": str(self.raw_data_path),
                "channels_to_scrape": config.get_telegram_channels()
            }
        )
    
    @asynccontextmanager
    async def telegram_session(self):
        """Context manager for Telegram client session"""
        try:
            await self._initialize_client()
            yield self.client
        finally:
            await self._close_client()
    
    async def _initialize_client(self):
        """Initialize Telegram client with retry logic"""
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.client = TelegramClient(
                    'medical_scraper_session',
                    int(config.TELEGRAM_API_ID),
                    config.TELEGRAM_API_HASH,
                    device_model="Medical Scraper v1.0",
                    system_version="Linux",
                    app_version="1.0.0",
                    lang_code="en",
                    system_lang_code="en"
                )
                
                await self.client.start(phone=config.TELEGRAM_PHONE, force_sms=True)
                
                # Get current user info for logging
                me = await self.client.get_me()
                self.scraper_logger.info(
                    "Telegram client initialized successfully",
                    extra={
                        "user_id": me.id,
                        "username": me.username,
                        "attempt": attempt + 1
                    }
                )
                return
                
            except FloodWaitError as e:
                wait_time = e.seconds
                self.scraper_logger.warning(
                    f"Flood wait error. Waiting {wait_time} seconds...",
                    extra={"wait_seconds": wait_time, "attempt": attempt + 1}
                )
                time.sleep(wait_time)
                
            except Exception as e:
                self.scraper_logger.error(
                    f"Failed to initialize Telegram client (attempt {attempt + 1}): {e}",
                    extra={"attempt": attempt + 1}
                )
                if attempt == max_retries - 1:
                    raise
                time.sleep(retry_delay)
    
    async def _close_client(self):
        """Safely close Telegram client"""
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            self.scraper_logger.info("Telegram client disconnected")
    
    async def scrape_all_channels(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape all configured Telegram channels
        
        Returns:
            Dictionary with channel names as keys and list of messages as values
        """
        all_messages = {}
        
        async with self.telegram_session():
            channels = config.get_telegram_channels()
            
            for channel_username in channels:
                try:
                    messages = await self.scrape_channel(channel_username)
                    all_messages[channel_username] = messages
                    
                    # Save after each channel for resilience
                    await self._save_channel_messages(channel_username, messages)
                    
                except Exception as e:
                    log_error_with_context(
                        e,
                        {
                            "channel": channel_username,
                            "action": "channel_scraping",
                            "error_type": type(e).__name__
                        }
                    )
                    continue
        
        self.scraper_logger.info(
            "Completed scraping all channels",
            extra={
                "total_channels": len(channels),
                "successful_channels": len(all_messages),
                "total_messages": sum(len(msgs) for msgs in all_messages.values())
            }
        )
        
        return all_messages
    
    async def scrape_channel(self, channel_username: str) -> List[Dict[str, Any]]:
        """
        Scrape messages from a specific Telegram channel
        
        Args:
            channel_username: Channel username or ID (e.g., '@CheMed123')
        
        Returns:
            List of message dictionaries
        """
        start_time = time.time()
        messages_data = []
        
        log_scraping_start(channel_username, self.max_messages)
        
        try:
            # Get channel entity
            channel = await self._get_channel_entity(channel_username)
            if not channel:
                return []
            
            # Create channel-specific directories
            channel_slug = self._slugify_channel_name(channel_username)
            channel_image_path = self.images_path / channel_slug
            channel_image_path.mkdir(exist_ok=True)
            
            # Scrape messages
            message_count = 0
            async for message in self._iter_channel_messages(channel):
                if message_count >= self.max_messages:
                    self.scraper_logger.info(
                        f"Reached maximum messages ({self.max_messages}) for {channel_username}"
                    )
                    break
                
                message_data = await self._process_message(
                    message, channel_username, channel_image_path
                )
                
                if message_data:
                    messages_data.append(message_data)
                    message_count += 1
                
                # Log progress
                if message_count % 50 == 0:
                    self.scraper_logger.info(
                        f"Scraped {message_count} messages from {channel_username}",
                        extra={
                            "channel": channel_username,
                            "progress": message_count,
                            "percentage": (message_count / self.max_messages) * 100
                        }
                    )
            
            duration = time.time() - start_time
            log_scraping_complete(channel_username, len(messages_data), duration)
            
        except Exception as e:
            log_error_with_context(
                e,
                {
                    "channel": channel_username,
                    "action": "channel_scraping",
                    "messages_scraped": len(messages_data)
                }
            )
            raise
        
        return messages_data
    
    async def _get_channel_entity(self, channel_username: str) -> Optional[Channel]:
        """Get channel entity with error handling"""
        try:
            return await self.client.get_entity(channel_username)
        except (ChannelPrivateError, ChatAdminRequiredError) as e:
            self.scraper_logger.warning(
                f"Cannot access channel {channel_username}: {e}",
                extra={
                    "channel": channel_username,
                    "error": type(e).__name__,
                    "action": "channel_access"
                }
            )
            return None
        except UsernameNotOccupiedError:
            self.scraper_logger.error(
                f"Channel {channel_username} does not exist",
                extra={"channel": channel_username, "action": "channel_lookup"}
            )
            return None
        except Exception as e:
            log_error_with_context(
                e,
                {
                    "channel": channel_username,
                    "action": "channel_lookup",
                    "error_type": type(e).__name__
                }
            )
            return None
    
    async def _iter_channel_messages(self, channel: Channel) -> AsyncGenerator[Message, None]:
        """Iterate through channel messages with rate limiting"""
        try:
            async for message in self.client.iter_messages(
                channel,
                limit=self.max_messages,
                reverse=False  # Chronological order (oldest first)
            ):
                yield message
                
        except FloodWaitError as e:
            self.scraper_logger.warning(
                f"Rate limited. Waiting {e.seconds} seconds before resuming...",
                extra={"wait_seconds": e.seconds, "action": "rate_limiting"}
            )
            time.sleep(e.seconds)
            # Resume from where we left off
            async for message in self._iter_channel_messages(channel):
                yield message
    
    async def _process_message(
        self, 
        message: Message, 
        channel_name: str, 
        image_path: Path
    ) -> Optional[Dict[str, Any]]:
        """Process a single message and extract relevant data"""
        
        # Skip service messages (joins, leaves, etc.)
        if not message.message and not message.media:
            return None
        
        message_data = {
            "message_id": message.id,
            "channel_name": channel_name,
            "message_date": message.date.isoformat() if message.date else None,
            "message_text": message.text or "",
            "has_media": bool(message.media),
            "views": message.views or 0,
            "forwards": message.forwards or 0,
            "reactions": self._extract_reactions(message),
            "image_path": None,
            "media_type": None,
            "scraped_at": datetime.utcnow().isoformat()
        }
        
        # Handle media
        if message.media:
            message_data.update(await self._handle_media(message, channel_name, image_path))
        
        # Extract entities (mentions, hashtags, URLs)
        message_data.update(self._extract_entities(message))
        
        # Calculate message metrics
        message_data.update({
            "message_length": len(message_data["message_text"]),
            "has_links": bool(message_data.get("urls", [])),
            "has_hashtags": bool(message_data.get("hashtags", [])),
            "has_mentions": bool(message_data.get("mentions", []))
        })
        
        return message_data
    
    async def _handle_media(
        self, 
        message: Message, 
        channel_name: str, 
        image_path: Path
    ) -> Dict[str, Any]:
        """Handle media files in messages"""
        result = {"media_type": None, "image_path": None}
        
        try:
            if isinstance(message.media, MessageMediaPhoto):
                result["media_type"] = "photo"
                result["image_path"] = await self._download_media(
                    message, channel_name, image_path, "jpg"
                )
                
            elif isinstance(message.media, MessageMediaDocument):
                # Check if it's a common image format
                document = message.media.document
                mime_type = getattr(document, 'mime_type', '')
                
                if mime_type.startswith('image/'):
                    result["media_type"] = "image"
                    ext = mime_type.split('/')[-1] or 'jpg'
                    result["image_path"] = await self._download_media(
                        message, channel_name, image_path, ext
                    )
                else:
                    result["media_type"] = "document"
        
        except Exception as e:
            self.scraper_logger.error(
                f"Failed to handle media for message {message.id}: {e}",
                extra={
                    "message_id": message.id,
                    "channel": channel_name,
                    "action": "media_handling"
                }
            )
        
        return result
    
    async def _download_media(
        self, 
        message: Message, 
        channel_name: str, 
        image_path: Path, 
        extension: str
    ) -> Optional[str]:
        """Download media file"""
        try:
            filename = f"{self._slugify_channel_name(channel_name)}_{message.id}.{extension}"
            filepath = image_path / filename
            
            await message.download_media(file=str(filepath))
            
            self.scraper_logger.debug(
                f"Downloaded media: {filename}",
                extra={
                    "message_id": message.id,
                    "channel": channel_name,
                    "file_size": filepath.stat().st_size if filepath.exists() else 0
                }
            )
            
            return str(filepath.relative_to(self.raw_data_path))
            
        except Exception as e:
            self.scraper_logger.error(
                f"Failed to download media for message {message.id}: {e}",
                extra={
                    "message_id": message.id,
                    "channel": channel_name,
                    "action": "media_download"
                }
            )
            return None
    
    def _extract_reactions(self, message: Message) -> Dict[str, int]:
        """Extract reaction counts from message"""
        reactions = {}
        
        if hasattr(message, 'reactions') and message.reactions:
            if hasattr(message.reactions, 'results'):
                for result in message.reactions.results:
                    if hasattr(result.reaction, 'emoticon'):
                        reactions[result.reaction.emoticon] = result.count
        
        return reactions
    
    def _extract_entities(self, message: Message) -> Dict[str, List[str]]:
        """Extract entities (hashtags, mentions, URLs) from message"""
        entities = {
            "hashtags": [],
            "mentions": [],
            "urls": []
        }
        
        if message.entities:
            for entity in message.entities:
                text = message.message[entity.offset:entity.offset + entity.length]
                
                if hasattr(entity, 'url'):
                    entities["urls"].append(entity.url)
                elif entity.__class__.__name__ == 'MessageEntityHashtag':
                    entities["hashtags"].append(text)
                elif entity.__class__.__name__ == 'MessageEntityMention':
                    entities["mentions"].append(text)
        
        return entities
    
    def _slugify_channel_name(self, channel_name: str) -> str:
        """Convert channel name to filesystem-safe slug"""
        return channel_name.replace('@', '').replace('-', '_').lower()
    
    async def _save_channel_messages(self, channel_name: str, messages: List[Dict[str, Any]]):
        """Save scraped messages to JSON file with date partitioning"""
        if not messages:
            self.scraper_logger.warning(
                f"No messages to save for {channel_name}",
                extra={"channel": channel_name, "action": "save_messages"}
            )
            return
        
        try:
            # Group messages by date
            messages_by_date = {}
            for msg in messages:
                if msg.get("message_date"):
                    try:
                        date_obj = datetime.fromisoformat(msg["message_date"].replace('Z', '+00:00'))
                        date_str = date_obj.strftime("%Y-%m-%d")
                        messages_by_date.setdefault(date_str, []).append(msg)
                    except (ValueError, AttributeError):
                        # Use current date if parsing fails
                        date_str = datetime.utcnow().strftime("%Y-%m-%d")
                        messages_by_date.setdefault(date_str, []).append(msg)
                else:
                    # Messages without date go to current date
                    date_str = datetime.utcnow().strftime("%Y-%m-%d")
                    messages_by_date.setdefault(date_str, []).append(msg)
            
            # Save each day's messages to separate file
            for date_str, day_messages in messages_by_date.items():
                date_path = self.messages_path / date_str
                date_path.mkdir(exist_ok=True)
                
                filename = f"{self._slugify_channel_name(channel_name)}.json"
                filepath = date_path / filename
                
                # Use async file writing
                await self._write_json_file(filepath, day_messages)
                
                self.scraper_logger.info(
                    f"Saved {len(day_messages)} messages for {channel_name} on {date_str}",
                    extra={
                        "channel": channel_name,
                        "date": date_str,
                        "message_count": len(day_messages),
                        "file_path": str(filepath),
                        "action": "save_messages"
                    }
                )
        
        except Exception as e:
            log_error_with_context(
                e,
                {
                    "channel": channel_name,
                    "action": "save_messages",
                    "message_count": len(messages)
                }
            )
    
    async def _write_json_file(self, filepath: Path, data: List[Dict[str, Any]]):
        """Asynchronously write JSON file"""
        async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
            json_data = json.dumps(data, ensure_ascii=False, indent=2)
            await f.write(json_data)


async def main():
    """Main function to run scraper"""
    scraper = TelegramScraper(max_messages_per_channel=500)
    
    try:
        # Scrape all channels
        all_messages = await scraper.scrape_all_channels()
        
        # Log summary
        total_messages = sum(len(msgs) for msgs in all_messages.values())
        logger.info(
            f"Scraping completed. Total messages: {total_messages}",
            extra={
                "total_messages": total_messages,
                "channels_scraped": len(all_messages),
                "action": "scraping_complete"
            }
        )
        
        return all_messages
        
    except Exception as e:
        log_error_with_context(
            e,
            {
                "action": "main_scraping",
                "component": "TelegramScraper"
            }
        )
        raise


if __name__ == "__main__":
    # Run the scraper
    asyncio.run(main())
