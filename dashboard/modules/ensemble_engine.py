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


def load_ensemble_data():
    try:
        df = load_table("ensemble_predictions")

        if df is None:
            return pd.DataFrame()

        return df

    except Exception as error:
        st.error(f"Unable to load ensemble predictions: {error}")
        return pd.DataFrame()


def prepare_dataframe(df):
    df = df.copy()

    # Convert model prediction columns to numbers
    prediction_columns = [
        "logistic_prediction",
        "random_forest_prediction",
        "xgboost_prediction",
        "final_prediction"
    ]

    for column in prediction_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            ).fillna(0).astype(int)

    # Confidence can be stored as 0-1 or 0-100
    if "confidence" in df.columns:
        df["confidence"] = pd.to_numeric(
            df["confidence"],
            errors="coerce"
        ).fillna(0)

        if df["confidence"].max() > 1:
            df["confidence"] = (
                df["confidence"] / 100
            )

        df["confidence"] = df[
            "confidence"
        ].clip(0, 1)

        df["confidence_percent"] = (
            df["confidence"] * 100
        ).round(2)

    else:
        df["confidence"] = 0.0
        df["confidence_percent"] = 0.0

    # Final label
    if "final_prediction" in df.columns:
        df["final_label"] = df[
            "final_prediction"
        ].apply(
            lambda value: "Fraud"
            if value == 1
            else "Legitimate"
        )

    else:
        df["final_prediction"] = 0
        df["final_label"] = "Legitimate"

    # Timestamp conversion
    possible_date_columns = [
        "created_at",
        "timestamp",
        "prediction_time"
    ]

    for column in possible_date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )
            df["prediction_datetime"] = df[column]
            break

    # Agreement calculation
    model_columns = [
        column for column in [
            "logistic_prediction",
            "random_forest_prediction",
            "xgboost_prediction"
        ]
        if column in df.columns
    ]

    if model_columns:
        df["agreement_percent"] = (
            df[model_columns]
            .sum(axis=1)
            / len(model_columns)
        ) * 100

        df["agreement_percent"] = df[
            "agreement_percent"
        ].round(2)

    else:
        df["agreement_percent"] = 0.0

    return df


def get_summary(df):
    if df.empty:
        return 0, 0, 0, 0.0, 0.0

    total = len(df)

    fraud_count = int(
        (df["final_prediction"] == 1).sum()
    )

    legitimate_count = total - fraud_count

    average_confidence = round(
        df["confidence_percent"].mean(),
        2
    )

    average_agreement = round(
        df["agreement_percent"].mean(),
        2
    )

    return (
        total,
        fraud_count,
        legitimate_count,
        average_confidence,
        average_agreement
    )


