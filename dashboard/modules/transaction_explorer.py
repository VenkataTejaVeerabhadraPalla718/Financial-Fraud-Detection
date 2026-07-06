import streamlit as st
import pandas as pd

from utils.db import load_table


# ==========================================================
# HELPERS
# ==========================================================

def go_home():
    st.session_state.page = "Home"
    st.rerun()


def load_all_transactions():
    tables = {
        "Financial Fraud": "fraud_predictions",
        "Credit Card Fraud": "credit_card_predictions",
        "Synthetic Fraud": "synthetic_predictions"
    }

    frames = []

    for source_name, table_name in tables.items():
        try:
            df = load_table(table_name)

            if df is not None and not df.empty:
                df = df.copy()
                df["data_source"] = source_name
                frames.append(df)

        except Exception:
            pass

    if not frames:
        return pd.DataFrame()

    return pd.concat(
        frames,
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

        if df["fraud_probability"].max() > 1:
            df["fraud_probability"] = (
                df["fraud_probability"] / 100
            )

        df["fraud_probability"] = df[
            "fraud_probability"
        ].clip(0, 1)

        df["risk_score"] = (
            df["fraud_probability"] * 100
        ).round(2)

    else:
        df["fraud_probability"] = 0.0
        df["risk_score"] = 0.0

    if "created_at" in df.columns:
        df["created_at"] = pd.to_datetime(
            df["created_at"],
            errors="coerce"
        )

    return df


def search_dataframe(df, search_text):
    if not search_text:
        return df

    searchable_columns = [
        column
        for column in df.columns
        if df[column].dtype == "object"
    ]

    if not searchable_columns:
        return df

    search_mask = pd.Series(
        False,
        index=df.index
    )

    for column in searchable_columns:
        search_mask = search_mask | (
            df[column]
            .astype(str)
            .str.contains(
                search_text,
                case=False,
                na=False
            )
        )

    return df[search_mask]


def get_display_columns(df):
    preferred_columns = [
        "data_source",
        "transaction_id",
        "Transaction_ID",
        "customer_id",
        "Customer_ID",
        "card_id",
        "Card_ID",
        "type",
        "transaction_type",
        "amount",
        "prediction_label",
        "prediction",
        "fraud_probability",
        "risk_score",
        "created_at"
    ]

    columns = [
        column
        for column in preferred_columns
        if column in df.columns
    ]

    return columns if columns else list(df.columns)


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_transaction_explorer():

    st.markdown(
        """
        <style>

        .explorer-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(20, 60, 110, 0.96),
                rgba(35, 125, 205, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .explorer-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .explorer-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .explorer-card {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 110px;
        }

        .explorer-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 8px;
        }

        .explorer-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home"):
        go_home()

    st.markdown(
        """
        <div class="explorer-banner">
            <div class="explorer-title">🔍 Transaction Explorer</div>
            <div class="explorer-subtitle">
                Search, filter, inspect, and export financial, credit-card,
                and synthetic fraud transaction records.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_all_transactions()

    if df.empty:
        st.warning(
            "No transaction prediction records are available yet."
        )
        st.info(
            "Run your financial, credit-card, or synthetic prediction pipelines first."
        )
        return

    df = prepare_dataframe(df)

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔎 Search and Filter Transactions</div>',
        unsafe_allow_html=True
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        search_text = st.text_input(
            "Search",
            placeholder="Transaction ID, customer ID, type..."
        )

    with col2:
        source_filter = st.selectbox(
            "Data Source",
            ["All"] + sorted(
                df["data_source"].unique().tolist()
            )
        )

    with col3:
        prediction_filter = st.selectbox(
            "Prediction",
            ["All", "Fraud", "Legitimate"]
        )

    with col4:
        min_risk = st.slider(
            "Minimum Risk Score",
            min_value=0,
            max_value=100,
            value=0,
            step=1
        )

    filtered_df = df.copy()

    if source_filter != "All":
        filtered_df = filtered_df[
            filtered_df["data_source"] == source_filter
        ]

    if (
        prediction_filter != "All"
        and "prediction_label" in filtered_df.columns
    ):
        filtered_df = filtered_df[
            filtered_df["prediction_label"] == prediction_filter
        ]

    filtered_df = filtered_df[
        filtered_df["risk_score"] >= min_risk
    ]

    filtered_df = search_dataframe(
        filtered_df,
        search_text
    )

    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    total = len(filtered_df)

    fraud_count = 0
    if "prediction" in filtered_df.columns:
        fraud_count = int(
            (filtered_df["prediction"] == 1).sum()
        )

    average_risk = 0.0
    if total > 0:
        average_risk = round(
            filtered_df["risk_score"].mean(),
            2
        )

    st.markdown(
        '<div class="section-heading">📊 Transaction Summary</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3, m4 = st.columns(4)

    cards = [
        ("📦", total, "Filtered Transactions"),
        ("🚨", fraud_count, "Fraud Predictions"),
        ("🎯", f"{average_risk}%", "Average Risk Score"),
        ("🗂️", filtered_df["data_source"].nunique(), "Data Sources")
    ]

    for column, card in zip(
        [m1, m2, m3, m4],
        cards
    ):
        icon, value, label = card

        with column:
            st.markdown(
                f"""
                <div class="explorer-card">
                    <div style="font-size:28px;">{icon}</div>
                    <div class="explorer-value">{value}</div>
                    <div class="explorer-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ------------------------------------------------------
    # TABLE
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📋 Transaction Records</div>',
        unsafe_allow_html=True
    )

    display_columns = get_display_columns(
        filtered_df
    )

    sort_column = st.selectbox(
        "Sort By",
        display_columns,
        index=0
    )

    sort_order = st.radio(
        "Sort Order",
        ["Descending", "Ascending"],
        horizontal=True
    )

    sorted_df = filtered_df.copy()

    try:
        sorted_df = sorted_df.sort_values(
            by=sort_column,
            ascending=(sort_order == "Ascending")
        )
    except Exception:
        pass

    st.dataframe(
        sorted_df[
            display_columns
        ].head(1000),
        use_container_width=True,
        hide_index=True
    )

    # ------------------------------------------------------
    # TRANSACTION DETAILS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔍 Inspect One Transaction</div>',
        unsafe_allow_html=True
    )

    if not sorted_df.empty:
        selected_index = st.selectbox(
            "Select transaction row",
            sorted_df.index.tolist(),
            format_func=lambda index: (
                f"Row {index} | "
                f"{sorted_df.loc[index, 'data_source']}"
            )
        )

        selected_transaction = sorted_df.loc[
            selected_index
        ]

        detail_df = pd.DataFrame(
            {
                "Field": list(selected_transaction.index),
                "Value": [
                    str(value)
                    for value in selected_transaction.values
                ]
            }
        )

        st.dataframe(
            detail_df,
            use_container_width=True,
            hide_index=True
        )

        risk_score = float(
            selected_transaction.get(
                "risk_score",
                0
            )
        )

        st.subheader("Transaction Risk")

        st.progress(
            min(max(risk_score / 100, 0), 1)
        )

        if risk_score >= 80:
            st.error(
                f"🔴 HIGH RISK — {risk_score}/100"
            )
        elif risk_score >= 50:
            st.warning(
                f"🟡 MEDIUM RISK — {risk_score}/100"
            )
        else:
            st.success(
                f"🟢 LOW RISK — {risk_score}/100"
            )

    # ------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------

    csv_data = sorted_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "📥 Download Filtered Transactions",
        csv_data,
        "transaction_explorer_export.csv",
        "text/csv",
        use_container_width=True
    )