import streamlit as st
import pandas as pd
import plotly.express as px

from utils.db import load_metrics


# ==========================================================
# HELPERS
# ==========================================================

def go_home():
    st.session_state.page = "Home"
    st.rerun()


def load_model_metrics():
    try:
        df = load_metrics()

        if df is None:
            return pd.DataFrame()

        return df

    except Exception as error:
        st.error(f"Unable to load model metrics: {error}")
        return pd.DataFrame()


def prepare_metrics_dataframe(df):
    df = df.copy()

    # Convert common metric columns safely to numeric values
    possible_metric_columns = [
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "f1",
        "roc_auc",
        "auc",
        "training_time",
        "test_size"
    ]

    for column in possible_metric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Handle different possible F1 column names
    if "f1_score" not in df.columns and "f1" in df.columns:
        df["f1_score"] = df["f1"]

    # Handle different possible AUC column names
    if "roc_auc" not in df.columns and "auc" in df.columns:
        df["roc_auc"] = df["auc"]

    # Find model name column if it has a different name
    if "model_name" not in df.columns:
        possible_model_columns = [
            "model",
            "Model",
            "algorithm",
            "classifier"
        ]

        for column in possible_model_columns:
            if column in df.columns:
                df["model_name"] = df[column].astype(str)
                break

    if "model_name" not in df.columns:
        df["model_name"] = "Unknown Model"

    # Find dataset column if it has a different name
    if "dataset" not in df.columns:
        possible_dataset_columns = [
            "data_source",
            "dataset_name",
            "module",
            "source"
        ]

        for column in possible_dataset_columns:
            if column in df.columns:
                df["dataset"] = df[column].astype(str)
                break

    if "dataset" not in df.columns:
        df["dataset"] = "All Datasets"

    # Date / timestamp handling
    possible_date_columns = [
        "created_at",
        "trained_at",
        "timestamp",
        "training_date"
    ]

    for column in possible_date_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(
                df[column],
                errors="coerce"
            )
            df["metric_datetime"] = df[column]
            break

    return df


def get_best_model(df):
    if df.empty:
        return None

    ranking_column = None

    for column in [
        "f1_score",
        "accuracy",
        "roc_auc",
        "precision",
        "recall"
    ]:
        if column in df.columns:
            ranking_column = column
            break

    if ranking_column is None:
        return None

    valid_df = df.dropna(
        subset=[ranking_column]
    )

    if valid_df.empty:
        return None

    return valid_df.sort_values(
        by=ranking_column,
        ascending=False
    ).iloc[0]


