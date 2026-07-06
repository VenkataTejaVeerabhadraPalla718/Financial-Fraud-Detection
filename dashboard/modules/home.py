import streamlit as st
import pandas as pd
from datetime import datetime

from utils.db import (
    get_counts,
    load_alerts,
    load_api_logs,
    load_kafka_logs
)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def go_to_page(page_name):
    st.session_state.page = page_name
    st.rerun()


def safe_count(loader_function):
    try:
        df = loader_function()

        if df is None:
            return 0

        return len(df)

    except Exception:
        return 0


def render_module_card(
    icon,
    title,
    description,
    page_name,
    button_key
):
    st.markdown(
        f"""
        <div class="module-card">
            <div class="module-icon">{icon}</div>
            <div class="module-title">{title}</div>
            <div class="module-description">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    if st.button(
        f"Open {title}",
        key=button_key,
        use_container_width=True
    ):
        go_to_page(page_name)


# ==========================================================
# HOME PAGE
# ==========================================================

def show_home():

    # ------------------------------------------------------
    # CSS FOR HOME PAGE
    # ------------------------------------------------------

    st.markdown(
        """
        <style>

        .home-hero {
            padding: 35px;
            border-radius: 22px;
            margin-bottom: 25px;
            background: linear-gradient(
                135deg,
                rgba(0, 51, 102, 0.95),
                rgba(0, 89, 179, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.25);
        }

        .hero-title {
            font-size: 38px;
            font-weight: 800;
            margin-bottom: 8px;
        }

        .hero-subtitle {
            font-size: 18px;
            opacity: 0.9;
        }

        .status-pill {
            display: inline-block;
            margin-top: 15px;
            padding: 7px 14px;
            border-radius: 30px;
            background: rgba(255, 255, 255, 0.18);
            font-size: 14px;
            font-weight: 600;
        }

        .section-title {
            font-size: 25px;
            font-weight: 700;
            margin-top: 25px;
            margin-bottom: 15px;
        }

        .kpi-card {
            padding: 20px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 18px rgba(0, 0, 0, 0.14);
            text-align: center;
            min-height: 130px;
        }

        .kpi-icon {
            font-size: 28px;
        }

        .kpi-number {
            font-size: 30px;
            font-weight: 800;
            margin-top: 8px;
        }

        .kpi-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .module-card {
            min-height: 190px;
            padding: 22px;
            margin-top: 10px;
            margin-bottom: 8px;
            border-radius: 18px;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 18px rgba(0, 0, 0, 0.12);
            transition: 0.25s ease-in-out;
        }

        .module-card:hover {
            transform: translateY(-5px);
            border: 1px solid rgba(0, 140, 255, 0.9);
            box-shadow: 0 10px 28px rgba(0, 89, 179, 0.30);
        }

        .module-icon {
            font-size: 42px;
            margin-bottom: 12px;
        }

        .module-title {
            font-size: 20px;
            font-weight: 750;
            margin-bottom: 8px;
        }

        .module-description {
            font-size: 14px;
            opacity: 0.78;
            min-height: 42px;
        }

        .footer-text {
            text-align: center;
            opacity: 0.65;
            padding: 25px 0 10px 0;
            font-size: 13px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # GET DATA SAFELY
    # ------------------------------------------------------

    try:
        financial_count, credit_count, synthetic_count = get_counts()

    except Exception:
        financial_count = 0
        credit_count = 0
        synthetic_count = 0

    alert_count = safe_count(load_alerts)
    api_log_count = safe_count(load_api_logs)
    kafka_log_count = safe_count(load_kafka_logs)

    username = st.session_state.get(
        "username",
        "User"
    )

    current_date = datetime.now().strftime(
        "%d %B %Y"
    )

    # ------------------------------------------------------
    # HERO SECTION
    # ------------------------------------------------------

    st.markdown(
        f"""
        <div class="home-hero">
            <div class="hero-title">
                🛡️ AI-Powered Financial Fraud Detection Platform
            </div>

            <div class="hero-subtitle">
                Welcome back, {username} 👋 <br>
                Monitor fraud, investigate transactions, and manage risk from one place.
            </div>

            <div class="status-pill">
                🟢 System Online &nbsp; | &nbsp; {current_date}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # QUICK STATISTICS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-title">📊 Quick Statistics</div>',
        unsafe_allow_html=True
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">💰</div>
                <div class="kpi-number">{financial_count}</div>
                <div class="kpi-label">Financial Records</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">💳</div>
                <div class="kpi-number">{credit_count}</div>
                <div class="kpi-label">Credit Card Records</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">🏦</div>
                <div class="kpi-number">{synthetic_count}</div>
                <div class="kpi-label">Synthetic Records</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k4:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">🚨</div>
                <div class="kpi-number">{alert_count}</div>
                <div class="kpi-label">Fraud Alerts</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k5:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">🔌</div>
                <div class="kpi-number">{api_log_count}</div>
                <div class="kpi-label">API Requests</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with k6:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon">📡</div>
                <div class="kpi-number">{kafka_log_count}</div>
                <div class="kpi-label">Kafka Messages</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------
    # MODULE GRID
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-title">🧭 Choose a Module</div>',
        unsafe_allow_html=True
    )

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        render_module_card(
            "💰",
            "Financial Fraud",
            "Analyze financial fraud predictions and transaction risk.",
            "Financial Fraud",
            "home_financial"
        )

    with row1_col2:
        render_module_card(
            "💳",
            "Credit Card Fraud",
            "Review credit card fraud predictions and alerts.",
            "Credit Card Fraud",
            "home_credit"
        )

    with row1_col3:
        render_module_card(
            "🏦",
            "Synthetic Fraud",
            "Monitor PaySim synthetic transaction predictions.",
            "Synthetic Fraud",
            "home_synthetic"
        )

    row2_col1, row2_col2, row2_col3 = st.columns(3)

    with row2_col1:
        render_module_card(
            "📊",
            "Executive Dashboard",
            "View business KPIs, trends, and fraud overview.",
            "Executive Dashboard",
            "home_executive"
        )

    with row2_col2:
        render_module_card(
            "📡",
            "Real-Time Monitor",
            "Track Kafka activity and streaming messages.",
            "Real Time Monitor",
            "home_realtime"
        )

    with row2_col3:
        render_module_card(
            "🚨",
            "Fraud Alerts",
            "Review high-risk alerts and investigation history.",
            "Fraud Alerts",
            "home_alerts"
        )

    row3_col1, row3_col2, row3_col3 = st.columns(3)

    with row3_col1:
        render_module_card(
            "⚠️",
            "Risk Score Center",
            "Inspect current fraud risk scores and recommendations.",
            "Risk Score Center",
            "home_risk"
        )

    with row3_col2:
        render_module_card(
            "🔍",
            "Transaction Explorer",
            "Search, filter, and inspect transaction records.",
            "Transaction Explorer",
            "home_explorer"
        )

    with row3_col3:
        render_module_card(
            "🗄️",
            "Database Analytics",
            "Review database record counts and stored data.",
            "Database Analytics",
            "home_database"
        )

    row4_col1, row4_col2, row4_col3 = st.columns(3)

    with row4_col1:
        render_module_card(
            "📈",
            "Model Performance",
            "View model metrics including accuracy and F1 score.",
            "Model Performance",
            "home_models"
        )

    with row4_col2:
        render_module_card(
            "🔌",
            "API Monitoring",
            "Review API request logs and response performance.",
            "API Monitoring",
            "home_api"
        )

    with row4_col3:
        render_module_card(
            "🔬",
            "Ensemble Engine",
            "Compare Logistic Regression, Random Forest, and XGBoost.",
            "🔬 Ensemble Fraud Engine",
            "home_ensemble"
        )

    row5_col1, row5_col2, row5_col3 = st.columns(3)

    with row5_col1:
        render_module_card(
            "📉",
            "Fraud Forecasting",
            "Forecast future fraud activity and trends.",
            "📈 Fraud Forecasting",
            "home_forecasting"
        )

    with row5_col2:
        render_module_card(
            "🤖",
            "AI Assistant",
            "Get explanations and recommendations for predictions.",
            "🤖 AI Fraud Assistant",
            "home_ai"
        )

    with row5_col3:
        render_module_card(
            "👤",
            "User Activity",
            "Review user login activity and platform usage.",
            "User Activity",
            "home_activity"
        )

    row6_col1, row6_col2, row6_col3 = st.columns(3)

    with row6_col1:
        render_module_card(
            "⚙️",
            "Admin Settings",
            "Manage administrative controls and user access.",
            "Admin Settings",
            "home_admin"
        )

    with row6_col2:
        render_module_card(
            "🛠️",
            "User Settings",
            "Manage your profile, theme, and preferences.",
            "User Settings",
            "home_settings"
        )

    with row6_col3:
        render_module_card(
            "🏠",
            "Home Dashboard",
            "Refresh the main platform overview.",
            "Home",
            "home_home"
        )

    # ------------------------------------------------------
    # RECENT ACTIVITY
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-title">🕒 Recent Platform Activity</div>',
        unsafe_allow_html=True
    )

    activity_data = pd.DataFrame(
        {
            "Activity": [
                "Financial fraud records available",
                "Credit card fraud records available",
                "Synthetic fraud records available",
                "Fraud alerts available",
                "Kafka logs available"
            ],
            "Count": [
                financial_count,
                credit_count,
                synthetic_count,
                alert_count,
                kafka_log_count
            ]
        }
    )

    st.dataframe(
        activity_data,
        use_container_width=True,
        hide_index=True
    )

    st.markdown(
        """
        <div class="footer-text">
            AI-Powered Financial Fraud Detection & Analytics Platform
            <br>
            Built with Streamlit, FastAPI, PostgreSQL, Kafka, and Machine Learning
        </div>
        """,
        unsafe_allow_html=True
    )