import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_table
from utils.charts import prediction_chart, probability_histogram


def go_home():
    st.session_state.page = "Home"
    st.rerun()


def load_synthetic_data():
    try:
        df = load_table("synthetic_predictions")
        return df if df is not None else pd.DataFrame()
    except Exception as error:
        st.error(f"Unable to load synthetic fraud data: {error}")
        return pd.DataFrame()


def prepare_dataframe(df):
    df = df.copy()

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(
            df["created_at"],
            errors="coerce"
        )

    if "prediction" in df.columns:
        df["prediction"] = pd.to_numeric(
            df["prediction"],
            errors="coerce"
        ).fillna(0).astype(int)

        df["prediction_label"] = df["prediction"].apply(
            lambda value: "Fraud" if value == 1 else "Legitimate"
        )

    if "fraud_probability" in df.columns:
        df["fraud_probability"] = pd.to_numeric(
            df["fraud_probability"],
            errors="coerce"
        ).fillna(0).clip(0, 1)

        df["risk_percent"] = (
            df["fraud_probability"] * 100
        ).round(2)

    return df


def filter_dataframe(
    df,
    prediction_filter,
    min_probability,
    search_text
):
    filtered_df = df.copy()

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

    if search_text:
        searchable_columns = [
            column
            for column in filtered_df.columns
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

    return filtered_df


def get_summary(df):
    if df.empty:
        return 0, 0, 0, 0.0, 0.0

    total = len(df)

    fraud_count = 0
    if "prediction" in df.columns:
        fraud_count = int(
            (df["prediction"] == 1).sum()
        )

    legitimate_count = total - fraud_count

    fraud_rate = round(
        (fraud_count / total) * 100,
        2
    ) if total > 0 else 0.0

    average_risk = 0.0
    if "fraud_probability" in df.columns:
        average_risk = round(
            df["fraud_probability"].mean() * 100,
            2
        )

    return (
        total,
        fraud_count,
        legitimate_count,
        fraud_rate,
        average_risk
    )


def show_synthetic():

    st.markdown(
        """
        <style>

        .synthetic-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(110, 70, 10, 0.96),
                rgba(190, 125, 20, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .synthetic-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .synthetic-subtitle {
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

        .insight-box {
            padding: 18px;
            border-radius: 14px;
            margin-top: 18px;
            background: rgba(190, 125, 20, 0.14);
            border-left: 5px solid #d99000;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home", use_container_width=False):
        go_home()

    st.markdown(
        """
        <div class="synthetic-banner">
            <div class="synthetic-title">🏦 Synthetic Fraud Analytics</div>
            <div class="synthetic-subtitle">
                Analyze PaySim-style synthetic transaction predictions,
                fraud probabilities, and suspicious transfer patterns.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_synthetic_data()

    if df.empty:
        st.warning(
            "No records are available in the synthetic_predictions table yet."
        )
        st.info(
            "Run the Kafka producer/consumer or synthetic prediction API, "
            "then return here to view synthetic fraud analytics."
        )
        return

    df = prepare_dataframe(df)

    st.markdown(
        '<div class="section-heading">🔎 Search and Filters</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        search_text = st.text_input(
            "Search transaction",
            placeholder="Search transaction type, ID, or record"
        )

    with col2:
        prediction_filter = st.selectbox(
            "Prediction Type",
            ["All", "Fraud", "Legitimate"],
            key="synthetic_prediction_filter"
        )

    with col3:
        min_probability = st.slider(
            "Minimum Fraud Probability",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.01,
            key="synthetic_min_probability"
        )

    filtered_df = filter_dataframe(
        df,
        prediction_filter,
        min_probability,
        search_text
    )

    (
        total,
        fraud_count,
        legitimate_count,
        fraud_rate,
        average_risk
    ) = get_summary(filtered_df)

    st.markdown(
        '<div class="section-heading">📊 Synthetic Fraud Summary</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    cards = [
        ("📦", total, "Filtered Records"),
        ("🚨", fraud_count, "Fraud Predictions"),
        ("✅", legitimate_count, "Legitimate Records"),
        ("⚠️", f"{fraud_rate}%", "Fraud Rate"),
        ("🎯", f"{average_risk}%", "Average Risk")
    ]

    for column, card in zip(
        [m1, m2, m3, m4, m5],
        cards
    ):
        icon, value, label = card

        with column:
            st.markdown(
                f"""
                <div class="metric-box">
                    <div class="metric-icon">{icon}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown(
        '<div class="section-heading">📈 Synthetic Fraud Visualizations</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        fig = prediction_chart(filtered_df)

        if fig is not None:
            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("Prediction chart is not available.")

    with chart_col2:
        fig = probability_histogram(filtered_df)

        if fig is not None:
            st.plotly_chart(
                fig,
                use_container_width=True
            )
        else:
            st.info("Risk probability chart is not available.")

    # ------------------------------------------------------
    # TRANSACTION TYPE ANALYSIS
    # ------------------------------------------------------

    type_column = None

    for column in ["type", "transaction_type", "Transaction_Type"]:
        if column in filtered_df.columns:
            type_column = column
            break

    if type_column is not None:
        st.markdown(
            '<div class="section-heading">🔁 Transaction Type Analysis</div>',
            unsafe_allow_html=True
        )

        type_summary = (
            filtered_df.groupby(type_column)
            .size()
            .reset_index(name="Transactions")
        )

        fig = px.bar(
            type_summary,
            x=type_column,
            y="Transactions",
            title="Synthetic Transactions by Type"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ------------------------------------------------------
    # RISK DISTRIBUTION
    # ------------------------------------------------------

    if "fraud_probability" in filtered_df.columns:
        st.markdown(
            '<div class="section-heading">⚠️ Synthetic Transaction Risk Levels</div>',
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

        fig = px.bar(
            risk_counts,
            x="Risk Level",
            y="Transactions",
            title="Synthetic Fraud Risk Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ------------------------------------------------------
    # HIGH-RISK TABLE
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🚨 High-Risk Synthetic Transactions</div>',
        unsafe_allow_html=True
    )

    high_risk_df = filtered_df.copy()

    if "fraud_probability" in high_risk_df.columns:
        high_risk_df = high_risk_df[
            high_risk_df["fraud_probability"] >= 0.70
        ]

    if not high_risk_df.empty:
        preferred_columns = [
            "step",
            "type",
            "transaction_type",
            "amount",
            "oldbalanceOrg",
            "newbalanceOrig",
            "oldbalanceDest",
            "newbalanceDest",
            "prediction_label",
            "fraud_probability",
            "risk_percent",
            "created_at"
        ]

        display_columns = [
            column
            for column in preferred_columns
            if column in high_risk_df.columns
        ]

        if not display_columns:
            display_columns = list(high_risk_df.columns)

        st.dataframe(
            high_risk_df[
                display_columns
            ].tail(100),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.success(
            "No high-risk synthetic transactions match the selected filters."
        )

    # ------------------------------------------------------
    # FULL TABLE
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📋 Synthetic Prediction Records</div>',
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
        "📥 Download Filtered Synthetic Fraud Records",
        csv_data,
        "synthetic_fraud_records.csv",
        "text/csv",
        use_container_width=True
    )

    # ------------------------------------------------------
    # INSIGHT
    # ------------------------------------------------------

    if fraud_rate >= 20:
        insight = (
            "High synthetic fraud activity is visible. "
            "Review transfer patterns, transaction types, and high-risk records."
        )

    elif fraud_rate >= 5:
        insight = (
            "Moderate synthetic fraud activity is visible. "
            "Continue monitoring high-probability transaction patterns."
        )

    else:
        insight = (
            "Synthetic fraud activity is currently low in the selected records. "
            "Continue monitoring the Kafka stream and prediction API."
        )

    st.markdown(
        f"""
        <div class="insight-box">
            <b>🧠 Synthetic Fraud Insight</b><br><br>
            Current fraud rate: <b>{fraud_rate}%</b><br>
            {insight}
        </div>
        """,
        unsafe_allow_html=True
    )