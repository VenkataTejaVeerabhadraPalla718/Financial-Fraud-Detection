import streamlit as st
import pandas as pd
from datetime import datetime

from utils.db import (
    load_table,
    load_alerts,
    load_kafka_logs,
    load_metrics
)


# ==========================================================
# HELPERS
# ==========================================================

def go_home():
    st.session_state.page = "Home"
    st.rerun()


def safe_load_table(table_name):
    try:
        df = load_table(table_name)

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


def safe_load(loader_function):
    try:
        df = loader_function()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


def load_all_prediction_data():
    table_mapping = {
        "Financial Fraud": "fraud_predictions",
        "Credit Card Fraud": "credit_card_predictions",
        "Synthetic Fraud": "synthetic_predictions"
    }

    dataframes = []

    for source_name, table_name in table_mapping.items():
        df = safe_load_table(table_name)

        if not df.empty:
            df = df.copy()
            df["data_source"] = source_name
            dataframes.append(df)

    if not dataframes:
        return pd.DataFrame()

    combined_df = pd.concat(
        dataframes,
        ignore_index=True,
        sort=False
    )

    return combined_df


def prepare_predictions(df):
    df = df.copy()

    if "prediction" in df.columns:
        df["prediction"] = pd.to_numeric(
            df["prediction"],
            errors="coerce"
        ).fillna(0).astype(int)

        df["prediction_label"] = df["prediction"].apply(
            lambda value: "Fraud"
            if value == 1
            else "Legitimate"
        )

    else:
        df["prediction"] = 0
        df["prediction_label"] = "Legitimate"

    if "fraud_probability" in df.columns:
        df["fraud_probability"] = pd.to_numeric(
            df["fraud_probability"],
            errors="coerce"
        ).fillna(0)

        if df["fraud_probability"].max() > 1:
            df["fraud_probability"] = (
                df["fraud_probability"] / 100
            )

        df["fraud_probability"] = df[
            "fraud_probability"
        ].clip(0, 1)

    else:
        df["fraud_probability"] = 0.0

    df["risk_score"] = (
        df["fraud_probability"] * 100
    ).round(2)

    df["risk_level"] = pd.cut(
        df["fraud_probability"],
        bins=[-0.01, 0.30, 0.70, 1.00],
        labels=["Low Risk", "Medium Risk", "High Risk"]
    ).astype(str)

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(
            df["created_at"],
            errors="coerce"
        )

    return df


def get_best_model(metrics_df):
    if metrics_df.empty:
        return None

    df = metrics_df.copy()

    if "model_name" not in df.columns:
        for column in ["model", "Model", "algorithm"]:
            if column in df.columns:
                df["model_name"] = df[column].astype(str)
                break

    if "model_name" not in df.columns:
        return None

    metric_column = None

    for column in [
        "f1_score",
        "f1",
        "accuracy",
        "roc_auc",
        "precision"
    ]:
        if column in df.columns:
            metric_column = column
            break

    if metric_column is None:
        return None

    df[metric_column] = pd.to_numeric(
        df[metric_column],
        errors="coerce"
    )

    df = df.dropna(
        subset=[metric_column]
    )

    if df.empty:
        return None

    return df.sort_values(
        by=metric_column,
        ascending=False
    ).iloc[0]


