
# Medical Telegram Data Warehouse – Interim Submission

**Ethiopian Medical & Cosmetics Intelligence Platform**

![Python application](https://github.com/Newaznezif/medical-telegram-warehouse/actions/workflows/python-app.yml/badge.svg)

---

## 📌 Project Overview
The goal of this project is to build an end-to-end data product that transforms raw Telegram data into actionable analytical insights. We focus on public Ethiopian medical and cosmetic channels to provide intelligence on product trends, engagement metrics, and potential anomalies.

### 🎯 Business Problem
The medical and cosmetic market in Ethiopia is rapidly growing, with a significant amount of commerce happening on Telegram. However, this data is unstructured and difficult to analyze manually. This project provides a structured data warehouse and analytical engine to:
- Track product popularity and engagement.
- Identify trends in medical and cosmetic discussions.
- Detect anomalies and outliers in channel activity.

---

## ✅ Interim Accomplishments
1.  **Refactored Codebase**: Moved core logic into a modular `src/` folder for better maintainability and scalability.
2.  **Modular ETL Pipeline**: Implemented `etl.py` to handle data ingestion, cleaning, and database loading.
3.  **KPI & Analytics Engine**: Created `analytics.py` for automated KPI calculations and risk/anomaly scoring.
4.  **Unit Testing Suite**: Integrated `pytest` with 5+ comprehensive tests covering core functionality.
5.  **CI/CD Integration**: Set up a GitHub Actions workflow to automate testing and linting on every push.
6.  **Data Warehouse Structure**: Star-schema design using dbt for staging, dimension, and fact modeling.

---

## 🚀 Getting Started

### 1️⃣ Installation
```bash
git clone https://github.com/Newaznezif/medical-telegram-warehouse.git
cd medical-telegram-warehouse
pip install -r requirements.txt
```

### 2️⃣ Run the Pipeline
Run the complete ETL and analytics pipeline from the command line:
```bash
python src/main.py
```

### 3️⃣ Run Unit Tests
Verify the code quality and logic:
```bash
pytest tests/test_core.py
```

---

## 🗂️ Project Structure
- `src/`: Core logic folder
    - `config.py`: Centralized constants and configuration.
    - `etl.py`: Data ingestion, cleaning, and database loading.
    - `analytics.py`: KPI calculations and anomaly detection logic.
    - `main.py`: Main entry point for the pipeline.
    - `dashboard.py`: Placeholder for the Streamlit dashboard.
- `tests/`: Unit tests suite.
- `.github/workflows/`: CI/CD configuration.
- `medical_warehouse/`: dbt project for data warehousing.

---

## 🔜 Planned Improvements
1.  **Streamlit Dashboard**: Implement a fully interactive dashboard with real-time analytics.
2.  **YOLO Enrichment**: Integrate object detection to identify products within images.
3.  **AI Interpretability**: Add SHAP/LIME to explain anomaly detection scores.
4.  **Scaled Scraping**: Enhance the scraper to handle a wider set of channels and larger data volumes.
5.  **Automated Daily Reporting**: Schedule automated email/Telegram reports of daily KPIs.

---

## 🏁 Final Notes
This submission prepares the foundation for a robust, production-ready data product. The focus on code quality, testing, and modularity ensures the project is ready for the final enhancement phase.
