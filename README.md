# 🚀 AI-Powered Financial Fraud Detection & Analytics Platform

## 📌 Overview

AI-Powered Financial Fraud Detection & Analytics Platform is a complete enterprise-level fraud detection system developed using Machine Learning, Kafka Streaming, FastAPI, PostgreSQL, and Streamlit.

The platform detects fraud across multiple datasets, provides real-time monitoring, ensemble learning, analytics dashboards, fraud forecasting, and REST APIs.

---

# 🎯 Features

## Financial Fraud Detection

- Logistic Regression
- Random Forest
- XGBoost
- Ensemble Learning
- Fraud Probability
- Risk Score
- Alert Generation

---

## Credit Card Fraud Detection

- Real-time Prediction
- Fraud Alerts
- Risk Monitoring

---

## Synthetic Fraud Detection

- PaySim Dataset
- API Prediction
- Kafka Streaming
- Database Logging

---

## Dashboard

Professional Streamlit Dashboard including:

- Executive Dashboard
- Financial Fraud Analytics
- Credit Card Fraud Analytics
- Synthetic Fraud Analytics
- Fraud Alerts
- Risk Score Center
- Real-Time Kafka Monitor
- Database Analytics
- Model Performance
- API Monitoring
- User Activity Logs
- Ensemble Fraud Engine
- Fraud Forecasting
- Admin Settings
- User Settings

---

## Machine Learning Models

- Logistic Regression
- Random Forest
- XGBoost
- Ensemble Voting

---

## Real-Time Streaming

Apache Kafka

- Producer
- Consumer
- Live Monitoring
- Kafka Logs

---

## REST APIs

FastAPI

- Financial Fraud API
- Credit Card Fraud API
- Synthetic Fraud API

---

## Database

PostgreSQL

Tables include:

- users
- fraud_predictions
- credit_card_predictions
- synthetic_predictions
- kafka_logs
- api_logs
- alert_history
- model_metrics
- fraud_forecast
- ensemble_predictions
- user_activity_logs

---

# 🛠 Technologies Used

### Programming

- Python

### Machine Learning

- Scikit-learn
- XGBoost

### Dashboard

- Streamlit
- Plotly

### APIs

- FastAPI

### Database

- PostgreSQL

### Streaming

- Apache Kafka

### Data Processing

- Pandas
- NumPy

---

# 📂 Project Structure

```
Financial-Fraud-Detection/

│

├── dashboard/

├── financial_fraud/

├── credit_card_fraud/

├── synthetic_fraud/

├── requirements.txt

├── README.md
```

---

# ⚙ Installation

Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/Financial-Fraud-Detection.git
```

Move inside

```bash
cd Financial-Fraud-Detection
```

Install dependencies

```bash
pip install -r requirements.txt
```

---

# Database

Create PostgreSQL database

```
fraud_db
```

Update database credentials in

```
dashboard/utils/db.py

financial_fraud/database/db_config.py
```

---

# Kafka

Start Kafka

Create Topics

```
fraud_transactions

credit_card_topic

synthetic_fraud_topic
```

---

# Run FastAPI

Financial

```bash
uvicorn financial_fraud.api.app:app --reload
```

Credit Card

```bash
uvicorn credit_card_fraud.api.app:app --reload
```

Synthetic

```bash
uvicorn synthetic_fraud.api.app:app --reload
```

---

# Run Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

---

# Screenshots

Add screenshots here

Executive Dashboard

Login Page

Risk Score Center

Kafka Monitor

Fraud Forecast

Ensemble Dashboard

---

# Future Enhancements

- AI Fraud Assistant
- Voice Assistant
- Docker Deployment
- Cloud Deployment
- SHAP Explainability
- PDF Reports
- Role-Based Access Control

---

# Author

Veera Bhadra

B.Tech Computer Science

Machine Learning | Data Science | AI

---

# License

This project is developed for educational and internship purposes.