#!/usr/bin/env python3
"""
Main Dagster pipeline for Medical Telegram Warehouse.
Orchestrates all tasks: Scraping → dbt → YOLO → API
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

import dagster as dg
from dagster import (
    Definitions,
    EnvVar,
    job,
    op,
    graph,
    repository,
    schedule,
    sensor,
    RunRequest,
    OpExecutionContext,
    RetryPolicy,
    Backoff,
    Jitter,
    multiprocess_executor,
    in_process_executor,
)
from dagster_dbt import dbt_cli_resource
import docker
import requests
import pandas as pd
from sqlalchemy import create_engine

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Create directory structure
Path("src/common").mkdir(parents=True, exist_ok=True)
Path("scripts").mkdir(exist_ok=True)
Path(".github/workflows").mkdir(parents=True, exist_ok=True)


# Telegram Resource
@dg.resource(
    config_schema={
        "api_id": dg.String,
        "api_hash": dg.String,
    }
)
def telegram_resource(context):
    """Resource for Telegram API."""
    class TelegramClient:
        def __init__(self, api_id, api_hash):
            self.api_id = api_id
            self.api_hash = api_hash
    return TelegramClient(
        context.resource_config["api_id"],
        context.resource_config["api_hash"]
    )


# Database Resource
@dg.resource(
    config_schema={
        "host": dg.String,
        "port": dg.String,
        "database": dg.String,
        "user": dg.String,
        "password": dg.String,
    }
)
def database_resource(context):
    """Resource for database connections."""
    config = context.resource_config
    engine = create_engine(
        f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
    )
    return {"engine": engine}


# Docker Resource
@dg.resource
def docker_resource(context):
    """Resource for Docker client."""
    return docker.from_env()


# Operation 1: Telegram Scraping
@op(
    config_schema={
        "channels": dg.Array(dg.String),
        "days_back": dg.Int,
        "limit": dg.Int,
    },
    required_resource_keys={"telegram", "database"},
    retry_policy=RetryPolicy(
        max_retries=3,
        delay=5,
        backoff=Backoff.EXPONENTIAL,
    ),
    tags={"task": "scraping", "component": "telegram"},
)
def scrape_telegram_data(context: OpExecutionContext) -> Dict[str, Any]:
    """Scrape data from Telegram channels."""
    config = context.op_config
    
    try:
        context.log.info(f"Starting Telegram scraping for {config['channels']}")
        
        # Simulate scraping (replace with actual Telethon code)
        mock_data = {
            "status": "success",
            "message_count": 150,
            "channels": config["channels"],
            "files": ["data/raw/messages.json"],
        }
        
        # Save to database
        engine = context.resources.database["engine"]
        with engine.connect() as conn:
            # Your database logic here
            pass
        
        context.log.info(f"Scraped {mock_data['message_count']} messages")
        return mock_data
        
    except Exception as e:
        context.log.error(f"Scraping failed: {str(e)}")
        raise


# Operation 2: dBT Transformations
@op(
    config_schema={
        "project_dir": dg.String,
        "target": dg.String,
    },
    required_resource_keys={"database"},
    tags={"task": "transformation", "component": "dbt"},
)
def run_dbt_transformations(context: OpExecutionContext, scraped_data: Dict) -> Dict[str, Any]:
    """Run dbt transformations."""
    config = context.op_config
    
    try:
        context.log.info(f"Running dbt in {config['project_dir']}")
        
        # Simulate dbt run
        import subprocess
        result = subprocess.run(
            ["dbt", "run", "--project-dir", config["project_dir"], "--target", config["target"]],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            context.log.info("dbt transformations completed")
            return {
                "status": "success",
                "models_processed": 5,
                "output": result.stdout[-500:],
            }
        else:
            raise Exception(f"dbt failed: {result.stderr}")
            
    except Exception as e:
        context.log.error(f"dbt failed: {str(e)}")
        raise


# Operation 3: YOLO Detection
@op(
    config_schema={
        "model_path": dg.String,
        "image_dir": dg.String,
        "confidence": dg.Float,
    },
    required_resource_keys={"database"},
    retry_policy=RetryPolicy(max_retries=2, delay=30),
    tags={"task": "enrichment", "component": "yolo"},
)
def run_yolo_detection(context: OpExecutionContext, scraped_data: Dict) -> Dict[str, Any]:
    """Run YOLO object detection."""
    config = context.op_config
    
    try:
        context.log.info(f"Starting YOLO detection with {config['model_path']}")
        
        # Simulate YOLO processing
        mock_detections = [
            {"image": "img1.jpg", "class": "medical", "confidence": 0.85},
            {"image": "img2.jpg", "class": "cosmetic", "confidence": 0.92},
            {"image": "img3.jpg", "class": "packaging", "confidence": 0.78},
        ]
        
        # Save to database
        engine = context.resources.database["engine"]
        df = pd.DataFrame(mock_detections)
        df.to_sql("detections", engine, if_exists="append", index=False)
        
        # Save to file
        output_dir = Path("data/processed/detections")
        output_dir.mkdir(parents=True, exist_ok=True)
        df.to_parquet(output_dir / "detections.parquet")
        
        context.log.info(f"Found {len(mock_detections)} detections")
        return {
            "status": "success",
            "detections_count": len(mock_detections),
            "output_file": str(output_dir / "detections.parquet"),
        }
        
    except Exception as e:
        context.log.error(f"YOLO failed: {str(e)}")
        raise


# Operation 4: Start API Service
@op(
    config_schema={
        "port": dg.Int,
        "host": dg.String,
    },
    required_resource_keys={"docker"},
    tags={"task": "serving", "component": "api"},
)
def start_fastapi_service(context: OpExecutionContext, dbt_results: Dict, yolo_results: Dict) -> Dict[str, Any]:
    """Start FastAPI service."""
    config = context.op_config
    
    try:
        context.log.info("Starting FastAPI service")
        
        docker_client = context.resources.docker
        
        # Check if container exists
        containers = docker_client.containers.list(all=True, filters={"name": "medical-api"})
        for container in containers:
            container.stop()
            container.remove()
        
        # Run container
        container = docker_client.containers.run(
            image="medical-telegram-api:latest",
            name="medical-api",
            ports={f"{config['port']}/tcp": config["port"]},
            environment={
                "DATABASE_URL": os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/db"),
            },
            detach=True,
            remove=True,
        )
        
        # Wait for health check
        import time
        for _ in range(30):
            try:
                response = requests.get(f"http://{config['host']}:{config['port']}/health", timeout=2)
                if response.status_code == 200:
                    context.log.info("API is healthy")
                    break
            except:
                time.sleep(2)
        
        return {
            "status": "success",
            "container_id": container.id,
            "api_url": f"http://{config['host']}:{config['port']}",
            "docs_url": f"http://{config['host']}:{config['port']}/docs",
        }
        
    except Exception as e:
        context.log.error(f"API startup failed: {str(e)}")
        raise


# Operation 5: Validate API
@op(
    config_schema={
        "endpoints": dg.Array(dg.String),
    },
    tags={"task": "validation", "component": "api"},
)
def validate_api_service(context: OpExecutionContext, api_info: Dict) -> Dict[str, Any]:
    """Validate API endpoints."""
    config = context.op_config
    
    results = {}
    for endpoint in config["endpoints"]:
        url = f"{api_info['api_url']}{endpoint}"
        try:
            response = requests.get(url, timeout=10)
            results[endpoint] = {
                "status": response.status_code,
                "success": 200 <= response.status_code < 300,
            }
        except Exception as e:
            results[endpoint] = {"error": str(e), "success": False}
    
    success_rate = sum(1 for r in results.values() if r.get("success")) / len(results) * 100
    
    return {
        "status": "success" if success_rate > 80 else "warning",
        "success_rate": success_rate,
        "results": results,
    }


# Operation 6: Generate Report
@op(
    tags={"task": "reporting"},
)
def generate_pipeline_report(
    context: OpExecutionContext,
    scrape_result: Dict,
    dbt_result: Dict,
    yolo_result: Dict,
    api_result: Dict,
    validation_result: Dict,
) -> Dict[str, Any]:
    """Generate pipeline report."""
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "pipeline_id": context.run_id,
        "components": {
            "scraping": {
                "status": scrape_result.get("status"),
                "messages": scrape_result.get("message_count", 0),
            },
            "dbt": {
                "status": dbt_result.get("status"),
                "models": dbt_result.get("models_processed", 0),
            },
            "yolo": {
                "status": yolo_result.get("status"),
                "detections": yolo_result.get("detections_count", 0),
            },
            "api": {
                "status": api_result.get("status"),
                "url": api_result.get("api_url"),
            },
            "validation": {
                "status": validation_result.get("status"),
                "success_rate": validation_result.get("success_rate", 0),
            },
        },
        "overall_status": "success" if all([
            scrape_result.get("status") == "success",
            dbt_result.get("status") == "success",
            yolo_result.get("status") == "success",
            api_result.get("status") == "success",
            validation_result.get("status") in ["success", "warning"],
        ]) else "failed",
    }
    
    # Save report
    import json
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    report_file = report_dir / f"pipeline_{context.run_id}.json"
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)
    
    context.log.info(f"Report saved to {report_file}")
    return report


# Pipeline Graph
@graph
def medical_telegram_pipeline():
    """Complete pipeline graph."""
    # Execute tasks in order
    scrape_result = scrape_telegram_data()
    dbt_result = run_dbt_transformations(scrape_result)
    yolo_result = run_yolo_detection(scrape_result)
    api_result = start_fastapi_service(dbt_result, yolo_result)
    validation_result = validate_api_service(api_result)
    report = generate_pipeline_report(
        scrape_result,
        dbt_result,
        yolo_result,
        api_result,
        validation_result,
    )
    return report


# Production Job
@job(
    resource_defs={
        "telegram": telegram_resource.configured({
            "api_id": {"env": "TELEGRAM_API_ID"},
            "api_hash": {"env": "TELEGRAM_API_HASH"},
        }),
        "database": database_resource.configured({
            "host": {"env": "DB_HOST"},
            "port": {"env": "DB_PORT"},
            "database": {"env": "DB_NAME"},
            "user": {"env": "DB_USER"},
            "password": {"env": "DB_PASSWORD"},
        }),
        "docker": docker_resource,
    },
    config={
        "ops": {
            "scrape_telegram_data": {
                "config": {
                    "channels": ["@chemed123", "@lobelia4cosmetics", "@tikvahpharma"],
                    "days_back": 7,
                    "limit": 100,
                }
            },
            "run_dbt_transformations": {
                "config": {
                    "project_dir": "medical_warehouse",
                    "target": "prod",
                }
            },
            "run_yolo_detection": {
                "config": {
                    "model_path": "yolov8n.pt",
                    "image_dir": "data/raw/images",
                    "confidence": 0.5,
                }
            },
            "start_fastapi_service": {
                "config": {
                    "port": 8000,
                    "host": "0.0.0.0",
                }
            },
            "validate_api_service": {
                "config": {
                    "endpoints": [
                        "/api/v1/channels",
                        "/api/v1/detections",
                        "/api/v1/messages",
                        "/api/v1/search",
                        "/health",
                    ]
                }
            }
        }
    },
    executor_def=multiprocess_executor.configured({"max_concurrent": 3}),
    tags={
        "pipeline": "medical-telegram",
        "environment": "production",
        "version": "1.0",
    },
)
def medical_telegram_etl_job():
    return medical_telegram_pipeline()


# Test Job
@job(
    resource_defs={
        "database": database_resource.configured({
            "host": "localhost",
            "port": "5432",
            "database": "test_db",
            "user": "test_user",
            "password": "test_pass",
        }),
    },
    config={
        "ops": {
            "scrape_telegram_data": {
                "config": {
                    "channels": ["@test_channel"],
                    "days_back": 1,
                    "limit": 10,
                }
            }
        }
    },
    executor_def=in_process_executor,
    tags={"environment": "testing"},
)
def test_pipeline_job():
    return scrape_telegram_data()


# Schedule
@schedule(
    cron_schedule="0 2 * * *",  # Daily at 2 AM
    job=medical_telegram_etl_job,
    execution_timezone="UTC",
)
def daily_pipeline_schedule():
    return {}


# Definitions
defs = Definitions(
    jobs=[medical_telegram_etl_job, test_pipeline_job],
    schedules=[daily_pipeline_schedule],
)
