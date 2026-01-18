# Telegram Medical Data Warehouse – Task 1: Data Scraping & Exploration

## 📌 Project Overview

This project collects, processes, and analyzes raw Telegram data from Ethiopian medical and cosmetic channels. Task 1 focuses on **data scraping and initial exploratory data analysis (EDA)** to prepare for downstream data modeling and analytics.

### Objective

* Scrape messages and media from public Telegram channels.
* Store raw data in a structured format (JSON + images).
* Explore data to understand content, engagement, and posting patterns.
* Prepare insights for Task 2: building a PostgreSQL-based data warehouse.

---

## 🗂️ Repository Structure

```
medical-telegram-warehouse/
├── data/
│   ├── raw/
│   │   ├── images/                 # Downloaded media organized by channel
│   │   └── telegram_messages/      # JSON files of scraped messages
│   └── processed/                  # Cleaned or transformed datasets
├── notebooks/
│   └── exploration.ipynb           # EDA notebook for Task 1
├── src/
│   ├── common/
│   │   └── config.py               # Environment and project configuration
│   └── scraper.py                  # Telegram scraping script
├── logs/                            # Logging for scraper
├── scripts/                         # Utility scripts
├── tests/                           # Unit tests
├── requirements.txt                 # Python dependencies
└── README.md
```

---

## ⚙️ Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/medical-telegram-warehouse.git
cd medical-telegram-warehouse
```

2. **Create a virtual environment**

```bash
python -m venv venv
.\venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # Linux/macOS
```

3. **Install dependencies**

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Configure environment variables**
   Create a `.env` file at the project root:

```
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

## 🚀 Task 1 – Steps

### 1. Run the Scraper

```bash
python -m src.scraper
```

* Downloads **messages as JSON** and **media/images** per channel.
* Logs scraping progress in `logs/`.
* Supports multiple channels configured in `.env`.

### 2. Explore the Data

Open the Jupyter notebook:

```bash
jupyter notebook notebooks/exploration.ipynb
```

The notebook performs:

* Basic data overview (shape, columns, missing values)
* Channel activity analysis (messages per channel, top posters)
* Engagement metrics (views, forwards)
* Message content analysis (text length, most common words)
* Temporal analysis (hourly/day-of-week posting patterns)
* Hashtag and mention analysis
* Data quality checks (duplicates, future dates, negative engagement)
* Business insights & recommendations for Task 2

---

## 📊 Sample Outputs

* **JSON data:** `data/raw/telegram_messages/YYYY-MM-DD/*.json`
* **Images:** `data/raw/images/<channel_name>/`
* **EDA visuals:** plots of channel activity, engagement, temporal patterns, top words, and hashtags

---

## ✅ Summary of Task 1

* Scraped messages from 3 initial Telegram channels: `@chemed123`, `@lobelia4cosmetics`, `@tikvahpharma`
* Downloaded associated media content
* Validated and structured raw data for processing
* Generated EDA insights to inform **data modeling** in Task 2

---

## 🔜 Next Steps – Task 2

* Load cleaned JSON data into PostgreSQL
* Build **dimensional models** (channels, dates, time, hashtags)
* Design **fact tables** (messages, media, engagement)
* Enable analytical queries and dashboarding

---

> **Tip:** If the scraper only downloads images and no text, update the Telegram API or account permissions and rerun. The EDA notebook is designed to handle both text and media content.

