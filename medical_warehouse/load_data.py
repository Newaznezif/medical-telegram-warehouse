import json
import psycopg2
import os
import glob
from datetime import datetime

def load_telegram_data():
    """Load Telegram data with correct field names"""
    
    print("📥 Loading Telegram data into PostgreSQL...")
    
    # Connect to PostgreSQL
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="medical_warehouse",
        user="admin",
        password="admin123"
    )
    conn.autocommit = True  # Auto-commit each statement
    cursor = conn.cursor()
    
    # Base directory
    base_dir = os.path.join('..', 'data', 'raw', 'telegram_messages')
    
    # Get all JSON files
    json_pattern = os.path.join(base_dir, '**', '*.json')
    json_files = glob.glob(json_pattern, recursive=True)
    
    print(f"📂 Found {len(json_files)} JSON files")
    
    total_loaded = 0
    
    for json_file in json_files:
        try:
            # Extract channel name and date from path
            rel_path = os.path.relpath(json_file, base_dir)
            path_parts = rel_path.split(os.sep)
            
            if len(path_parts) >= 2:
                date_str = path_parts[0]
                filename = path_parts[1]
                file_channel_name = filename.replace('.json', '')
            else:
                date_str = 'unknown'
                file_channel_name = os.path.basename(json_file).replace('.json', '')
            
            print(f"   Processing: {file_channel_name} - {date_str}")
            
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                print(f"   Skipping: Not a list")
                continue
            
            print(f"   Found {len(data)} messages")
            
            # Process each message
            loaded_count = 0
            for msg in data:
                if not isinstance(msg, dict):
                    continue
                
                # Extract data with actual field names from your JSON
                message_id = msg.get('message_id')
                channel_name = msg.get('channel_name') or file_channel_name
                message_date = msg.get('message_date')
                message_text = msg.get('message_text', '')
                views = msg.get('views', 0)
                forwards = msg.get('forwards', 0)
                
                # Media fields
                has_media = msg.get('has_media', False)
                image_path = msg.get('image_path')
                media_type = msg.get('media_type')
                
                # Content analysis fields
                message_length = msg.get('message_length', 0)
                has_links = msg.get('has_links', False)
                has_hashtags = msg.get('has_hashtags', False)
                has_mentions = msg.get('has_mentions', False)
                
                # Lists
                hashtags = msg.get('hashtags', [])
                mentions = msg.get('mentions', [])
                urls = msg.get('urls', [])
                reactions = msg.get('reactions', {})
                
                scraped_at = msg.get('scraped_at')
                
                # Skip if missing essential data
                if not message_id or not message_date:
                    continue
                
                # Insert into database
                cursor.execute("""
                    INSERT INTO raw_telegram.telegram_messages 
                    (channel_name, message_id, message_text, message_date, 
                     views, forwards, media_path, hashtags, raw_json)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (channel_name, message_id) DO NOTHING
                """, [
                    channel_name,
                    message_id,
                    message_text,
                    message_date,
                    views,
                    forwards,
                    image_path,  # Using image_path as media_path
                    json.dumps(hashtags),
                    json.dumps(msg)
                ])
                
                loaded_count += 1
            
            total_loaded += loaded_count
            print(f"   ✓ Loaded {loaded_count} messages")
            
        except Exception as e:
            print(f"   ✗ Error loading {json_file}: {str(e)}")
    
    cursor.close()
    conn.close()
    
    print(f"\n✅ Loading complete!")
    print(f"   Total messages loaded: {total_loaded}")
    
    # Verify the data was loaded
    verify_data()

def verify_data():
    """Verify data was loaded correctly"""
    print("\n🔍 Verifying data...")
    
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="medical_warehouse",
        user="admin",
        password="admin123"
    )
    cursor = conn.cursor()
    
    # Count total messages
    cursor.execute("SELECT COUNT(*) FROM raw_telegram.telegram_messages")
    total = cursor.fetchone()[0]
    print(f"   Total messages in database: {total}")
    
    if total > 0:
        # Count by channel
        cursor.execute("""
            SELECT channel_name, COUNT(*) as message_count 
            FROM raw_telegram.telegram_messages 
            GROUP BY channel_name 
            ORDER BY message_count DESC
        """)
        
        print("\n   Messages by channel:")
        for row in cursor.fetchall():
            print(f"     {row[0]}: {row[1]} messages")
        
        # Show data types
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'raw_telegram' 
            AND table_name = 'telegram_messages'
            ORDER BY ordinal_position
        """)
        
        print("\n   Table schema:")
        for row in cursor.fetchall():
            print(f"     {row[0]}: {row[1]}")
        
        # Show sample data
        cursor.execute("""
            SELECT channel_name, message_id, 
                   LEFT(message_text, 50) as preview, 
                   message_date,
                   views,
                   forwards
            FROM raw_telegram.telegram_messages 
            ORDER BY message_date DESC 
            LIMIT 5
        """)
        
        print("\n   Sample messages (most recent):")
        for row in cursor.fetchall():
            print(f"     [{row[0]}] ID:{row[1]} - '{row[2]}...' - {row[3]} (👁️{row[4]} 🔄{row[5]})")
    else:
        print("\n   No messages found in database")
    
    cursor.close()
    conn.close()

if __name__ == "__main__":
    load_telegram_data()