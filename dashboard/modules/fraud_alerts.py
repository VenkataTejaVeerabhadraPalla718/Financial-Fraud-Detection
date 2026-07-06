import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_alerts


def go_home():
    st.session_state.page = "Home"
    st.rerun()


def load_alert_data():
    try:
        df = load_alerts()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception as error:
        st.error(f"Unable to load fraud alerts: {error}")
        return pd.DataFrame()


def prepare_alert_dataframe(df):
    df = df.copy()

    possible_time_columns = [
        "created_at",
        "alert_time",
        "timestamp",
        "generated_at"
    ]

    for column in possible_time_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )
            df["alert_datetime"] = df[column]
            break

    possible_risk_columns = [
        "fraud_probability",
        "risk_score",
        "confidence",
        "probability"
    ]

    for column in possible_risk_columns:
        if column in df.columns:
            df["risk_value"] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0)

            # Converts values such as 80 to 0.80 when needed
            if df["risk_value"].max() > 1:
                df["risk_value"] = (
                    df["risk_value"] / 100
                )

            break

    if "risk_value" not in df.columns:
        df["risk_value"] = 0.0

    if "severity" not in df.columns:
        df["severity"] = pd.cut(
            df["risk_value"],
            bins=[-0.01, 0.30, 0.70, 1.00],
            labels=["Low", "Medium", "High"]
        ).astype(str)

    if "status" not in df.columns:
        df["status"] = "Open"

    return df


def filter_alerts(
    df,
    search_text,
    severity_filter,
    status_filter,
    min_risk
):
    filtered_df = df.copy()

    if severity_filter != "All":
        filtered_df = filtered_df[
            filtered_df["severity"].astype(str)
            .str.lower()
            == severity_filter.lower()
        ]

    if status_filter != "All":
        filtered_df = filtered_df[
            filtered_df["status"].astype(str)
            .str.lower()
            == status_filter.lower()
        ]

    filtered_df = filtered_df[
        filtered_df["risk_value"] >= min_risk
    ]

    if search_text:
        text_columns = [
            column
            for column in filtered_df.columns
            if filtered_df[column].dtype == "object"
        ]

        if text_columns:
            mask = pd.Series(
                False,
                index=filtered_df.index
            )

            for column in text_columns:
                mask = mask | (
                    filtered_df[column]
                    .astype(str)
                    .str.contains(
                        search_text,
                        case=False,
                        na=False
                    )
                )

            filtered_df = filtered_df[mask]

    return filtered_df


