import streamlit as st
import pandas as pd

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


def prepare_prediction_data():
    table_names = [
        "fraud_predictions",
        "credit_card_predictions",
        "synthetic_predictions"
    ]

    dataframes = []

    for table_name in table_names:
        df = safe_load_table(table_name)

        if not df.empty:
            df = df.copy()
            df["source_module"] = table_name
            dataframes.append(df)

    if not dataframes:
        return pd.DataFrame()

    combined_df = pd.concat(
        dataframes,
        ignore_index=True,
        sort=False
    )

    if "prediction" in combined_df.columns:
        combined_df["prediction"] = pd.to_numeric(
            combined_df["prediction"],
            errors="coerce"
        ).fillna(0).astype(int)

    else:
        combined_df["prediction"] = 0

    if "fraud_probability" in combined_df.columns:
        combined_df["fraud_probability"] = pd.to_numeric(
            combined_df["fraud_probability"],
            errors="coerce"
        ).fillna(0)

        if combined_df["fraud_probability"].max() > 1:
            combined_df["fraud_probability"] = (
                combined_df["fraud_probability"] / 100
            )

        combined_df["fraud_probability"] = combined_df[
            "fraud_probability"
        ].clip(0, 1)

    else:
        combined_df["fraud_probability"] = 0.0

    combined_df["risk_score"] = (
        combined_df["fraud_probability"] * 100
    ).round(2)

    return combined_df


def get_platform_context():
    predictions_df = prepare_prediction_data()
    alerts_df = safe_load(load_alerts)
    kafka_df = safe_load(load_kafka_logs)
    metrics_df = safe_load(load_metrics)

    total_predictions = len(predictions_df)

    fraud_predictions = 0

    if not predictions_df.empty:
        fraud_predictions = int(
            (predictions_df["prediction"] == 1).sum()
        )

    legitimate_predictions = (
        total_predictions - fraud_predictions
    )

    fraud_rate = 0.0

    if total_predictions > 0:
        fraud_rate = round(
            (fraud_predictions / total_predictions) * 100,
            2
        )

    average_risk = 0.0

    if not predictions_df.empty:
        average_risk = round(
            predictions_df["risk_score"].mean(),
            2
        )

    high_risk_count = 0

    if not predictions_df.empty:
        high_risk_count = len(
            predictions_df[
                predictions_df["risk_score"] >= 70
            ]
        )

    context = {
        "total_predictions": total_predictions,
        "fraud_predictions": fraud_predictions,
        "legitimate_predictions": legitimate_predictions,
        "fraud_rate": fraud_rate,
        "average_risk": average_risk,
        "high_risk_count": high_risk_count,
        "alerts_count": len(alerts_df),
        "kafka_count": len(kafka_df),
        "metrics_count": len(metrics_df)
    }

    return context, predictions_df, alerts_df, kafka_df, metrics_df


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


