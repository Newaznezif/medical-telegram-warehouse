

# Telegram Medical Data Warehouse – Task 1 & Task 2

**Ethiopian Medical & Cosmetics Intelligence Platform**

---

## 📌 Project Overview

This project collects, processes, models, and analyzes data from **public Ethiopian medical and cosmetic Telegram channels**.
It is built as an **end-to-end data engineering pipeline**, moving from raw data ingestion to a fully modeled PostgreSQL data warehouse ready for analytics and machine learning.

---

## 🎯 Objectives

### Task 1 – Data Scraping & Exploration

* Scrape messages and media from public Telegram channels
* Store raw data in structured JSON format
* Download and organize media (images)
* Perform Exploratory Data Analysis (EDA)
* Generate insights to guide data modeling

### Task 2 – Data Modeling & Warehousing

* Load raw Telegram data into PostgreSQL
* Build a **star-schema data warehouse** using dbt
* Create staging, dimension, and fact models
* Apply data quality tests
* Enable analytics-ready datasets

---

## 🗂️ Repository Structure

```
medical-telegram-warehouse/
├── data/
│   ├── raw/
│   │   ├── images/                      # Downloaded media by channel
│   │   └── telegram_messages/           # Raw JSON message files (by date)
│   ├── processed/                       # Cleaned/derived datasets
│   └── staging/                         # Intermediate files (optional)
│
├── medical_warehouse/                   # dbt project
│   ├── dbt_project.yml
│   ├── profiles.yml
│   ├── models/
│   │   ├── staging/
│   │   │   └── stg_telegram_messages.sql
│   │   └── marts/
│   │       ├── dim_channels.sql
│   │       ├── dim_dates.sql
│   │       └── fct_messages.sql
│   └── tests/
│       └── *.sql
│
├── notebooks/
│   └── exploration.ipynb                # Task 1 EDA
│
├── src/
│   ├── common/
│   │   └── config.py                    # Centralized config
│   └── scraper.py                      # Telegram scraping logic
│
├── scripts/
│   └── load_json_to_postgres.py         # Load raw JSON into PostgreSQL
│
├── logs/                                # Scraper and pipeline logs
├── tests/                               # Unit tests
├── docker-compose.yml                   # PostgreSQL container
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/yourusername/medical-telegram-warehouse.git
cd medical-telegram-warehouse
```

---

### 2️⃣ Create & Activate Virtual Environment

```bash
python -m venv venv
.\venv\Scripts\activate     # Windows
# or
source venv/bin/activate   # Linux/macOS
```

---

### 3️⃣ Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

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

RAW_DATA_PATH=./data/raw
PROCESSED_DATA_PATH=./data/processed
LOG_PATH=./logs
```

---

## 🚀 Task 1 – Data Scraping & Exploration

### 1️⃣ Run the Telegram Scraper

```bash
python -m src.scraper
```

**What this does:**

* Scrapes messages from configured Telegram channels
* Saves messages as JSON files by date
* Downloads images/media per channel
* Logs progress and errors to `logs/`

---

### 2️⃣ Exploratory Data Analysis (EDA)

```bash
jupyter notebook notebooks/exploration.ipynb
```

The notebook includes:

* Dataset overview and schema inspection
* Channel-level activity analysis
* Engagement metrics (views, forwards)
* Text length and content analysis
* Temporal trends (daily, hourly)
* Data quality checks
* Business insights to guide modeling

---

### ✅ Task 1 Summary

* Scraped **3 Ethiopian medical/cosmetics channels**
* Stored raw data in structured JSON format
* Downloaded associated images
* Generated EDA insights
* Prepared data for warehousing

---

## 🏗️ Task 2 – Data Modeling & Data Warehouse

### 1️⃣ Start PostgreSQL with Docker

```bash
docker-compose up -d
```

* PostgreSQL runs on **port 5432**
* Database: `medical_warehouse`

---

### 2️⃣ Load Raw JSON Data into PostgreSQL

```bash
python scripts/load_json_to_postgres.py
```

**Result:**

* `raw_telegram.telegram_messages` populated
* **1071 messages loaded**

---

### 3️⃣ Run dbt Models

```bash
cd medical_warehouse
dbt run
```

---

### 4️⃣ Validate Data Quality

```bash
dbt test
```

---

## 📊 Data Warehouse Architecture (Star Schema)

```
raw_telegram.telegram_messages        (1071 rows)
        ↓
dbt_staging.stg_telegram_messages    (cleaned view)
        ↓
dbt_marts.dim_channels               (3 channels)
dbt_marts.dim_dates                  (82 dates)
dbt_marts.fct_messages               (1071 messages)
```

---

## 🧪 Data Quality Tests

* No future-dated messages
* Positive engagement metrics
* Referential integrity between facts and dimensions

---

## ✅ Task 2 Summary

* PostgreSQL data warehouse deployed
* dbt project fully configured
* Staging, dimension, and fact models built
* 1071 Telegram messages modeled
* Star-schema ready for analytics and ML

---

## 🔜 Next Steps – Task 3 (YOLO Image Enrichment)

* Apply YOLOv8 to Telegram images
* Detect medical and cosmetic products
* Enrich warehouse with image intelligence
* Enable visual analytics & AI-driven insights

---

## 🏁 Final Notes

This project follows **industry-standard data engineering practices**:

* Raw → Staging → Marts
* Version-controlled dbt models
* Reproducible pipelines
* Analytics-ready schemas

You are now set up for **advanced analytics, dashboards, and AI enrichment** 🚀

---