def show_fraud_alerts():

    st.markdown(
        """
        <style>

        .alert-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(130, 20, 20, 0.96),
                rgba(220, 53, 69, 0.80)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .alert-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .alert-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .alert-metric {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 120px;
        }

        .alert-icon {
            font-size: 28px;
        }

        .alert-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 7px;
        }

        .alert-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .high-alert-box {
            padding: 18px;
            border-radius: 14px;
            margin-top: 15px;
            background: rgba(220, 53, 69, 0.12);
            border-left: 5px solid #dc3545;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home"):
        go_home()

    st.markdown(
        """
        <div class="alert-banner">
            <div class="alert-title">🚨 Fraud Alerts Center</div>
            <div class="alert-subtitle">
                Review suspicious transactions, prioritize high-risk cases,
                and monitor fraud alert history.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_alert_data()

    if df.empty:
        st.warning(
            "No records are available in the alert_history table yet."
        )
        st.info(
            "Alerts will appear here after your prediction pipeline "
            "creates high-risk fraud alerts."
        )
        return

    df = prepare_alert_dataframe(df)

    st.markdown(
        '<div class="section-heading">🔎 Alert Filters</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search_text = st.text_input(
            "Search alert",
            placeholder="Transaction ID, customer, message..."
        )

    with col2:
        severity_filter = st.selectbox(
            "Severity",
            ["All", "High", "Medium", "Low"]
        )

    with col3:
        statuses = ["All"] + sorted(
            df["status"]
            .astype(str)
            .dropna()
            .unique()
            .tolist()
        )

        status_filter = st.selectbox(
            "Alert Status",
            statuses
        )

    with col4:
        min_risk = st.slider(
            "Minimum Risk",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
        )

    filtered_df = filter_alerts(
        df,
        search_text,
        severity_filter,
        status_filter,
        min_risk
    )

    total_alerts = len(filtered_df)

    high_alerts = len(
        filtered_df[
            filtered_df["severity"]
            .astype(str)
            .str.lower() == "high"
        ]
    )

    medium_alerts = len(
        filtered_df[
            filtered_df["severity"]
            .astype(str)
            .str.lower() == "medium"
        ]
    )

    open_alerts = len(
        filtered_df[
            filtered_df["status"]
            .astype(str)
            .str.lower()
            .isin(["open", "pending", "new"])
        ]
    )

    st.markdown(
        '<div class="section-heading">📊 Alert Summary</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3, m4 = st.columns(4)

    cards = [
        ("🚨", total_alerts, "Filtered Alerts"),
        ("🔴", high_alerts, "High Severity"),
        ("🟡", medium_alerts, "Medium Severity"),
        ("📬", open_alerts, "Open / Pending")
    ]

    for column, card in zip(
        [m1, m2, m3, m4],
        cards
    ):
        icon, value, label = card

        with column:
            st.markdown(
                f"""
                <div class="alert-metric">
                    <div class="alert-icon">{icon}</div>
                    <div class="alert-value">{value}</div>
                    <div class="alert-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="section-heading">📈 Alert Severity Distribution</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        severity_counts = (
            filtered_df["severity"]
            .astype(str)
            .value_counts()
            .reset_index()
        )

        severity_counts.columns = [
            "Severity",
            "Alerts"
        ]

        if not severity_counts.empty:
            fig = px.pie(
                severity_counts,
                names="Severity",
                values="Alerts",
                hole=0.45,
                title="Alerts by Severity"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    with chart_col2:
        status_counts = (
            filtered_df["status"]
            .astype(str)
            .value_counts()
            .reset_index()
        )

        status_counts.columns = [
            "Status",
            "Alerts"
        ]

        if not status_counts.empty:
            fig = px.bar(
                status_counts,
                x="Status",
                y="Alerts",
                title="Alerts by Status"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    st.markdown(
        '<div class="section-heading">🔴 High-Risk Fraud Alerts</div>',
        unsafe_allow_html=True
    )

    high_risk_df = filtered_df[
        filtered_df["severity"]
        .astype(str)
        .str.lower() == "high"
    ].copy()

    if high_risk_df.empty:
        st.success(
            "No high-severity alerts match the selected filters."
        )
    else:
        display_columns = [
            column
            for column in [
                "id",
                "alert_id",
                "transaction_id",
                "Transaction_ID",
                "customer_id",
                "severity",
                "status",
                "risk_value",
                "fraud_probability",
                "alert_datetime",
                "created_at",
                "message"
            ]
            if column in high_risk_df.columns
        ]

        if not display_columns:
            display_columns = list(high_risk_df.columns)

        st.dataframe(
            high_risk_df[
                display_columns
            ].head(100),
            use_container_width=True,
            hide_index=True
        )

    st.markdown(
        '<div class="section-heading">📋 All Fraud Alerts</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        filtered_df.tail(500),
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Alert History",
        csv_data,
        "fraud_alert_history.csv",
        "text/csv",
        use_container_width=True
    )

    if high_alerts > 0:
        alert_note = (
            f"{high_alerts} high-severity alert(s) require priority investigation. "
            "Review the related transaction data and risk scores."
        )
    else:
        alert_note = (
            "No high-severity alerts match the current filters. "
            "Continue monitoring incoming prediction results."
        )

    st.markdown(
        f"""
        <div class="high-alert-box">
            <b>🧠 Alert Investigation Note</b><br><br>
            {alert_note}
        </div>
        """,
        unsafe_allow_html=True
    )