def answer_question(
    question,
    context,
    predictions_df,
    alerts_df,
    kafka_df,
    metrics_df
):
    question_lower = question.lower()

    total_predictions = context["total_predictions"]
    fraud_predictions = context["fraud_predictions"]
    legitimate_predictions = context["legitimate_predictions"]
    fraud_rate = context["fraud_rate"]
    average_risk = context["average_risk"]
    high_risk_count = context["high_risk_count"]
    alerts_count = context["alerts_count"]
    kafka_count = context["kafka_count"]

    # ------------------------------------------------------
    # FRAUD QUESTIONS
    # ------------------------------------------------------

    if (
        "fraud rate" in question_lower
        or "fraud percentage" in question_lower
        or "how much fraud" in question_lower
    ):
        return (
            f"📊 Current fraud rate is **{fraud_rate}%**.\n\n"
            f"Out of **{total_predictions} total predictions**, "
            f"the system identified **{fraud_predictions} fraud cases** "
            f"and **{legitimate_predictions} legitimate cases**."
        )

    if (
        "fraud" in question_lower
        and (
            "count" in question_lower
            or "number" in question_lower
            or "how many" in question_lower
        )
    ):
        return (
            f"🚨 The platform currently contains **{fraud_predictions} fraud predictions** "
            f"out of **{total_predictions} total predictions**."
        )

    # ------------------------------------------------------
    # RISK QUESTIONS
    # ------------------------------------------------------

    if (
        "risk" in question_lower
        and (
            "average" in question_lower
            or "overall" in question_lower
            or "score" in question_lower
        )
    ):
        risk_level = "Low"

        if average_risk >= 80:
            risk_level = "High"
        elif average_risk >= 50:
            risk_level = "Medium"

        return (
            f"⚠️ The current average fraud risk score is **{average_risk}/100**.\n\n"
            f"Overall platform risk level: **{risk_level} Risk**."
        )

    if (
        "high risk" in question_lower
        or "dangerous" in question_lower
        or "suspicious" in question_lower
    ):
        return (
            f"🔴 There are currently **{high_risk_count} high-risk transactions** "
            f"with a risk score of **70 or above**.\n\n"
            f"Recommended action: Review these records in the **Risk Score Center** "
            f"and create alerts for suspicious cases."
        )

    # ------------------------------------------------------
    # ALERT QUESTIONS
    # ------------------------------------------------------

    if (
        "alert" in question_lower
        or "alerts" in question_lower
    ):
        return (
            f"🚨 The platform currently has **{alerts_count} stored fraud alerts**.\n\n"
            f"Open the **Fraud Alerts Center** to inspect severity, "
            f"status, and transaction details."
        )

    # ------------------------------------------------------
    # KAFKA QUESTIONS
    # ------------------------------------------------------

    if (
        "kafka" in question_lower
        or "real time" in question_lower
        or "realtime" in question_lower
        or "live monitor" in question_lower
    ):
        kafka_status = (
            "active"
            if kafka_count > 0
            else "waiting for stored messages"
        )

        return (
            f"📡 Kafka monitoring status: **{kafka_status}**.\n\n"
            f"Stored Kafka messages: **{kafka_count}**.\n\n"
            f"Open the **Real-Time Kafka Monitor** page to inspect "
            f"recent messages and topic activity."
        )

    # ------------------------------------------------------
    # MODEL QUESTIONS
    # ------------------------------------------------------

    if (
        "model" in question_lower
        or "accuracy" in question_lower
        or "precision" in question_lower
        or "recall" in question_lower
        or "f1" in question_lower
        or "performance" in question_lower
    ):
        best_model = get_best_model(metrics_df)

        if best_model is None:
            return (
                "🤖 No saved model metrics are available yet.\n\n"
                "Run your training scripts and save accuracy, precision, recall, "
                "F1-score, and ROC-AUC values into the `model_metrics` table."
            )

        model_name = best_model.get(
            "model_name",
            "Unknown Model"
        )

        accuracy = best_model.get(
            "accuracy",
            "Not Available"
        )

        precision = best_model.get(
            "precision",
            "Not Available"
        )

        recall = best_model.get(
            "recall",
            "Not Available"
        )

        f1_score = best_model.get(
            "f1_score",
            best_model.get("f1", "Not Available")
        )

        return (
            f"🏆 Best available model: **{model_name}**.\n\n"
            f"- Accuracy: **{accuracy}**\n"
            f"- Precision: **{precision}**\n"
            f"- Recall: **{recall}**\n"
            f"- F1 Score: **{f1_score}**\n\n"
            f"Open the **Model Performance Center** for full comparison charts."
        )

    # ------------------------------------------------------
    # DATA / DATABASE QUESTIONS
    # ------------------------------------------------------

    if (
        "database" in question_lower
        or "data" in question_lower
        or "records" in question_lower
    ):
        return (
            f"🗄️ Platform data summary:\n\n"
            f"- Total predictions: **{total_predictions}**\n"
            f"- Fraud predictions: **{fraud_predictions}**\n"
            f"- Alerts stored: **{alerts_count}**\n"
            f"- Kafka logs stored: **{kafka_count}**\n"
            f"- Model metric records: **{context['metrics_count']}**\n\n"
            f"Open **Database Analytics** to explore tables and download records."
        )

    # ------------------------------------------------------
    # HELP QUESTIONS
    # ------------------------------------------------------

    if (
        "help" in question_lower
        or "what can you do" in question_lower
        or "commands" in question_lower
    ):
        return (
            "🤖 I can help you understand the fraud detection platform.\n\n"
            "Try asking:\n\n"
            "- What is the current fraud rate?\n"
            "- How many high-risk transactions are there?\n"
            "- Show fraud alert information.\n"
            "- What is the Kafka status?\n"
            "- Which model performs best?\n"
            "- What is the average risk score?\n"
            "- Give database summary."
        )

    # ------------------------------------------------------
    # DEFAULT RESPONSE
    # ------------------------------------------------------

    return (
        "🤖 I can help with fraud analytics, risk scores, alerts, "
        "Kafka monitoring, database records, and model performance.\n\n"
        "Try asking: **What is the fraud rate?**, "
        "**How many high-risk transactions are there?**, "
        "or **Which model performs best?**"
    )


# ==========================================================
# MAIN PAGE
# ==========================================================