def get_metric_value(record, column_name):
    if record is None:
        return 0.0

    value = record.get(column_name, 0)

    try:
        return float(value)

    except Exception:
        return 0.0


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_model_performance():

    st.markdown(
        """
        <style>

        .model-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(40, 20, 95, 0.96),
                rgba(105, 70, 190, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .model-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .model-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .model-card {
            padding: 18px;
            border-radius: 16px;
            text-align: center;
            background: rgba(255, 255, 255, 0.10);
            border: 1px solid rgba(255, 255, 255, 0.18);
            box-shadow: 0 5px 16px rgba(0, 0, 0, 0.12);
            min-height: 120px;
        }

        .model-icon {
            font-size: 28px;
        }

        .model-value {
            font-size: 28px;
            font-weight: 800;
            margin-top: 7px;
        }

        .model-label {
            font-size: 14px;
            opacity: 0.80;
            margin-top: 4px;
        }

        .best-model-box {
            padding: 20px;
            border-radius: 14px;
            margin-top: 15px;
            background: rgba(105, 70, 190, 0.14);
            border-left: 5px solid #6946be;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home"):
        go_home()

    st.markdown(
        """
        <div class="model-banner">
            <div class="model-title">🤖 Model Performance Center</div>
            <div class="model-subtitle">
                Compare fraud detection models using accuracy, precision,
                recall, F1-score, and ROC-AUC metrics.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    df = load_model_metrics()

    if df.empty:
        st.warning(
            "No model metrics are available in the model_metrics table yet."
        )

        st.info(
            "Run your training scripts and save metrics into the database. "
            "After that, this page will automatically show model comparisons."
        )

        st.markdown(
            """
            ### Expected metrics columns

            Your `model_metrics` table should preferably contain:

            - `model_name`
            - `dataset`
            - `accuracy`
            - `precision`
            - `recall`
            - `f1_score`
            - `roc_auc`
            - `created_at`
            """
        )

        return

    df = prepare_metrics_dataframe(df)

    # ------------------------------------------------------
    # FILTERS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔎 Model Filters</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        dataset_options = ["All"] + sorted(
            df["dataset"]
            .astype(str)
            .dropna()
            .unique()
            .tolist()
        )

        selected_dataset = st.selectbox(
            "Dataset / Module",
            dataset_options
        )

    with col2:
        model_options = ["All"] + sorted(
            df["model_name"]
            .astype(str)
            .dropna()
            .unique()
            .tolist()
        )

        selected_model = st.selectbox(
            "Model",
            model_options
        )

    filtered_df = df.copy()

    if selected_dataset != "All":
        filtered_df = filtered_df[
            filtered_df["dataset"].astype(str)
            == selected_dataset
        ]

    if selected_model != "All":
        filtered_df = filtered_df[
            filtered_df["model_name"].astype(str)
            == selected_model
        ]

    if filtered_df.empty:
        st.warning(
            "No metrics match the selected filters."
        )
        return

    # ------------------------------------------------------
    # BEST MODEL
    # ------------------------------------------------------

    best_model = get_best_model(filtered_df)

    best_model_name = "Not Available"
    best_f1 = 0.0
    best_accuracy = 0.0
    best_precision = 0.0
    best_recall = 0.0

    if best_model is not None:
        best_model_name = str(
            best_model.get(
                "model_name",
                "Unknown Model"
            )
        )

        best_f1 = get_metric_value(
            best_model,
            "f1_score"
        )

        best_accuracy = get_metric_value(
            best_model,
            "accuracy"
        )

        best_precision = get_metric_value(
            best_model,
            "precision"
        )

        best_recall = get_metric_value(
            best_model,
            "recall"
        )

    # ------------------------------------------------------
    # KPI CARDS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📊 Performance Summary</div>',
        unsafe_allow_html=True
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    cards = [
        ("🤖", filtered_df["model_name"].nunique(), "Models Compared"),
        ("🏆", best_model_name, "Best Model"),
        ("🎯", f"{best_accuracy:.2%}", "Best Accuracy"),
        ("⚖️", f"{best_precision:.2%}", "Best Precision"),
        ("📈", f"{best_f1:.2%}", "Best F1 Score")
    ]

    for column, card in zip(
        [m1, m2, m3, m4, m5],
        cards
    ):
        icon, value, label = card

        with column:
            st.markdown(
                f"""
                <div class="model-card">
                    <div class="model-icon">{icon}</div>
                    <div class="model-value" style="font-size:22px;">
                        {value}
                    </div>
                    <div class="model-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # ------------------------------------------------------
    # BEST MODEL INSIGHT
    # ------------------------------------------------------

    if best_model is not None:
        st.markdown(
            f"""
            <div class="best-model-box">
                <b>🏆 Best Performing Model: {best_model_name}</b><br><br>
                Accuracy: <b>{best_accuracy:.2%}</b><br>
                Precision: <b>{best_precision:.2%}</b><br>
                Recall: <b>{best_recall:.2%}</b><br>
                F1 Score: <b>{best_f1:.2%}</b><br><br>
                This model currently has the strongest available performance
                based on the stored evaluation metrics.
            </div>
            """,
            unsafe_allow_html=True
        )

    # ------------------------------------------------------
    # METRIC COMPARISON CHART
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📈 Model Metric Comparison</div>',
        unsafe_allow_html=True
    )

    metric_columns = [
        column for column in [
            "accuracy",
            "precision",
            "recall",
            "f1_score",
            "roc_auc"
        ]
        if column in filtered_df.columns
    ]

    if metric_columns:
        chart_df = filtered_df[
            ["model_name"] + metric_columns
        ].copy()

        chart_df = chart_df.melt(
            id_vars="model_name",
            value_vars=metric_columns,
            var_name="Metric",
            value_name="Score"
        )

        chart_df = chart_df.dropna(
            subset=["Score"]
        )

        if not chart_df.empty:
            fig = px.bar(
                chart_df,
                x="model_name",
                y="Score",
                color="Metric",
                barmode="group",
                title="Fraud Detection Model Comparison"
            )

            fig.update_yaxes(
                range=[0, 1]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    else:
        st.info(
            "No standard metric columns were found for chart generation."
        )

    # ------------------------------------------------------
    # ACCURACY VS F1
    # ------------------------------------------------------

    if (
        "accuracy" in filtered_df.columns
        and "f1_score" in filtered_df.columns
    ):
        st.markdown(
            '<div class="section-heading">🎯 Accuracy vs F1 Score</div>',
            unsafe_allow_html=True
        )

        scatter_df = filtered_df.dropna(
            subset=["accuracy", "f1_score"]
        )

        if not scatter_df.empty:
            fig = px.scatter(
                scatter_df,
                x="accuracy",
                y="f1_score",
                size="recall" if "recall" in scatter_df.columns else None,
                hover_name="model_name",
                color="dataset",
                title="Accuracy and F1 Score Relationship"
            )

            fig.update_xaxes(
                range=[0, 1]
            )

            fig.update_yaxes(
                range=[0, 1]
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    # ------------------------------------------------------
    # PERFORMANCE TABLE
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📋 Detailed Model Metrics</div>',
        unsafe_allow_html=True
    )

    preferred_columns = [
        "model_name",
        "dataset",
        "accuracy",
        "precision",
        "recall",
        "f1_score",
        "roc_auc",
        "training_time",
        "metric_datetime",
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
        ].sort_values(
            by="f1_score",
            ascending=False
        ) if "f1_score" in filtered_df.columns else filtered_df[
            display_columns
        ],
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
        "📥 Download Model Performance Report",
        csv_data,
        "model_performance_report.csv",
        "text/csv",
        use_container_width=True
    )