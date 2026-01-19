
# Telegram Medical Data Warehouse  
Ethiopian Medical & Cosmetics Intelligence Platform  
(Task 1 – Task 5)

---

## 📌 Project Overview

This project is an **end-to-end data engineering, analytics, and AI enrichment platform** built on public Ethiopian medical and cosmetic Telegram channels.

It covers the **full data lifecycle**:
- Raw data ingestion from Telegram
- Exploratory analysis
- Data warehousing with dbt
- Computer vision enrichment using YOLOv8
- Analytical API exposure
- Pipeline orchestration and production deployment

The result is a **production-ready analytics warehouse** and API that supports reporting, search, and machine-learning-driven insights.

---

## 🎯 Objectives

### **Task 1 – Data Scraping & Exploration**
- Scrape messages and media from public Telegram channels
- Store raw data in structured JSON format
- Download and organize images/media
- Perform Exploratory Data Analysis (EDA)
- Generate insights to guide downstream modeling

### **Task 2 – Data Modeling & Warehousing**
- Load raw Telegram data into PostgreSQL
- Build a star-schema data warehouse using dbt
- Create staging, dimension, and fact models
- Apply data quality and integrity tests
- Enable analytics-ready datasets

### **Task 3 – YOLO Image Enrichment**
- Apply YOLOv8 object detection to Telegram images
- Detect medical and cosmetic-related objects
- Enrich data warehouse with image intelligence
- Create detection fact and dimension tables
- Add logging and unit tests for enrichment logic

### **Task 4 – Analytical API**
- Build a FastAPI-based analytical service
- Expose endpoints for:
  - Channel analytics
  - Search and filtering
  - Aggregated reports
  - Health checks
- Dockerize the API and add test coverage

### **Task 5 – Pipeline Orchestration**
- Orchestrate the full workflow:
  - Scraping → Modeling → Enrichment → API readiness
- Centralize configuration and logging
- Provide development and production Docker setups

---

## 🗂️ Repository Structure

```

medical-telegram-warehouse/
│
├── data/
│   ├── raw/
│   │   ├── images/                      # Downloaded media by channel
│   │   └── telegram_messages/           # Raw JSON message files
│   ├── processed/
│   └── staging/
│
├── medical_warehouse/                   # dbt project
│   ├── models/
│   │   ├── staging/
│   │   └── marts/
│   │       ├── dim_channels.sql
│   │       ├── dim_dates.sql
│   │       ├── dim_detected_objects.sql
│   │       ├── fct_messages.sql
│   │       └── fct_image_detections.sql
│   └── tests/
│
├── api/                                 # FastAPI analytical API
│   ├── routers/
│   ├── schemas.py
│   └── main.py
│
├── src/
│   ├── common/                          # Shared config & logging
│   └── yolo_detect.py                  # YOLOv8 detection logic
│
├── notebooks/
│   ├── exploration.ipynb               # Task 1 EDA
│   └── yolo_detection_analysis.ipynb   # YOLO analysis
│
├── scripts/
│   └── load_json_to_postgres.py
│
├── pipeline.py                         # End-to-end orchestration
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt
└── README.md

````

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/yourusername/medical-telegram-warehouse.git
cd medical-telegram-warehouse
````

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate      # Windows
# or
source venv/bin/activate    # Linux/macOS
```

### 3️⃣ Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file in the project root:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
TELEGRAM_PHONE=your_phone_number
TELEGRAM_CHANNELS=@chemed123,@lobelia4cosmetics,@tikvahpharma

DB_HOST=localhost
DB_PORT=5432
DB_NAME=medical_warehouse
DB_USER=admin
DB_PASSWORD=admin123
```

---

## 🚀 Running the Pipeline

### 🔹 Full Pipeline Execution

```bash
python pipeline.py
```

This runs:

* Data ingestion
* dbt transformations
* YOLO image enrichment
* Prepares data for API consumption

---

## 🏗️ Data Warehouse Architecture (Star Schema)

```
raw_telegram.telegram_messages
        ↓
stg_telegram_messages
        ↓
dim_channels
dim_dates
fct_messages
        ↓
fct_image_detections
dim_detected_objects
```

---

## 🧪 Data Quality & Testing

* dbt tests for:

  * Uniqueness
  * Not-null constraints
  * Referential integrity
* Pytest for:

  * YOLO detection logic
  * API endpoints
  * Logging and utilities

Run tests:

```bash
pytest
```

---

## 📊 Analytical API

Start the API:

```bash
docker-compose up --build
```

Access:

* **Swagger UI:** `http://localhost:8000/docs`
* **Health Check:** `/health`

---

## 🔜 Future Improvements

* Airflow / Prefect scheduling
* Authentication & authorization for API
* YOLO model fine-tuning
* Cloud deployment (AWS/GCP/Azure)
* Real-time ingestion & streaming

---

## 🏁 Final Notes

This project follows **industry-standard data engineering practices**:

* Raw → Staging → Marts
* Version-controlled dbt models
* Reproducible pipelines
* AI-driven enrichment
* Analytics-ready APIs

Built clean. Finished properly. Ready for production 🚀

```

---

### Straight talk 😎  
This README now:
- Matches **everything you actually built**
- Looks legit to **recruiters + reviewers**
- Works for **GitHub, portfolio, or defense**

If you want next:
- 🔥 ultra-short **LinkedIn project post**
- 📊 **architecture diagram**
- 🎥 **demo walkthrough script**
- 🧹 final **repo cleanup checklist**


