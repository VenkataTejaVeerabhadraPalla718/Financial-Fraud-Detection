import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

from utils.db import load_kafka_logs


# ==========================================================
# HELPERS
# ==========================================================

def go_home():
    st.session_state.page = "Home"
    st.rerun()


def load_realtime_logs():
    try:
        df = load_kafka_logs()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception as error:
        st.error(f"Unable to load Kafka logs: {error}")
        return pd.DataFrame()


def prepare_logs(df):
    df = df.copy()

    possible_time_columns = [
        "created_at",
        "timestamp",
        "message_time",
        "processed_at"
    ]

    for column in possible_time_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )
            df["log_time"] = df[column]
            break

    possible_topic_columns = [
        "topic",
        "kafka_topic",
        "topic_name"
    ]

    for column in possible_topic_columns:
        if column in df.columns:
            df["topic_display"] = df[column].astype(str)
            break

    if "topic_display" not in df.columns:
        df["topic_display"] = "fraud-transactions"

    return df


def get_kafka_summary(df):
    if df.empty:
        return {
            "messages": 0,
            "topics": 0,
            "last_time": None,
            "latest_status": "Waiting for data"
        }

    messages = len(df)

    topics = 0
    if "topic_display" in df.columns:
        topics = df["topic_display"].nunique()

    last_time = None
    if "log_time" in df.columns:
        valid_times = df["log_time"].dropna()

        if not valid_times.empty:
            last_time = valid_times.max()

    return {
        "messages": messages,
        "topics": topics,
        "last_time": last_time,
        "latest_status": "Connected"
    }


def create_timeline_chart(df):
    if df.empty or "log_time" not in df.columns:
        return None

    timeline_df = df.dropna(
        subset=["log_time"]
    ).copy()

    if timeline_df.empty:
        return None

    timeline_df["minute"] = timeline_df[
        "log_time"
    ].dt.floor("min")

    grouped_df = (
        timeline_df.groupby("minute")
        .size()
        .reset_index(name="Messages")
    )

    if grouped_df.empty:
        return None

    return px.line(
        grouped_df,
        x="minute",
        y="Messages",
        markers=True,
        title="Kafka Messages Over Time"
    )


