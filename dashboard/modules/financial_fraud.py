import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_table
from utils.charts import prediction_chart, probability_histogram


# ==========================================================
# HELPERS
# ==========================================================

def go_home():
    st.session_state.page = "Home"
    st.rerun()


def load_financial_data():
    try:
        df = load_table("fraud_predictions")

        if df is None:
            return pd.DataFrame()

        return df

    except Exception as error:
        st.error(f"Unable to load financial fraud data: {error}")
        return pd.DataFrame()


def prepare_dataframe(df):
    df = df.copy()

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(
            df["created_at"],
            errors="coerce"
        )

    if "prediction" in df.columns:
        df["prediction_label"] = df["prediction"].apply(
            lambda value: "Fraud" if value == 1 else "Legitimate"
        )

    if "fraud_probability" in df.columns:
        df["fraud_probability"] = pd.to_numeric(
            df["fraud_probability"],
            errors="coerce"
        ).fillna(0)

        df["risk_percent"] = (
            df["fraud_probability"] * 100
        ).round(2)

    return df


def filter_dataframe(df, search_text, prediction_filter, min_probability):
    filtered_df = df.copy()

    if search_text:
        searchable_columns = [
            column for column in filtered_df.columns
            if filtered_df[column].dtype == "object"
        ]

        if searchable_columns:
            search_mask = pd.Series(
                False,
                index=filtered_df.index
            )

            for column in searchable_columns:
                search_mask = search_mask | (
                    filtered_df[column]
                    .astype(str)
                    .str.contains(
                        search_text,
                        case=False,
                        na=False
                    )
                )

            filtered_df = filtered_df[search_mask]

    if (
        prediction_filter != "All"
        and "prediction_label" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["prediction_label"] == prediction_filter
        ]

    if "fraud_probability" in filtered_df.columns:
        filtered_df = filtered_df[
            filtered_df["fraud_probability"] >= min_probability
        ]

    return filtered_df