def create_vote_chart(df):
    model_columns = [
        column for column in [
            "logistic_prediction",
            "random_forest_prediction",
            "xgboost_prediction"
        ]
        if column in df.columns
    ]

    if not model_columns:
        return None

    chart_rows = []

    for column in model_columns:
        fraud_votes = int(
            (df[column] == 1).sum()
        )

        legitimate_votes = int(
            (df[column] == 0).sum()
        )

        readable_name = column.replace(
            "_prediction",
            ""
        ).replace(
            "_",
            " "
        ).title()

        chart_rows.append(
            {
                "Model": readable_name,
                "Prediction": "Fraud",
                "Votes": fraud_votes
            }
        )

        chart_rows.append(
            {
                "Model": readable_name,
                "Prediction": "Legitimate",
                "Votes": legitimate_votes
            }
        )

    chart_df = pd.DataFrame(chart_rows)

    return px.bar(
        chart_df,
        x="Model",
        y="Votes",
        color="Prediction",
        barmode="group",
        title="Model Voting Comparison"
    )


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_ensemble_engine():

    st.markdown(
        """
        <style>

        .ensemble-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(35, 20, 95, 0.96),
                rgba(100, 65, 200, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .ensemble-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .ensemble-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .ensemble-card {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 120px;
        }

        .ensemble-icon {
            font-size: 28px;
        }

        .ensemble-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 7px;
        }

        .ensemble-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .ensemble-note {
            padding: 18px;
            border-radius: 14px;
            margin-top: 18px;
            background: rgba(100, 65, 200, 0.14);
            border-left: 5px solid #6441c8;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home"):
        go_home()

    st.markdown(
        """
        <div class="ensemble-banner">
            <div class="ensemble-title">🔬 Ensemble Fraud Engine</div>
            <div class="ensemble-subtitle">
                Compare Logistic Regression, Random Forest, and XGBoost votes
                to produce a more reliable final fraud decision.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_ensemble_data()

    if df.empty:
        st.warning(
            "No ensemble predictions are available yet."
        )

        st.info(
            "Run the ensemble prediction API first. "
            "The page will show data after records are saved to the "
            "`ensemble_predictions` table."
        )

        return

    df = prepare_dataframe(df)

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔎 Ensemble Filters</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        prediction_filter = st.selectbox(
            "Final Prediction",
            ["All", "Fraud", "Legitimate"]
        )

    with col2:
        minimum_confidence = st.slider(
            "Minimum Confidence",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )

    with col3:
        minimum_agreement = st.slider(
            "Minimum Model Agreement",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )

    filtered_df = df.copy()

    if prediction_filter != "All":
        filtered_df = filtered_df[
            filtered_df["final_label"] == prediction_filter
        ]

    filtered_df = filtered_df[
        filtered_df["confidence_percent"] >= minimum_confidence
    ]

    filtered_df = filtered_df[
        filtered_df["agreement_percent"] >= minimum_agreement
    ]

    # ------------------------------------------------------
    # KPI SUMMARY
    # ------------------------------------------------------

    (
        total,
        fraud_count,
        legitimate_count,
        average_confidence,
        average_agreement
    ) = get_summary(filtered_df)

    st.markdown(
        '<div class="section-heading">📊 Ensemble Summary</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4, c5 = st.columns(5)

    cards = [
        ("📦", total, "Predictions"),
        ("🚨", fraud_count, "Fraud"),
        ("✅", legitimate_count, "Legitimate"),
        ("🎯", f"{average_confidence}%", "Average Confidence"),
        ("🤝", f"{average_agreement}%", "Average Agreement")
    ]

    for column, card in zip(
        [c1, c2, c3, c4, c5],
        cards
    ):
        icon, value, label = card

        with column:
            st.markdown(
                f"""
                <div class="ensemble-card">
                    <div class="ensemble-icon">{icon}</div>
                    <div class="ensemble-value">{value}</div>
                    <div class="ensemble-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ------------------------------------------------------
    # VOTING CHART
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📈 Model Voting Analysis</div>',
        unsafe_allow_html=True
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        vote_chart = create_vote_chart(filtered_df)

        if vote_chart is not None:
            st.plotly_chart(
                vote_chart,
                use_container_width=True
            )
        else:
            st.info(
                "Voting chart is not available because model prediction columns are missing."
            )

    with chart_col2:
        confidence_chart = px.histogram(
            filtered_df,
            x="confidence_percent",
            nbins=20,
            title="Confidence Distribution"
        )

        st.plotly_chart(
            confidence_chart,
            use_container_width=True
        )

    # ------------------------------------------------------
    # AGREEMENT CHART
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🤝 Model Agreement Analysis</div>',
        unsafe_allow_html=True
    )

    agreement_chart = px.histogram(
        filtered_df,
        x="agreement_percent",
        nbins=10,
        title="Model Agreement Distribution"
    )

    st.plotly_chart(
        agreement_chart,
        use_container_width=True
    )

    # ------------------------------------------------------
    # HIGH-CONFIDENCE FRAUD
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🚨 High-Confidence Fraud Predictions</div>',
        unsafe_allow_html=True
    )

    high_confidence_fraud = filtered_df[
        (filtered_df["final_prediction"] == 1)
        &
        (filtered_df["confidence_percent"] >= 70)
    ].copy()

    if high_confidence_fraud.empty:
        st.success(
            "No high-confidence fraud predictions match the selected filters."
        )

    else:
        preferred_columns = [
            "transaction_id",
            "Transaction_ID",
            "logistic_prediction",
            "random_forest_prediction",
            "xgboost_prediction",
            "final_prediction",
            "final_label",
            "confidence_percent",
            "agreement_percent",
            "prediction_datetime",
            "created_at"
        ]

        display_columns = [
            column
            for column in preferred_columns
            if column in high_confidence_fraud.columns
        ]

        if not display_columns:
            display_columns = list(
                high_confidence_fraud.columns
            )

        st.dataframe(
            high_confidence_fraud[
                display_columns
            ].sort_values(
                by="confidence_percent",
                ascending=False
            ).head(200),
            use_container_width=True,
            hide_index=True
        )

    # ------------------------------------------------------
    # ALL ENSEMBLE RECORDS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📋 Recent Ensemble Predictions</div>',
        unsafe_allow_html=True
    )

    preferred_columns = [
        "transaction_id",
        "Transaction_ID",
        "logistic_prediction",
        "random_forest_prediction",
        "xgboost_prediction",
        "final_prediction",
        "final_label",
        "confidence_percent",
        "agreement_percent",
        "prediction_datetime",
        "created_at"
    ]

    display_columns = [
        column
        for column in preferred_columns
        if column in filtered_df.columns
    ]

    if not display_columns:
        display_columns = list(filtered_df.columns)

    st.dataframe(
        filtered_df[
            display_columns
        ].tail(500),
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
        "📥 Download Ensemble Prediction Report",
        csv_data,
        "ensemble_prediction_report.csv",
        "text/csv",
        use_container_width=True
    )

    # ------------------------------------------------------
    # INSIGHT
    # ------------------------------------------------------

    if average_agreement >= 80:
        note = (
            "The models show strong agreement. Ensemble predictions are currently consistent."
        )

    elif average_agreement >= 50:
        note = (
            "The models show moderate agreement. Review cases where models disagree."
        )

    else:
        note = (
            "The models show low agreement. Investigate feature quality, "
            "model training, and data consistency."
        )

    st.markdown(
        f"""
        <div class="ensemble-note">
            <b>🧠 Ensemble Insight</b><br><br>
            {note}
        </div>
        """,
        unsafe_allow_html=True
    )