def create_report_text(
    predictions_df,
    alerts_df,
    kafka_df,
    metrics_df,
    report_type
):
    generated_time = datetime.now().strftime(
        "%d %B %Y, %I:%M %p"
    )

    total_predictions = len(predictions_df)

    fraud_count = 0
    legitimate_count = 0
    high_risk_count = 0
    average_risk = 0.0
    fraud_rate = 0.0

    if not predictions_df.empty:
        fraud_count = int(
            (predictions_df["prediction"] == 1).sum()
        )

        legitimate_count = (
            total_predictions - fraud_count
        )

        high_risk_count = int(
            (predictions_df["risk_score"] >= 70).sum()
        )

        average_risk = round(
            predictions_df["risk_score"].mean(),
            2
        )

        if total_predictions > 0:
            fraud_rate = round(
                (fraud_count / total_predictions) * 100,
                2
            )

    best_model = get_best_model(metrics_df)

    best_model_text = "No model metrics available."

    if best_model is not None:
        model_name = best_model.get(
            "model_name",
            "Unknown Model"
        )

        accuracy = best_model.get(
            "accuracy",
            "Not Available"
        )

        f1_score = best_model.get(
            "f1_score",
            best_model.get(
                "f1",
                "Not Available"
            )
        )

        best_model_text = (
            f"Best Model: {model_name}\n"
            f"Accuracy: {accuracy}\n"
            f"F1 Score: {f1_score}"
        )

    report = f"""
============================================================
AI-POWERED FINANCIAL FRAUD DETECTION PLATFORM
{report_type.upper()}
============================================================

Generated On: {generated_time}

------------------------------------------------------------
1. EXECUTIVE SUMMARY
------------------------------------------------------------

Total Predictions Processed: {total_predictions}
Fraud Predictions Detected: {fraud_count}
Legitimate Predictions: {legitimate_count}
Overall Fraud Rate: {fraud_rate}%
High-Risk Transactions: {high_risk_count}
Average Risk Score: {average_risk}/100

------------------------------------------------------------
2. FRAUD ALERT SUMMARY
------------------------------------------------------------

Total Fraud Alerts Stored: {len(alerts_df)}

"""

    if not alerts_df.empty:
        report += "Recent Alert Records:\n"

        preview_alerts = alerts_df.tail(5)

        for _, row in preview_alerts.iterrows():
            report += f"- {row.to_dict()}\n"

    else:
        report += "No fraud alerts are currently stored.\n"

    report += f"""

------------------------------------------------------------
3. REAL-TIME KAFKA MONITORING
------------------------------------------------------------

Kafka Messages Stored: {len(kafka_df)}

"""

    if len(kafka_df) > 0:
        report += (
            "Kafka streaming data is available in the platform database.\n"
        )
    else:
        report += (
            "No Kafka messages are currently stored. "
            "Start the producer and consumer pipeline to enable real-time monitoring.\n"
        )

    report += f"""

------------------------------------------------------------
4. MODEL PERFORMANCE SUMMARY
------------------------------------------------------------

{best_model_text}

------------------------------------------------------------
5. RISK ASSESSMENT
------------------------------------------------------------

"""

    if fraud_rate >= 20:
        report += (
            "Risk Status: HIGH\n"
            "Recommendation: Immediately investigate high-risk transactions, "
            "review alerts, and consider blocking suspicious transactions.\n"
        )

    elif fraud_rate >= 5:
        report += (
            "Risk Status: MEDIUM\n"
            "Recommendation: Continue monitoring high-risk predictions and "
            "perform manual verification for suspicious transactions.\n"
        )

    else:
        report += (
            "Risk Status: LOW\n"
            "Recommendation: Continue routine monitoring and evaluate "
            "new transaction patterns regularly.\n"
        )

    report += """

------------------------------------------------------------
6. PROJECT MODULES INCLUDED
------------------------------------------------------------

- Financial Fraud Detection
- Credit Card Fraud Detection
- Synthetic Fraud Detection
- Ensemble Fraud Engine
- Fraud Alerts Center
- Risk Score Center
- Real-Time Kafka Monitor
- Database Analytics
- Model Performance Center
- AI Fraud Assistant

============================================================
END OF REPORT
============================================================
"""

    return report


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_reports():

    st.markdown(
        """
        <style>

        .report-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(15, 75, 65, 0.96),
                rgba(0, 155, 125, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .report-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .report-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .report-card {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 120px;
        }

        .report-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 7px;
        }

        .report-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .report-note {
            padding: 18px;
            border-radius: 14px;
            margin-top: 18px;
            background: rgba(0, 155, 125, 0.14);
            border-left: 5px solid #009b7d;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home"):
        go_home()

    st.markdown(
        """
        <div class="report-banner">
            <div class="report-title">📄 Fraud Intelligence Reports</div>
            <div class="report-subtitle">
                Generate downloadable reports containing fraud analytics,
                risk scores, alerts, Kafka monitoring, and model performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    predictions_df = load_all_prediction_data()
    predictions_df = prepare_predictions(predictions_df)

    alerts_df = safe_load(load_alerts)
    kafka_df = safe_load(load_kafka_logs)
    metrics_df = safe_load(load_metrics)

    total_predictions = len(predictions_df)

    fraud_count = 0
    average_risk = 0.0

    if not predictions_df.empty:
        fraud_count = int(
            (predictions_df["prediction"] == 1).sum()
        )

        average_risk = round(
            predictions_df["risk_score"].mean(),
            2
        )

    # ------------------------------------------------------
    # SUMMARY CARDS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📊 Report Data Summary</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    cards = [
        ("📦", total_predictions, "Predictions"),
        ("🚨", fraud_count, "Fraud Cases"),
        ("⚠️", f"{average_risk}%", "Average Risk"),
        ("📬", len(alerts_df), "Fraud Alerts")
    ]

    for column, card in zip(
        [c1, c2, c3, c4],
        cards
    ):
        icon, value, label = card

        with column:
            st.markdown(
                f"""
                <div class="report-card">
                    <div style="font-size:28px;">{icon}</div>
                    <div class="report-value">{value}</div>
                    <div class="report-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ------------------------------------------------------
    # REPORT OPTIONS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">⚙️ Generate Report</div>',
        unsafe_allow_html=True
    )

    report_type = st.selectbox(
        "Select Report Type",
        [
            "Executive Fraud Report",
            "Risk Assessment Report",
            "Fraud Alert Report",
            "Model Performance Report",
            "Complete Platform Report"
        ]
    )

    report_text = create_report_text(
        predictions_df,
        alerts_df,
        kafka_df,
        metrics_df,
        report_type
    )

    st.text_area(
        "Report Preview",
        report_text,
        height=550
    )

    # ------------------------------------------------------
    # TXT DOWNLOAD
    # ------------------------------------------------------

    st.download_button(
        "📥 Download Report as TXT",
        data=report_text,
        file_name=(
            report_type.lower()
            .replace(" ", "_")
            + ".txt"
        ),
        mime="text/plain",
        use_container_width=True
    )

    # ------------------------------------------------------
    # CSV DOWNLOADS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📥 Download Detailed CSV Reports</div>',
        unsafe_allow_html=True
    )

    csv_col1, csv_col2, csv_col3 = st.columns(3)

    with csv_col1:
        prediction_csv = predictions_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "📊 Download Prediction Report",
            prediction_csv,
            "all_fraud_predictions.csv",
            "text/csv",
            use_container_width=True
        )

    with csv_col2:
        alerts_csv = alerts_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "🚨 Download Alert Report",
            alerts_csv,
            "fraud_alert_history.csv",
            "text/csv",
            use_container_width=True
        )

    with csv_col3:
        metrics_csv = metrics_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "🤖 Download Model Metrics",
            metrics_csv,
            "model_metrics.csv",
            "text/csv",
            use_container_width=True
        )

    # ------------------------------------------------------
    # NOTE
    # ------------------------------------------------------

    st.markdown(
        """
        <div class="report-note">
            <b>ℹ️ Report Note</b><br><br>
            These reports use the current records stored in your PostgreSQL
            database. For a future improvement, you can add PDF generation
            using ReportLab and automatically email reports to administrators.
        </div>
        """,
        unsafe_allow_html=True
    )