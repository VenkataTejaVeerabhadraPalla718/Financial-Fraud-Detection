import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_counts,
    load_alerts,
    load_api_logs,
    load_kafka_logs,
    load_table
)

from utils.charts import (
    fraud_distribution_chart,
    fraud_bar_chart,
    prediction_chart,
    probability_histogram,
    timeline_chart
)


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def go_home():
    st.session_state.page = "Home"
    st.rerun()


def safe_load(loader_function):
    try:
        df = loader_function()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


def safe_table(table_name):
    try:
        df = load_table(table_name)

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


def get_prediction_summary(df):
    if df.empty or "prediction" not in df.columns:
        return 0, 0, 0

    total = len(df)

    fraud_count = len(
        df[df["prediction"] == 1]
    )

    legitimate_count = total - fraud_count

    return total, fraud_count, legitimate_count


def prepare_timeline(df):
    if df.empty:
        return pd.DataFrame()

    if "created_at" not in df.columns:
        return pd.DataFrame()

    try:
        df = df.copy()

        df["created_at"] = pd.to_datetime(
            df["created_at"],
            errors="coerce"
        )

        df = df.dropna(
            subset=["created_at"]
        )

        if df.empty:
            return pd.DataFrame()

        timeline = (
            df.groupby(
                df["created_at"].dt.date
            )
            .size()
            .reset_index(
                name="transactions"
            )
        )

        timeline.columns = [
            "date",
            "transactions"
        ]

        return timeline

    except Exception:
        return pd.DataFrame()


# ==========================================================
# EXECUTIVE DASHBOARD PAGE
# ==========================================================

