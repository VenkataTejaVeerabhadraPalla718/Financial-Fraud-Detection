import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import (
    get_counts,
    load_table,
    load_alerts,
    load_api_logs,
    load_kafka_logs,
    load_metrics
)


# ==========================================================
# HELPERS
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


def safe_load_table(table_name):
    try:
        df = load_table(table_name)

        if df is None:
            return pd.DataFrame()

        return df

    except Exception:
        return pd.DataFrame()


def get_dataframe_memory_mb(df):
    if df.empty:
        return 0.0

    try:
        return round(
            df.memory_usage(
                deep=True
            ).sum() / (1024 * 1024),
            4
        )

    except Exception:
        return 0.0


def get_table_info(table_name, display_name):
    df = safe_load_table(table_name)

    return {
        "Table": display_name,
        "Database Table": table_name,
        "Records": len(df),
        "Columns": len(df.columns),
        "Estimated Memory (MB)": get_dataframe_memory_mb(df)
    }


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_database_analytics():

    st.markdown(
        """
        <style>

        .db-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(25, 45, 80, 0.96),
                rgba(50, 95, 160, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .db-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .db-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .db-card {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 120px;
        }

        .db-icon {
            font-size: 28px;
        }

        .db-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 7px;
        }

        .db-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .db-note {
            padding: 18px;
            border-radius: 14px;
            margin-top: 18px;
            background: rgba(50, 95, 160, 0.14);
            border-left: 5px solid #3260a0;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home"):
        go_home()

    st.markdown(
        """
        <div class="db-banner">
            <div class="db-title">🗄️ Database Analytics</div>
            <div class="db-subtitle">
                Review PostgreSQL table records, prediction storage,
                alerts, logs, and model metric availability.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # LOAD CORE COUNTS
    # ------------------------------------------------------

    try:
        financial_count, credit_count, synthetic_count = get_counts()

    except Exception:
        financial_count = 0
        credit_count = 0
        synthetic_count = 0

    alerts_df = safe_load(load_alerts)
    api_logs_df = safe_load(load_api_logs)
    kafka_logs_df = safe_load(load_kafka_logs)
    metrics_df = safe_load(load_metrics)

    total_records = (
        financial_count
        + credit_count
        + synthetic_count
        + len(alerts_df)
        + len(api_logs_df)
        + len(kafka_logs_df)
        + len(metrics_df)
    )

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📊 Database Overview</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    cards = [
        ("🗄️", total_records, "Total Stored Records"),
        ("💰", financial_count, "Financial Predictions"),
        ("💳", credit_count, "Credit Predictions"),
        ("🏦", synthetic_count, "Synthetic Predictions"),
        ("🚨", len(alerts_df), "Alert Records")
    ]

    for column, card in zip(
        [c1, c2, c3, c4, c5],
        cards
    ):
        icon, value, label = card

        with column:
            st.markdown(
                f"""
                <div class="db-card">
                    <div class="db-icon">{icon}</div>
                    <div class="db-value">{value}</div>
                    <div class="db-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ------------------------------------------------------
    # TABLE SUMMARY
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📋 Database Table Summary</div>',
        unsafe_allow_html=True
    )

    table_info = [
        get_table_info(
            "fraud_predictions",
            "Financial Fraud Predictions"
        ),
        get_table_info(
            "credit_card_predictions",
            "Credit Card Predictions"
        ),
        get_table_info(
            "synthetic_predictions",
            "Synthetic Fraud Predictions"
        ),
        {
            "Table": "Fraud Alert History",
            "Database Table": "alert_history",
            "Records": len(alerts_df),
            "Columns": len(alerts_df.columns),
            "Estimated Memory (MB)": get_dataframe_memory_mb(alerts_df)
        },
        {
            "Table": "Kafka Logs",
            "Database Table": "kafka_logs",
            "Records": len(kafka_logs_df),
            "Columns": len(kafka_logs_df.columns),
            "Estimated Memory (MB)": get_dataframe_memory_mb(kafka_logs_df)
        },
        {
            "Table": "API Logs",
            "Database Table": "api_logs",
            "Records": len(api_logs_df),
            "Columns": len(api_logs_df.columns),
            "Estimated Memory (MB)": get_dataframe_memory_mb(api_logs_df)
        },
        {
            "Table": "Model Metrics",
            "Database Table": "model_metrics",
            "Records": len(metrics_df),
            "Columns": len(metrics_df.columns),
            "Estimated Memory (MB)": get_dataframe_memory_mb(metrics_df)
        }
    ]

    table_summary_df = pd.DataFrame(table_info)

    st.dataframe(
        table_summary_df,
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------------------
    # CHARTS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📈 Storage and Record Distribution</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        record_chart_df = table_summary_df[
            ["Table", "Records"]
        ].copy()

        fig = px.bar(
            record_chart_df,
            x="Table",
            y="Records",
            title="Records Stored by Table"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with chart_col2:
        memory_chart_df = table_summary_df[
            ["Table", "Estimated Memory (MB)"]
        ].copy()

        fig = px.pie(
            memory_chart_df,
            names="Table",
            values="Estimated Memory (MB)",
            hole=0.45,
            title="Estimated DataFrame Memory Usage"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ------------------------------------------------------
    # TABLE EXPLORER
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔍 Database Table Explorer</div>',
        unsafe_allow_html=True
    )

    selected_table = st.selectbox(
        "Select a table to preview",
        table_summary_df["Database Table"].tolist()
    )

    preview_df = safe_load_table(selected_table)

    # Tables loaded through special functions
    if selected_table == "alert_history":
        preview_df = alerts_df

    elif selected_table == "kafka_logs":
        preview_df = kafka_logs_df

    elif selected_table == "api_logs":
        preview_df = api_logs_df

    elif selected_table == "model_metrics":
        preview_df = metrics_df

    if preview_df.empty:
        st.warning(
            f"No records are available in `{selected_table}`."
        )

    else:
        preview_rows = st.slider(
            "Rows to preview",
            min_value=10,
            max_value=min(500, len(preview_df)),
            value=min(50, len(preview_df)),
            step=10
        )

        st.dataframe(
            preview_df.tail(preview_rows),
            use_container_width=True,
            hide_index=True
        )

        csv_data = preview_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            f"📥 Download {selected_table} Data",
            csv_data,
            f"{selected_table}.csv",
            "text/csv",
            use_container_width=True
        )

    # ------------------------------------------------------
    # DATABASE HEALTH
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🩺 Database Health Summary</div>',
        unsafe_allow_html=True
    )

    active_tables = len(
        table_summary_df[
            table_summary_df["Records"] > 0
        ]
    )

    total_tables = len(table_summary_df)

    health_percentage = round(
        (active_tables / total_tables) * 100,
        2
    ) if total_tables > 0 else 0

    health_col1, health_col2 = st.columns(
        [2, 1]
    )

    with health_col1:
        st.progress(
            min(max(health_percentage / 100, 0), 1)
        )

        st.caption(
            f"{active_tables} out of {total_tables} tracked tables contain data."
        )

    with health_col2:
        st.metric(
            "Database Activity",
            f"{health_percentage}%"
        )

    if health_percentage >= 80:
        note = (
            "Database activity is healthy. Most platform modules have stored data."
        )

    elif health_percentage >= 40:
        note = (
            "Database activity is partially available. Some modules may still need data insertion."
        )

    else:
        note = (
            "Database activity is low. Run prediction pipelines, Kafka consumers, "
            "or API requests to populate the platform tables."
        )

    st.markdown(
        f"""
        <div class="db-note">
            <b>🧠 Database Insight</b><br><br>
            {note}
        </div>
        """,
        unsafe_allow_html=True
    )