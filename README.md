<<<<<<< HEAD

=======
>>>>>>> main
# Medical Telegram Data Warehouse – Interim Submission

**Ethiopian Medical & Cosmetics Intelligence Platform**

![Python application](https://github.com/Newaznezif/medical-telegram-warehouse/actions/workflows/python-app.yml/badge.svg)

---

## 📌 Project Overview
The goal of this project is to build an end-to-end data product that transforms raw Telegram data into actionable analytical insights. We focus on public Ethiopian medical and cosmetic channels to provide intelligence on product trends, engagement metrics, and potential anomalies.

<<<<<<< HEAD
### 🎯 Business Problem
The medical and cosmetic market in Ethiopia is rapidly growing, with a significant amount of commerce happening on Telegram. However, this data is unstructured and difficult to analyze manually. This project provides a structured data warehouse and analytical engine to:
- Track product popularity and engagement.
- Identify trends in medical and cosmetic discussions.
- Detect anomalies and outliers in channel activity.
=======
This platform covers the **full data lifecycle**:
- Raw data ingestion from Telegram
- Exploratory analysis
- Data warehousing with dbt (Star Schema)
- Computer vision enrichment (YOLOv8 - In Progress)
- Analytical API exposure (FastAPI)
- Pipeline orchestration and production deployment
>>>>>>> main

---

## ✅ Interim Accomplishments
<<<<<<< HEAD
1.  **Refactored Codebase**: Moved core logic into a modular `src/` folder for better maintainability and scalability.
2.  **Modular ETL Pipeline**: Implemented `etl.py` to handle data ingestion, cleaning, and database loading.
3.  **KPI & Analytics Engine**: Created `analytics.py` for automated KPI calculations and risk/anomaly scoring.
4.  **Unit Testing Suite**: Integrated `pytest` with 5+ comprehensive tests covering core functionality.
5.  **CI/CD Integration**: Set up a GitHub Actions workflow to automate testing and linting on every push.
6.  **Data Warehouse Structure**: Star-schema design using dbt for staging, dimension, and fact modeling.

---

## 🚀 Getting Started
=======
1.  **Refactored Codebase**: Modularized the project into a clean `src/` directory for better maintainability.
2.  **Modular ETL Pipeline**: Implemented `etl.py` for automated data ingestion, cleaning, and DB loading.
3.  **KPI & Analytics Engine**: Created `analytics.py` for KPI calculations and anomaly scoring.
4.  **Unit Testing Suite**: Integrated `pytest` with 5+ comprehensive tests (Passing: 100%).
5.  **CI/CD Integration**: Established GitHub Actions for automated linting and testing.

---

## 🚀 Technical Evidence

### 🧪 Unit Test Snippets
Standardized testing for core logic enables reliable updates.
```python
def test_clean_data_removes_duplicates():
    df = clean_data(MOCK_RAW_DATA)
    assert len(df) == 2
    assert df["message_id"].is_unique

def test_calculate_kpis_produces_correct_values():
    df = clean_data(MOCK_RAW_DATA)
    kpis = calculate_kpis(df)
    assert kpis["total_messages"] == 2
```

### 📋 Verified Execution Logs
#### Unit Tests (`pytest`)
```text
tests\test_core.py .....                                                 [100%]
============================== 5 passed in 0.53s ==============================
```

#### Pipeline (`python -m src.main`)
```text
2026-02-14 19:57:00,168 - INFO - Ingested 1071 messages.
2026-02-14 19:57:00,181 - INFO - Cleaned data: 1071 records remaining.
2026-02-14 19:57:01,000 - INFO - Pipeline execution completed successfully.
```

---

## 🚧 Challenges & Blockers
While core goals were met, some advanced features were deferred due to technical challenges:

1. **YOLO Image Enrichment**: 
   - *Blocker*: Required specific pre-trained weights (`yolov8n.pt`) and local C++ build environment setup that faced compatibility issues during the initial sprint.
   - *Status*: Foundation in place, integration planned for next phase.
2. **AI Interpretability (SHAP/LIME)**:
   - *Blocker*: Depends on a fully trained predictive model. Current scoring is rule-based; SHAP/LIME will be added once the ML models are fully integrated.
3. **Streamlit Dashboard**:
   - *Blocker*: Priority was shifted to ensure 100% data integrity in the database before building the UI layer.

---

## ⚙️ Setup Instructions
>>>>>>> main

### 1️⃣ Installation
```bash
git clone https://github.com/Newaznezif/medical-telegram-warehouse.git
cd medical-telegram-warehouse
pip install -r requirements.txt
```

### 2️⃣ Run the Pipeline
<<<<<<< HEAD
Run the complete ETL and analytics pipeline from the command line:
=======
>>>>>>> main
```bash
python src/main.py
```

### 3️⃣ Run Unit Tests
<<<<<<< HEAD
Verify the code quality and logic:
=======
>>>>>>> main
```bash
pytest tests/test_core.py
```

---

## 🗂️ Project Structure
- `src/`: Core logic folder
    - `config.py`: Centralized constants and configuration.
    - `etl.py`: Data ingestion, cleaning, and database loading.
<<<<<<< HEAD
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
=======
    - `analytics.py`: KPI calculations and anomaly detection.
    - `main.py`: Entry point.
- `tests/`: Unit tests suite.
- `.github/workflows/`: CI/CD configuration.
- `medical_warehouse/`: dbt project.
>>>>>>> main

---

## 🏁 Final Notes
<<<<<<< HEAD
This submission prepares the foundation for a robust, production-ready data product. The focus on code quality, testing, and modularity ensures the project is ready for the final enhancement phase.
=======
This submission establishes a robust, testable, and production-ready foundation. The focus on code quality and testing ensures a reliable platform for final feature enhancements. 🚀
>>>>>>> main