def show_executive_dashboard():

    # ------------------------------------------------------
    # PAGE CSS
    # ------------------------------------------------------

    st.markdown(
        """
        <style>

        .executive-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(0, 51, 102, 0.96),
                rgba(0, 89, 179, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .executive-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .executive-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .summary-card {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 130px;
        }

        .summary-icon {
            font-size: 28px;
        }

        .summary-value {
            font-size: 29px;
            font-weight: 800;
            margin-top: 7px;
        }

        .summary-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .insight-box {
            padding: 18px;
            border-radius: 14px;
            margin-top: 10px;
            background: rgba(0, 89, 179, 0.12);
            border-left: 5px solid #0059B3;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # BACK BUTTON
    # ------------------------------------------------------

    top_left, top_right = st.columns(
        [1, 6]
    )

    with top_left:
        if st.button(
            "← Home",
            use_container_width=True
        ):
            go_home()

    # ------------------------------------------------------
    # LOAD DATABASE DATA
    # ------------------------------------------------------

    try:
        financial_count, credit_count, synthetic_count = get_counts()

    except Exception:
        financial_count = 0
        credit_count = 0
        synthetic_count = 0

    financial_df = safe_table(
        "fraud_predictions"
    )

    credit_df = safe_table(
        "credit_card_predictions"
    )

    synthetic_df = safe_table(
        "synthetic_predictions"
    )

    alerts_df = safe_load(
        load_alerts
    )

    api_logs_df = safe_load(
        load_api_logs
    )

    kafka_logs_df = safe_load(
        load_kafka_logs
    )

    # ------------------------------------------------------
    # COMBINE PREDICTION DATA
    # ------------------------------------------------------

    all_predictions = pd.concat(
        [
            financial_df,
            credit_df,
            synthetic_df
        ],
        ignore_index=True,
        sort=False
    )

    total_predictions, fraud_count, legitimate_count = (
        get_prediction_summary(
            all_predictions
        )
    )

    fraud_rate = 0.0

    if total_predictions > 0:
        fraud_rate = round(
            (fraud_count / total_predictions) * 100,
            2
        )

    average_probability = 0.0

    if (
        not all_predictions.empty
        and "fraud_probability" in all_predictions.columns
    ):
        try:
            average_probability = round(
                all_predictions[
                    "fraud_probability"
                ].astype(float).mean() * 100,
                2
            )

        except Exception:
            average_probability = 0.0

    # ------------------------------------------------------
    # HEADER
    # ------------------------------------------------------

    username = st.session_state.get(
        "username",
        "User"
    )

    st.markdown(
        f"""
        <div class="executive-banner">
            <div class="executive-title">
                📊 Executive Dashboard
            </div>

            <div class="executive-subtitle">
                Welcome, {username}. Review your platform-wide fraud intelligence,
                risk signals, and system activity from one place.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # MAIN KPI CARDS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">Platform Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-icon">📦</div>
                <div class="summary-value">{total_predictions}</div>
                <div class="summary-label">Total Predictions</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-icon">🚨</div>
                <div class="summary-value">{fraud_count}</div>
                <div class="summary-label">Fraud Detected</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-icon">✅</div>
                <div class="summary-value">{legitimate_count}</div>
                <div class="summary-label">Legitimate Records</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-icon">⚠️</div>
                <div class="summary-value">{fraud_rate}%</div>
                <div class="summary-label">Overall Fraud Rate</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c5:
        st.markdown(
            f"""
            <div class="summary-card">
                <div class="summary-icon">🎯</div>
                <div class="summary-value">{average_probability}%</div>
                <div class="summary-label">Average Risk Score</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------
    # DATASET COUNTS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">Fraud Detection Modules</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3 = st.columns(3)

    with m1:
        st.metric(
            "💰 Financial Fraud Records",
            financial_count
        )

    with m2:
        st.metric(
            "💳 Credit Card Records",
            credit_count
        )

    with m3:
        st.metric(
            "🏦 Synthetic Fraud Records",
            synthetic_count
        )

    # ------------------------------------------------------
    # MAIN CHARTS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">Fraud Analytics Overview</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        try:
            pie_chart = fraud_distribution_chart(
                financial_count,
                credit_count,
                synthetic_count
            )

            st.plotly_chart(
                pie_chart,
                use_container_width=True
            )

        except Exception:
            st.info(
                "Fraud distribution chart will appear when data is available."
            )

    with chart_col2:
        try:
            bar_chart = fraud_bar_chart(
                financial_count,
                credit_count,
                synthetic_count
            )

            st.plotly_chart(
                bar_chart,
                use_container_width=True
            )

        except Exception:
            st.info(
                "Fraud records chart will appear when data is available."
            )

    # ------------------------------------------------------
    # PREDICTION CHARTS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">Prediction Intelligence</div>',
        unsafe_allow_html=True
    )

    prediction_col1, prediction_col2 = st.columns(2)

    with prediction_col1:
        try:
            fig = prediction_chart(
                all_predictions
            )

            if fig is not None:
                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
            else:
                st.info(
                    "Prediction chart is not available yet."
                )

        except Exception:
            st.info(
                "Prediction chart is not available yet."
            )

    with prediction_col2:
        try:
            fig = probability_histogram(
                all_predictions
            )

            if fig is not None:
                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
            else:
                st.info(
                    "Risk probability chart is not available yet."
                )

        except Exception:
            st.info(
                "Risk probability chart is not available yet."
            )

    # ------------------------------------------------------
    # TIMELINE
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">Transaction Trend</div>',
        unsafe_allow_html=True
    )

    timeline_df = prepare_timeline(
        all_predictions
    )

    if not timeline_df.empty:
        fig = px.line(
            timeline_df,
            x="date",
            y="transactions",
            markers=True,
            title="Predictions Processed Over Time"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:
        st.info(
            "Transaction timeline will appear after prediction records include created_at values."
        )

    # ------------------------------------------------------
    # SYSTEM ACTIVITY
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">System Activity</div>',
        unsafe_allow_html=True
    )

    a1, a2, a3 = st.columns(3)

    with a1:
        st.metric(
            "🚨 Alert History",
            len(alerts_df)
        )

    with a2:
        st.metric(
            "🔌 API Requests Logged",
            len(api_logs_df)
        )

    with a3:
        st.metric(
            "📡 Kafka Messages Logged",
            len(kafka_logs_df)
        )

    # ------------------------------------------------------
    # EXECUTIVE INSIGHT
    # ------------------------------------------------------

    if fraud_rate >= 20:
        insight = (
            "High fraud activity is currently visible. "
            "Review the Fraud Alerts and Risk Score Center immediately."
        )

    elif fraud_rate >= 5:
        insight = (
            "Moderate fraud activity is visible. "
            "Continue monitoring high-risk transactions and alerts."
        )

    else:
        insight = (
            "Fraud activity is currently within a lower range. "
            "Continue monitoring model predictions and streaming activity."
        )

    st.markdown(
        f"""
        <div class="insight-box">
            <b>🧠 Executive Insight</b><br><br>
            {insight}
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # RECENT ALERTS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">Recent Alerts</div>',
        unsafe_allow_html=True
    )

    if not alerts_df.empty:
        st.dataframe(
            alerts_df.tail(10),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "No alert history is available yet."
        )