def show_ai_assistant():

    st.markdown(
        """
        <style>

        .assistant-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(15, 55, 95, 0.96),
                rgba(0, 145, 190, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .assistant-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .assistant-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .assistant-info {
            padding: 18px;
            border-radius: 14px;
            margin-top: 15px;
            background: rgba(0, 145, 190, 0.12);
            border-left: 5px solid #0091be;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home"):
        go_home()

    st.markdown(
        """
        <div class="assistant-banner">
            <div class="assistant-title">🤖 AI Fraud Assistant</div>
            <div class="assistant-subtitle">
                Ask questions about fraud activity, risk scores, alerts,
                Kafka streaming, database records, and model performance.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    context, predictions_df, alerts_df, kafka_df, metrics_df = (
        get_platform_context()
    )

    # ------------------------------------------------------
    # PLATFORM SUMMARY
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">📊 Current Platform Context</div>',
        unsafe_allow_html=True
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Predictions",
            context["total_predictions"]
        )

    with c2:
        st.metric(
            "Fraud Cases",
            context["fraud_predictions"]
        )

    with c3:
        st.metric(
            "Average Risk",
            f"{context['average_risk']}%"
        )

    with c4:
        st.metric(
            "Alerts",
            context["alerts_count"]
        )

    # ------------------------------------------------------
    # CHAT HISTORY
    # ------------------------------------------------------

    if "ai_messages" not in st.session_state:
        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your AI Fraud Assistant. "
                    "Ask me about fraud rate, risk scores, alerts, "
                    "Kafka activity, database records, or model performance."
                )
            }
        ]

    st.markdown(
        '<div class="section-heading">💬 Ask the Assistant</div>',
        unsafe_allow_html=True
    )

    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_question = st.chat_input(
        "Ask a question about your fraud detection platform..."
    )

    if user_question:
        st.session_state.ai_messages.append(
            {
                "role": "user",
                "content": user_question
            }
        )

        with st.chat_message("user"):
            st.markdown(user_question)

        assistant_response = answer_question(
            user_question,
            context,
            predictions_df,
            alerts_df,
            kafka_df,
            metrics_df
        )

        st.session_state.ai_messages.append(
            {
                "role": "assistant",
                "content": assistant_response
            }
        )

        with st.chat_message("assistant"):
            st.markdown(assistant_response)

    # ------------------------------------------------------
    # QUICK QUESTIONS
    # ------------------------------------------------------

    st.markdown(
        '<div class="section-heading">⚡ Quick Questions</div>',
        unsafe_allow_html=True
    )

    q1, q2, q3 = st.columns(3)

    with q1:
        if st.button(
            "📊 What is the fraud rate?",
            use_container_width=True
        ):
            question = "What is the current fraud rate?"

            response = answer_question(
                question,
                context,
                predictions_df,
                alerts_df,
                kafka_df,
                metrics_df
            )

            st.session_state.ai_messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

    with q2:
        if st.button(
            "⚠️ Show high-risk transactions",
            use_container_width=True
        ):
            question = "How many high risk transactions are there?"

            response = answer_question(
                question,
                context,
                predictions_df,
                alerts_df,
                kafka_df,
                metrics_df
            )

            st.session_state.ai_messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

    with q3:
        if st.button(
            "🤖 Which model performs best?",
            use_container_width=True
        ):
            question = "Which model performs best?"

            response = answer_question(
                question,
                context,
                predictions_df,
                alerts_df,
                kafka_df,
                metrics_df
            )

            st.session_state.ai_messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

    q4, q5, q6 = st.columns(3)

    with q4:
        if st.button(
            "🚨 Show fraud alerts",
            use_container_width=True
        ):
            question = "Show fraud alert information."

            response = answer_question(
                question,
                context,
                predictions_df,
                alerts_df,
                kafka_df,
                metrics_df
            )

            st.session_state.ai_messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

    with q5:
        if st.button(
            "📡 What is Kafka status?",
            use_container_width=True
        ):
            question = "What is the Kafka status?"

            response = answer_question(
                question,
                context,
                predictions_df,
                alerts_df,
                kafka_df,
                metrics_df
            )

            st.session_state.ai_messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

    with q6:
        if st.button(
            "🗄️ Give database summary",
            use_container_width=True
        ):
            question = "Give database summary."

            response = answer_question(
                question,
                context,
                predictions_df,
                alerts_df,
                kafka_df,
                metrics_df
            )

            st.session_state.ai_messages.append(
                {
                    "role": "user",
                    "content": question
                }
            )

            st.session_state.ai_messages.append(
                {
                    "role": "assistant",
                    "content": response
                }
            )

            st.rerun()

    # ------------------------------------------------------
    # CLEAR CHAT
    # ------------------------------------------------------

    if st.button(
        "🗑️ Clear Chat History",
        use_container_width=True
    ):
        st.session_state.ai_messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! I am your AI Fraud Assistant. "
                    "Ask me about fraud rate, risk scores, alerts, "
                    "Kafka activity, database records, or model performance."
                )
            }
        ]

        st.rerun()

    st.markdown(
        """
        <div class="assistant-info">
            <b>ℹ️ Note</b><br><br>
            This assistant currently uses your stored project data and rule-based
            responses. Later, you can connect it to an LLM API such as OpenAI,
            Gemini, or Groq for more natural conversational answers.
        </div>
        """,
        unsafe_allow_html=True
    )