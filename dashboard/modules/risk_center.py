import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_table


# ==========================================================
# HELPERS
# ==========================================================

def go_home():
    st.session_state.page = "Home"
    st.rerun()


def load_prediction_data():
    table_names = [
        "fraud_predictions",
        "credit_card_predictions",
        "synthetic_predictions"
    ]

    dataframes = []

    for table_name in table_names:
        try:
            df = load_table(table_name)

            if df is not None and not df.empty:
                df = df.copy()
                df["source_module"] = table_name
                dataframes.append(df)

        except Exception:
            pass

    if not dataframes:
        return pd.DataFrame()

    return pd.concat(
        dataframes,
        ignore_index=True,
        sort=False
    )


def prepare_dataframe(df):
    df = df.copy()

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
        ).fillna(0)

        # Handles probabilities stored as 0–100 or 0–1
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


def get_recommendation(risk_score):
    if risk_score >= 80:
        return (
            "🚫 Block the transaction immediately and create a high-priority fraud alert."
        )

    if risk_score >= 50:
        return (
            "⚠️ Hold the transaction for manual verification and request additional validation."
        )

    return (
        "✅ Transaction risk is low. Continue monitoring for unusual behavior."
    )


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_risk_center():

    st.markdown(
        """
        <style>

        .risk-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(105, 65, 0, 0.96),
                rgba(230, 155, 0, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .risk-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .risk-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .risk-metric {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 120px;
        }

        .risk-icon {
            font-size: 28px;
        }

        .risk-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 7px;
        }

        .risk-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .recommendation-box {
            padding: 18px;
            border-radius: 14px;
            margin-top: 18px;
            background: rgba(230, 155, 0, 0.14);
            border-left: 5px solid #e69b00;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home"):
        go_home()

    st.markdown(
        """
        <div class="risk-banner">
            <div class="risk-title">⚠️ Risk Score Center</div>
            <div class="risk-subtitle">
                Review fraud risk scores, identify high-risk transactions,
                and get recommended actions for investigation.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_prediction_data()

    if df.empty:
        st.warning(
            "No prediction records are available yet."
        )
        st.info(
            "Run one or more fraud prediction pipelines first. "
            "This page combines financial, credit-card, and synthetic predictions."
        )
        return

    df = prepare_dataframe(df)

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔎 Risk Filters</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        selected_module = st.selectbox(
            "Data Source",
            ["All"] + sorted(
                df["source_module"].unique().tolist()
            )
        )

    with col2:
        selected_risk = st.selectbox(
            "Risk Level",
            ["All", "High Risk", "Medium Risk", "Low Risk"]
        )

    with col3:
        minimum_score = st.slider(
            "Minimum Risk Score",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )

    filtered_df = df.copy()

    if selected_module != "All":
        filtered_df = filtered_df[
            filtered_df["source_module"] == selected_module
        ]

    if selected_risk != "All":
        filtered_df = filtered_df[
            filtered_df["risk_level"] == selected_risk
        ]

    filtered_df = filtered_df[
        filtered_df["risk_score"] >= minimum_score
    ]

    # ------------------------------------------------------
    # KPI SUMMARY
    # ------------------------------------------------------

    total_records = len(filtered_df)

    high_risk_count = len(
        filtered_df[
            filtered_df["risk_level"] == "High Risk"
        ]
    )

    medium_risk_count = len(
        filtered_df[
            filtered_df["risk_level"] == "Medium Risk"
        ]
    )

    low_risk_count = len(
        filtered_df[
            filtered_df["risk_level"] == "Low Risk"
        ]
    )

    average_risk = 0.0

    if total_records > 0:
        average_risk = round(
            filtered_df["risk_score"].mean(),
            2
        )

    st.markdown(
        '<div class="section-heading">📊 Risk Summary</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    cards = [
        ("📦", total_records, "Filtered Transactions"),
        ("🔴", high_risk_count, "High Risk"),
        ("🟡", medium_risk_count, "Medium Risk"),
        ("🟢", low_risk_count, "Low Risk"),
        ("🎯", f"{average_risk}%", "Average Risk Score")
    ]

    for column, card in zip(
        [m1, m2, m3, m4, m5],
        cards
    ):
        icon, value, label = card

        with column:
            st.markdown(
                f"""
                <div class="risk-metric">
                    <div class="risk-icon">{icon}</div>
                    <div class="risk-value">{value}</div>
                    <div class="risk-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ------------------------------------------------------
    # RISK GAUGE
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🎯 Overall Risk Level</div>',
        unsafe_allow_html=True
    )

    gauge_col1, gauge_col2 = st.columns([2, 1])

    with gauge_col1:
        gauge_data = pd.DataFrame(
            {
                "Category": ["Average Risk", "Remaining"],
                "Value": [
                    average_risk,
                    max(0, 100 - average_risk)
                ]
            }
        )

        gauge_chart = px.pie(
            gauge_data,
            names="Category",
            values="Value",
            hole=0.72,
            title="Average Fraud Risk Score"
        )

        st.plotly_chart(
            gauge_chart,
            use_container_width=True
        )

    with gauge_col2:
        st.metric(
            "Average Risk Score",
            f"{average_risk}/100"
        )

        st.progress(
            min(max(average_risk / 100, 0), 1)
        )

        if average_risk >= 80:
            st.error("🔴 HIGH RISK")

        elif average_risk >= 50:
            st.warning("🟡 MEDIUM RISK")

        else:
            st.success("🟢 LOW RISK")

    # ------------------------------------------------------
    # RISK DISTRIBUTION
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📈 Risk Distribution</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        risk_counts = (
            filtered_df["risk_level"]
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
            title="Transactions by Risk Level"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    with chart_col2:
        module_risk = (
            filtered_df.groupby("source_module")[
                "risk_score"
            ]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            module_risk,
            x="source_module",
            y="risk_score",
            title="Average Risk Score by Module"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # ------------------------------------------------------
    # LATEST / HIGHEST-RISK TRANSACTION
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🚨 Highest-Risk Transaction</div>',
        unsafe_allow_html=True
    )

    if not filtered_df.empty:
        latest = filtered_df.sort_values(
            by="risk_score",
            ascending=False
        ).iloc[0]

        risk_score = float(latest["risk_score"])

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Risk Score",
                f"{risk_score}/100"
            )

        with c2:
            prediction = latest.get(
                "prediction",
                0
            )

            st.metric(
                "Prediction",
                "Fraud" if prediction == 1 else "Legitimate"
            )

        with c3:
            probability = latest.get(
                "fraud_probability",
                0
            )

            st.metric(
                "Probability",
                f"{float(probability):.2%}"
            )

        st.subheader("Risk Level")

        st.progress(
            min(max(risk_score / 100, 0), 1)
        )

        if risk_score >= 80:
            st.error("🔴 HIGH RISK")

        elif risk_score >= 50:
            st.warning("🟡 MEDIUM RISK")

        else:
            st.success("🟢 LOW RISK")

        st.metric(
            "Risk Level",
            latest.get(
                "risk_level",
                "Unknown"
            )
        )

        recommendation = get_recommendation(
            risk_score
        )

        st.markdown(
            f"""
            <div class="recommendation-box">
                <b>🧠 Recommended Action</b><br><br>
                {recommendation}
            </div>
            """,
            unsafe_allow_html=True
        )

        transaction_details = pd.DataFrame(
            {
                "Field": list(latest.index),
                "Value": [
                    str(value)
                    for value in latest.values
                ]
            }
        )

        with st.expander(
            "View Highest-Risk Transaction Details"
        ):
            st.dataframe(
                transaction_details,
                use_container_width=True,
                hide_index=True
            )

    # ------------------------------------------------------
    # HIGH-RISK TABLE
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔴 High-Risk Transactions</div>',
        unsafe_allow_html=True
    )

    high_risk_df = filtered_df[
        filtered_df["risk_score"] >= 70
    ].copy()

    if high_risk_df.empty:
        st.success(
            "No high-risk transactions match the selected filters."
        )

    else:
        preferred_columns = [
            "source_module",
            "transaction_id",
            "Transaction_ID",
            "customer_id",
            "Customer_ID",
            "prediction_label",
            "risk_score",
            "fraud_probability",
            "risk_level",
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
            ].sort_values(
                by="risk_score",
                ascending=False
            ).head(200),
            use_container_width=True,
            hide_index=True
        )

    # ------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Risk Score Report",
        csv_data,
        "risk_score_report.csv",
        "text/csv",
        use_container_width=True
    )