def get_metrics(df):
    if df.empty:
        return 0, 0, 0, 0.0

    total_records = len(df)

    fraud_records = 0

    if "prediction" in df.columns:
        fraud_records = int(
            (df["prediction"] == 1).sum()
        )

    legitimate_records = total_records - fraud_records

    average_probability = 0.0

    if "fraud_probability" in df.columns:
        average_probability = round(
            df["fraud_probability"].mean() * 100,
            2
        )

    return (
        total_records,
        fraud_records,
        legitimate_records,
        average_probability
    )


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_financial_fraud():

    st.markdown(
        """
        <style>

        .financial-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(10, 80, 70, 0.96),
                rgba(0, 140, 110, 0.78)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .financial-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .financial-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .metric-box {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 120px;
        }

        .metric-icon {
            font-size: 28px;
        }

        .metric-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 7px;
        }

        .metric-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .risk-box {
            padding: 18px;
            border-radius: 14px;
            margin-top: 15px;
            background: rgba(0, 140, 110, 0.12);
            border-left: 5px solid #00a67a;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    top_left, top_right = st.columns([1, 6])

    with top_left:
        if st.button(
            "← Home",
            use_container_width=True
        ):
            go_home()

    st.markdown(
        """
        <div class="financial-banner">
            <div class="financial-title">
                💰 Financial Fraud Analytics
            </div>

            <div class="financial-subtitle">
                Investigate financial fraud predictions, risk probabilities,
                and transaction-level fraud patterns.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_financial_data()

    if df.empty:
        st.warning(
            "No records are available in the fraud_predictions table yet."
        )
        st.info(
            "Run your financial fraud API or prediction pipeline first, "
            "then refresh this page."
        )
        return

    df = prepare_dataframe(df)

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔎 Search and Filters</div>',
        unsafe_allow_html=True
    )

    filter_col1, filter_col2, filter_col3 = st.columns(3)

    with filter_col1:
        search_text = st.text_input(
            "Search transactions",
            placeholder="Search transaction ID, customer ID, etc."
        )

    with filter_col2:
        prediction_filter = st.selectbox(
            "Prediction Type",
            ["All", "Fraud", "Legitimate"]
        )

    with filter_col3:
        min_probability = st.slider(
            "Minimum Fraud Probability",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01
        )

    filtered_df = filter_dataframe(
        df,
        search_text,
        prediction_filter,
        min_probability
    )

    # ------------------------------------------------------
    # METRICS
    # ------------------------------------------------------

    (
        total_records,
        fraud_records,
        legitimate_records,
        average_probability
    ) = get_metrics(filtered_df)

    st.markdown(
        '<div class="section-heading">📊 Fraud Summary</div>',
        unsafe_allow_html=True
    )

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-icon">📦</div>
                <div class="metric-value">{total_records}</div>
                <div class="metric-label">Filtered Records</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_col2:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-icon">🚨</div>
                <div class="metric-value">{fraud_records}</div>
                <div class="metric-label">Fraud Predictions</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_col3:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-icon">✅</div>
                <div class="metric-value">{legitimate_records}</div>
                <div class="metric-label">Legitimate Predictions</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with metric_col4:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-icon">🎯</div>
                <div class="metric-value">{average_probability}%</div>
                <div class="metric-label">Average Risk Score</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------
    # CHARTS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📈 Fraud Visualizations</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        chart = prediction_chart(filtered_df)

        if chart is not None:
            st.plotly_chart(
                chart,
                use_container_width=True
            )
        else:
            st.info("Prediction chart is not available.")

    with chart_col2:
        chart = probability_histogram(filtered_df)

        if chart is not None:
            st.plotly_chart(
                chart,
                use_container_width=True
            )
        else:
            st.info("Fraud probability chart is not available.")

    # ------------------------------------------------------
    # RISK DISTRIBUTION
    # ------------------------------------------------------

    if "fraud_probability" in filtered_df.columns:
        st.markdown(
            '<div class="section-heading">⚠️ Risk Distribution</div>',
            unsafe_allow_html=True
        )

        risk_df = filtered_df.copy()

        risk_df["risk_level"] = pd.cut(
            risk_df["fraud_probability"],
            bins=[-0.01, 0.30, 0.70, 1.00],
            labels=["Low Risk", "Medium Risk", "High Risk"]
        )

        risk_counts = (
            risk_df["risk_level"]
            .value_counts()
            .reset_index()
        )

        risk_counts.columns = [
            "Risk Level",
            "Transactions"
        ]

        risk_chart = px.bar(
            risk_counts,
            x="Risk Level",
            y="Transactions",
            title="Transaction Risk Levels"
        )

        st.plotly_chart(
            risk_chart,
            use_container_width=True
        )

    # ------------------------------------------------------
    # HIGH RISK TRANSACTIONS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🚨 High-Risk Transactions</div>',
        unsafe_allow_html=True
    )

    high_risk_df = filtered_df.copy()

    if "fraud_probability" in high_risk_df.columns:
        high_risk_df = high_risk_df[
            high_risk_df["fraud_probability"] >= 0.70
        ]

    if not high_risk_df.empty:
        display_columns = [
            column for column in [
                "transaction_id",
                "Transaction_ID",
                "customer_id",
                "Customer_ID",
                "prediction_label",
                "fraud_probability",
                "risk_percent",
                "created_at"
            ]
            if column in high_risk_df.columns
        ]

        if not display_columns:
            display_columns = list(
                high_risk_df.columns
            )

        st.dataframe(
            high_risk_df[
                display_columns
            ].tail(100),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success(
            "No high-risk transactions match the selected filters."
        )

    # ------------------------------------------------------
    # ALL TRANSACTIONS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📋 Financial Transaction Records</div>',
        unsafe_allow_html=True
    )

    st.dataframe(
        filtered_df.tail(500),
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------------------
    # DOWNLOAD CSV
    # ------------------------------------------------------

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="📥 Download Filtered Financial Fraud Records",
        data=csv_data,
        file_name="financial_fraud_records.csv",
        mime="text/csv",
        use_container_width=True
    )

    # ------------------------------------------------------
    # RISK INSIGHT
    # ------------------------------------------------------

    if total_records > 0:
        fraud_rate = round(
            (fraud_records / total_records) * 100,
            2
        )

        if fraud_rate >= 20:
            message = (
                "High fraud activity is present in the selected records. "
                "Review high-risk transactions and create alerts immediately."
            )

        elif fraud_rate >= 5:
            message = (
                "Moderate fraud activity is present. "
                "Continue monitoring high-probability transactions."
            )

        else:
            message = (
                "Fraud activity is currently low in the selected records. "
                "Continue monitoring new transactions."
            )

        st.markdown(
            f"""
            <div class="risk-box">
                <b>🧠 Financial Fraud Insight</b><br><br>
                Fraud Rate: <b>{fraud_rate}%</b><br>
                {message}
            </div>
            """,
            unsafe_allow_html=True
        )