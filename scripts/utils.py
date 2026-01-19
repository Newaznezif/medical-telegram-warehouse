#!/usr/bin/env python3
"""
Utility functions for the pipeline.
"""

import os
import sys
import json
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib
import subprocess
import psutil
import docker
from sqlalchemy import create_engine, text


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('pipeline.log'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_file = Path(config_path)
    
    if not config_file.exists():
        # Create default config
        default_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "medical_warehouse",
                "user": "postgres",
                "password": "postgres"
            },
            "telegram": {
                "channels": ["@chemed123", "@lobelia4cosmetics", "@tikvahpharma"],
                "session_name": "telegram_session",
                "api_id": "",
                "api_hash": ""
            },
            "yolo": {
                "model_path": "yolov8n.pt",
                "confidence_threshold": 0.5,
                "batch_size": 16
            },
            "api": {
                "host": "0.0.0.0",
                "port": 8000,
                "reload": False
            },
            "pipeline": {
                "max_retries": 3,
                "retry_delay": 5,
                "timeout": 3600
            }
        }
        
        with open(config_file, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        return default_config
    
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)


def get_database_connection(config: Dict[str, Any]) -> Any:
    """Create database connection."""
    db_config = config["database"]
    connection_string = (
        f"postgresql://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['name']}"
    )
    return create_engine(connection_string)


def calculate_md5(file_path: str) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def check_disk_space(path: str = ".", threshold_gb: float = 5.0) -> bool:
    """Check if there's enough disk space."""
    usage = psutil.disk_usage(path)
    free_gb = usage.free / (1024 ** 3)
    return free_gb >= threshold_gb


def run_command(cmd: List[str], timeout: int = 300) -> Dict[str, Any]:
    """Run shell command with timeout."""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=True
        )
        return {
            "success": True,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    except subprocess.CalledProcessError as e:
        return {
            "success": False,
            "error": f"Command failed with code {e.returncode}",
            "stderr": e.stderr,
            "stdout": e.stdout
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def backup_database(config: Dict[str, Any], backup_dir: str = "backups") -> str:
    """Create database backup."""
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_path / f"backup_{timestamp}.sql"
    
    db_config = config["database"]
    
    # Use pg_dump for backup
    cmd = [
        "pg_dump",
        "-h", db_config["host"],
        "-p", str(db_config["port"]),
        "-U", db_config["user"],
        "-d", db_config["name"],
        "-f", str(backup_file)
    ]
    
    # Set password environment variable
    env = os.environ.copy()
    env["PGPASSWORD"] = db_config["password"]
    
    result = subprocess.run(cmd, env=env, capture_output=True, text=True)
    
    if result.returncode == 0:
        return str(backup_file)
    else:
        raise Exception(f"Backup failed: {result.stderr}")


def monitor_system_metrics() -> Dict[str, Any]:
    """Collect system metrics."""
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_usage": psutil.disk_usage(".").percent,
        "network_io": psutil.net_io_counters()._asdict(),
        "running_processes": len(psutil.pids())
    }


def check_docker_service() -> bool:
    """Check if Docker service is running."""
    try:
        client = docker.from_env()
        client.ping()
        return True
    except:
        return False


def validate_file_structure() -> List[str]:
    """Validate required file structure."""
    required_dirs = [
        "data/raw/images",
        "data/processed/detections",
        "src/common",
        "api/routers",
        "medical_warehouse/models",
        "tests",
        "scripts"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    return missing_dirs


def send_alert(message: str, alert_type: str = "error") -> None:
    """Send alert notification."""
    # This can be extended to send emails, Slack messages, etc.
    logger = setup_logging()
    
    if alert_type == "error":
        logger.error(f"ALERT: {message}")
    elif alert_type == "warning":
        logger.warning(f"WARNING: {message}")
    else:
        logger.info(f"INFO: {message}")
    
    # Example: Send to file
    alert_file = Path("alerts.log")
    with open(alert_file, "a") as f:
        f.write(f"{datetime.now().isoformat()} - {alert_type.upper()}: {message}\n")


def cleanup_old_files(directory: str, days_old: int = 30) -> int:
    """Clean up files older than specified days."""
    cleanup_dir = Path(directory)
    cutoff_date = datetime.now() - timedelta(days=days_old)
    deleted_count = 0
    
    if not cleanup_dir.exists():
        return 0
    
    for file_path in cleanup_dir.rglob("*"):
        if file_path.is_file():
            file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            if file_mtime < cutoff_date:
                try:
                    file_path.unlink()
                    deleted_count += 1
                except Exception as e:
                    send_alert(f"Failed to delete {file_path}: {str(e)}", "warning")
    
    return deleted_count


if __name__ == "__main__":
    # Test utilities
    logger = setup_logging()
    logger.info("Utilities module loaded successfully")
    
    config = load_config()
    logger.info(f"Config loaded: {list(config.keys())}")
    
    metrics = monitor_system_metrics()
    logger.info(f"System metrics: CPU={metrics['cpu_percent']}%, Memory={metrics['memory_percent']}%")