def create_topic_chart(df):
    if df.empty or "topic_display" not in df.columns:
        return None

    topic_df = (
        df["topic_display"]
        .value_counts()
        .reset_index()
    )

    topic_df.columns = [
        "Topic",
        "Messages"
    ]

    if topic_df.empty:
        return None

    return px.bar(
        topic_df,
        x="Topic",
        y="Messages",
        title="Kafka Messages by Topic"
    )


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_realtime_monitor():

    st.markdown(
        """
        <style>

        .live-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(120, 20, 20, 0.96),
                rgba(220, 55, 55, 0.78)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .live-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .live-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .status-card {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 120px;
        }

        .status-icon {
            font-size: 28px;
        }

        .status-value {
            font-size: 25px;
            font-weight: 800;
            margin-top: 7px;
        }

        .status-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .live-info-box {
            padding: 18px;
            border-radius: 14px;
            margin-top: 15px;
            background: rgba(220, 55, 55, 0.10);
            border-left: 5px solid #dc3545;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home", use_container_width=False):
        go_home()

    st.markdown(
        """
        <div class="live-banner">
            <div class="live-title">📡 Real-Time Kafka Monitor</div>
            <div class="live-subtitle">
                Monitor streaming fraud transactions, Kafka topics,
                message activity, and live ingestion status.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # CONTROLS
    # ------------------------------------------------------

    control_col1, control_col2, control_col3 = st.columns(
        [2, 2, 3]
    )

    with control_col1:
        auto_refresh = st.toggle(
            "Enable Auto Refresh",
            value=False,
            key="kafka_auto_refresh"
        )

    with control_col2:
        refresh_seconds = st.selectbox(
            "Refresh Interval",
            [5, 10, 20, 30, 60],
            index=1,
            key="kafka_refresh_seconds"
        )

    with control_col3:
        if st.button(
            "🔄 Refresh Kafka Data",
            use_container_width=True
        ):
            st.rerun()

    if auto_refresh:
        st.caption(
            f"Auto refresh is enabled. Refresh interval: {refresh_seconds} seconds."
        )
        st.info(
            "For continuous live refresh, use the Refresh button or add "
            "`streamlit-autorefresh` later. The page will refresh when you interact with it."
        )

    # ------------------------------------------------------
    # LOAD DATA
    # ------------------------------------------------------

    logs = load_realtime_logs()
    logs = prepare_logs(logs)

    summary = get_kafka_summary(logs)

    # ------------------------------------------------------
    # STATUS CARDS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📊 Kafka Streaming Status</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    kafka_status = (
        "🟢 Connected"
        if summary["messages"] > 0
        else "🟡 Waiting"
    )

    with c1:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-icon">📡</div>
                <div class="status-value">{kafka_status}</div>
                <div class="status-label">Kafka Status</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-icon">📨</div>
                <div class="status-value">{summary["messages"]}</div>
                <div class="status-label">Messages Processed</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-icon">🗂️</div>
                <div class="status-value">{summary["topics"]}</div>
                <div class="status-label">Active Topics</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    last_activity = "No messages yet"

    if summary["last_time"] is not None:
        last_activity = summary["last_time"].strftime(
            "%d %b %Y %I:%M:%S %p"
        )

    with c4:
        st.markdown(
            f"""
            <div class="status-card">
                <div class="status-icon">⏱️</div>
                <div class="status-value" style="font-size:16px;">
                    {last_activity}
                </div>
                <div class="status-label">Latest Activity</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------
    # LIVE MESSAGE TABLE
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📨 Recent Kafka Messages</div>',
        unsafe_allow_html=True
    )

    if logs.empty:
        st.warning(
            "No Kafka logs are available yet. Start your Kafka consumer "
            "and ensure it saves messages into the kafka_logs table."
        )

    else:
        display_df = logs.copy()

        if "log_time" in display_df.columns:
            display_df = display_df.sort_values(
                by="log_time",
                ascending=False
            )

        st.dataframe(
            display_df.head(100),
            use_container_width=True,
            hide_index=True
        )

        csv_data = display_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            "📥 Download Kafka Logs",
            csv_data,
            "kafka_logs.csv",
            "text/csv",
            use_container_width=True
        )

    # ------------------------------------------------------
    # CHARTS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📈 Kafka Message Analytics</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        timeline_chart = create_timeline_chart(logs)

        if timeline_chart is not None:
            st.plotly_chart(
                timeline_chart,
                use_container_width=True
            )
        else:
            st.info(
                "Kafka timeline chart will appear when logs contain a timestamp column."
            )

    with chart_col2:
        topic_chart = create_topic_chart(logs)

        if topic_chart is not None:
            st.plotly_chart(
                topic_chart,
                use_container_width=True
            )
        else:
            st.info(
                "Topic chart will appear when logs contain a topic column."
            )

    # ------------------------------------------------------
    # LATEST MESSAGE DETAILS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔍 Latest Message Details</div>',
        unsafe_allow_html=True
    )

    if not logs.empty:
        latest_record = logs.iloc[0].to_dict()

        detail_data = pd.DataFrame(
            {
                "Field": list(latest_record.keys()),
                "Value": [
                    str(value)
                    for value in latest_record.values()
                ]
            }
        )

        st.dataframe(
            detail_data,
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info(
            "Latest message details will appear after Kafka messages are received."
        )

    # ------------------------------------------------------
    # SYSTEM NOTE
    # ------------------------------------------------------

    status_message = (
        "Kafka data is actively available in the database. "
        "Use this page to inspect incoming fraud transactions."
        if summary["messages"] > 0
        else
        "Kafka is ready, but no stored messages were found. "
        "Start your Kafka producer and consumer pipeline."
    )

    st.markdown(
        f"""
        <div class="live-info-box">
            <b>🧠 Live Monitoring Note</b><br><br>
            {status_message}
        </div>
        """,
        unsafe_allow_html=True
    )