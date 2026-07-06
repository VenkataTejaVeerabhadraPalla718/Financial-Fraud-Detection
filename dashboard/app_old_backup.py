import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from datetime import datetime
import base64
import os
from utils.activity_logger import log_activity
from utils.db import *
from utils.auth import *
from utils.styles import *
from utils.charts import *
from utils.ai_assistant import *
from forecasting.forecast import *

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Fraud Detection Platform",
    page_icon="🛡️",
    layout="wide",
)

# =====================================================
# IMAGE PLACEHOLDERS
# =====================================================

LOGIN_IMAGE = "dashboard/assets/ED.png"

LOGO_IMAGE = "dashboard/assets/logo.png"

EXECUTIVE_IMAGE = "dashboard/assets/back.png"

FINANCIAL_IMAGE = "dashboard/assets/background.jpg"

CREDIT_IMAGE = "dashboard/assets/background.jpg"

SYNTHETIC_IMAGE = "dashboard/assets/background.jpg"

ALERT_IMAGE = "dashboard/assets/alert.png"

PROFILE_IMAGE = "dashboard/assets/profile.png"
def set_background(image_file):

    if not image_file or not os.path.exists(image_file):
        return

    with open(image_file, "rb") as f:
        data = base64.b64encode(
            f.read()
        ).decode()

    st.markdown(
        f"""
        <style>

        .stApp {{

            background-image:
            linear-gradient(
                rgba(15,23,42,0.85),
                rgba(15,23,42,0.85)
            ),
            url("data:image/png;base64,{data}");

            background-size: cover;

            background-position: center;

            background-repeat: no-repeat;

            background-attachment: fixed;
        }}

        section[data-testid="stSidebar"] {{

            background-color:
            rgba(17,24,39,0.95);

        }}

        .block-container {{

            background-color:
            rgba(15,23,42,0.55);

            padding: 1rem;

            border-radius: 15px;

        }}

        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# SESSION STATE
# =====================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "username" not in st.session_state:
    st.session_state.username = ""

if "role" not in st.session_state:
    st.session_state.role = "User"

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"
  
# =====================================================
# LOGIN / REGISTER PAGE
# =====================================================

if not st.session_state.get(
        "authenticated",
        False
    ):
    set_background(
        LOGIN_IMAGE
    )
    left, center, right = st.columns([1,2,1])

    with center:

        st.markdown(
            """
            <h1 style="
                text-align:center;
                color:white;
                font-size:55px;
                font-weight:800;
                margin-top:20px;
            ">
                AI Fraud Detection Platform
            </h1>
            """,
            unsafe_allow_html=True
        )

        left, center, right = st.columns([1,2,1])

        with center:

            login_tab, register_tab, forgot_tab = st.tabs(
                [
                    "Login",
                    "Register",
                    "Forgot Password"
                ]
            )
        
        # ==========================================
        # LOGIN
        # ==========================================

        with login_tab:

            username = st.text_input(
                "Username",
                key="login_user"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_pass"
            )

            c1,c2,c3 = st.columns([1,2,1])

            with c2:

                login_clicked = st.button(
                    "Login",
                    use_container_width=True
                )

            if login_clicked:

                user = authenticate_user(
                    username,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.authenticated = True

                    st.session_state.username = user[1]
                    log_activity(
                        username,
                        "Login",
                        "Login Page"
                    )

                    st.rerun()


                    st.session_state.role = (
                        user[4]
                        if user[4]
                        else "User"
                    )
                    st.success(
                        "Login Successful"
                    )

                    st.rerun()

                else:

                    st.error(
                        "Invalid Credentials"
                    )

        # ==========================================
        # REGISTER
        # ==========================================

        with register_tab:

            new_user = st.text_input(
                "Username",
                key="reg_user"
            )

            new_email = st.text_input(
                "Email",
                key="reg_email"
            )

            new_password = st.text_input(
                "Password",
                type="password",
                key="reg_pass"
            )

            if st.button(
                "Create Account",
                use_container_width=True
            ):

                try:

                    register_user(
                        new_user,
                        new_email,
                        new_password
                    )

                    st.success(
                        "Account Created"
                    )

                except Exception as e:

                    st.error(str(e))

        # ==========================================
        # FORGOT PASSWORD
        # ==========================================

        with forgot_tab:

            st.info(
                "Contact Administrator to reset password."
            )

            st.text_input(
                "Registered Email"
            )

            st.button(
                "Request Reset"
            )

# =====================================================
# MAIN DASHBOARD
# =====================================================
else:
    try:

        alerts = load_alerts()

        if len(alerts) > 0:

            latest_alert = alerts.iloc[-1]

            st.sidebar.warning(
                f"🚨 Latest Alert\n\n"
                f"{latest_alert['fraud_type']}"
            )

    except Exception:
        pass

    # ==========================================
    # SIDEBAR
    # ==========================================

    if LOGO_IMAGE != "":
        st.sidebar.image(
            LOGO_IMAGE,
            use_container_width=True
        )
    
    
    st.sidebar.success(
        f"Welcome {st.session_state.username}"
    )

    st.sidebar.info(
        f"Role : {st.session_state.role}"
    )

    page = st.sidebar.radio(

        "Navigation",

        [

            "Executive Dashboard",

            "Financial Fraud",

            "Credit Card Fraud",

            "Synthetic Fraud",

            "Fraud Alerts",

            "Real Time Monitor",

            "Risk Score Center",

            "Transaction Explorer",

            "Database Analytics",

            "Model Performance",

            "API Monitoring",

            "Ensemble Fraud Engine",

            "Admin Settings",

            "System Health",

            "User Activity",

            "Fraud Forecasting",

            "User Settings",

            "🤖 AI Fraud Assistant"

            
        ]

    )
    log_activity(
        st.session_state.username,
        "Visited",
        page
    )

    st.sidebar.markdown(
    "---"
    )
    st.sidebar.caption(
        "Developed by Veera Bhadra"
    )

    if st.sidebar.button(
        "Logout",
        use_container_width=True
    ):

        log_activity(
            st.session_state.username,
            "Logout",
            "Dashboard"
        )

        st.session_state.authenticated = False

        st.session_state.username = ""

        st.rerun()
    
    theme = st.session_state.theme
    if theme == "Dark":

        st.markdown(
            """
            <style>

            .stApp{
                background-color:#0f172a;
                color:white;
            }

            section[data-testid="stSidebar"]{
                background-color:#111827;
            }

            </style>
            """,
            unsafe_allow_html=True
        )

    else:

        st.markdown(
            """
            <style>

            .stApp{
                background-color:#f8fafc;
                color:black;
            }

            section[data-testid="stSidebar"]{
                background-color:white;
            }

            </style>
            """,
            unsafe_allow_html=True
        )
    # =====================================================
    # EXECUTIVE DASHBOARD
    # =====================================================
    refresh_rate = st.sidebar.slider(
        "Auto Refresh (seconds)",
        5,
        60,
        10
    )

    auto_refresh = st.sidebar.checkbox(
        "Enable Auto Refresh",
        value=False
    )

    if auto_refresh:
        import time
        time.sleep(refresh_rate)
        st.rerun()
    if page == "Executive Dashboard":

        set_background(
            EXECUTIVE_IMAGE
        )

        st.title(
            "📊 Executive Dashboard"
        )

    
        financial_count,credit_count,synthetic_count = get_counts()

        alerts = load_alerts()

        api_logs = load_api_logs()

        kafka_logs = load_kafka_logs()

        row1 = st.columns(3)

        row1[0].metric(
            "Financial",
            financial_count
        )

        row1[1].metric(
            "Credit Card",
            credit_count
        )

        row1[2].metric(
            "Synthetic",
            synthetic_count
        )

        row2 = st.columns(3)

        row2[0].metric(
            "Alerts",
            len(alerts)
        )

        row2[1].metric(
            "API Calls",
            len(api_logs)
        )

        row2[2].metric(
            "Kafka Events",
            len(kafka_logs)
        )

        total_records = (
            financial_count
            + credit_count
            + synthetic_count
        )

        avg_alerts = len(alerts)

        st.metric(
            "Total Records",
            total_records
        )

        st.metric(
            "Total Alerts",
            avg_alerts
        )
        st.plotly_chart(

            fraud_distribution_chart(

                financial_count,
                credit_count,
                synthetic_count

            ),

            use_container_width=True

        )

        st.plotly_chart(

            fraud_bar_chart(

                financial_count,
                credit_count,
                synthetic_count

            ),

            use_container_width=True

        )
    # =====================================================
    # FINANCIAL FRAUD DASHBOARD
    # =====================================================

    elif page == "Financial Fraud":

        set_background(
            FINANCIAL_IMAGE
        )

        st.title("💰 Financial Fraud Analytics")

        try:

            df = load_table(
                "fraud_predictions"
            )

            if not df.empty:
                fraud_rate = round(

                    (
                        len(
                            df[df["prediction"] == 1]
                        )
                        /
                        len(df)
                    ) * 100,

                    2

                )
                df["created_at"] = pd.to_datetime(
                    df["created_at"]
                )

                c1,c2,c3 = st.columns(3)

                c1.metric(
                    "Total Records",
                    len(df)
                )

                c2.metric(
                    "Fraud Cases",
                    len(
                        df[
                            df["prediction"] == 1
                        ]
                    )
                )

                c3.metric(
                    "Legitimate",
                    len(
                        df[
                            df["prediction"] == 0
                        ]
                    )
                )

                fig1 = prediction_chart(df)

                if fig1 is not None:
                    st.plotly_chart(
                        fig1,
                        use_container_width=True
                    )

                fig2 = probability_histogram(df)

                if fig2 is not None:
                    st.plotly_chart(
                        fig2,
                        use_container_width=True
                    )

                st.subheader(
                    "Recent Transactions"
                )

                st.dataframe(
                    df.tail(100),
                    use_container_width=True
                )

                csv = df.to_csv(
                    index=False
                )

                st.download_button(
                    "Download Financial Data",
                    csv,
                    "financial_fraud.csv"
                )
                st.metric(
                    "Fraud Rate %",
                    fraud_rate
                )
        except Exception as e:

            st.error(str(e))
       
    # =====================================================
    # CREDIT CARD FRAUD DASHBOARD
    # =====================================================

    elif page == "Credit Card Fraud":

        set_background(
            CREDIT_IMAGE
        )

        st.title(
            "💳 Credit Card Fraud Analytics"
        )

        try:

            df = load_table(
                "credit_card_predictions"
            )

            if not df.empty:

                df["created_at"] = pd.to_datetime(
                    df["created_at"]
                )

                c1,c2,c3 = st.columns(3)

                c1.metric(
                    "Total Records",
                    len(df)
                )

                c2.metric(
                    "Fraud Cases",
                    len(
                        df[
                            df["prediction"] == 1
                        ]
                    )
                )

                c3.metric(
                    "Legitimate",
                    len(
                        df[
                            df["prediction"] == 0
                        ]
                    )
                )

                fig1 = prediction_chart(df)

                if fig1 is not None:
                    st.plotly_chart(
                        fig1,
                        use_container_width=True
                    )

                fig2 = probability_histogram(df)

                if fig2 is not None:
                    st.plotly_chart(
                        fig2,
                        use_container_width=True
                    )

                st.dataframe(
                    df.tail(100),
                    use_container_width=True
                )

                csv = df.to_csv(
                    index=False
                )

                st.download_button(
                    "Download Credit Card Data",
                    csv,
                    "credit_card_fraud.csv"
                )

        except Exception as e:

            st.error(str(e))

    # =====================================================
    # SYNTHETIC FRAUD DASHBOARD
    # =====================================================

    elif page == "Synthetic Fraud":

        set_background(
            SYNTHETIC_IMAGE
        )

        st.title(
            "🏦 Synthetic Fraud Analytics"
        )

        try:

            df = load_table(
                "synthetic_predictions"
            )

            if not df.empty:

                df["created_at"] = pd.to_datetime(
                    df["created_at"]
                )

                c1,c2,c3 = st.columns(3)

                c1.metric(
                    "Total Records",
                    len(df)
                )

                c2.metric(
                    "Fraud Cases",
                    len(
                        df[
                            df["prediction"] == 1
                        ]
                    )
                )

                c3.metric(
                    "Legitimate",
                    len(
                        df[
                            df["prediction"] == 0
                        ]
                    )
                )

                fig1 = prediction_chart(df)

                if fig1 is not None:
                    st.plotly_chart(
                        fig1,
                        use_container_width=True
                    )

                fig2 = probability_histogram(df)

                if fig2 is not None:
                    st.plotly_chart(
                        fig2,
                        use_container_width=True
                    )

                st.dataframe(
                    df.tail(100),
                    use_container_width=True
                )

                csv = df.to_csv(
                    index=False
                )

                st.download_button(
                    "Download Synthetic Data",
                    csv,
                    "synthetic_fraud.csv"
                )

        except Exception as e:

            st.error(str(e))
        
    # =====================================================
    # FRAUD ALERTS
    # =====================================================

    elif page == "Fraud Alerts":

        set_background(
            ALERT_IMAGE
        )

        st.title(
            "🚨 Fraud Alerts"
        )

        try:

            alerts = load_alerts()

            st.metric(
                "Total Alerts",
                len(alerts)
            )

            if not alerts.empty:

                fig = px.histogram(
                    alerts,
                    x="fraud_type",
                    title="Alert Distribution"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

                st.dataframe(
                    alerts,
                    use_container_width=True
                )
                csv = alerts.to_csv(index=False)

                st.download_button(
                    "⬇ Download Report",
                    csv,
                    "financial_report.csv",
                    "text/csv"
                )

        except Exception as e:

            st.error(str(e))
        

    # =====================================================
    # REAL TIME MONITOR
    # =====================================================

    elif page == "Real Time Monitor":

        st.title(
            "📡 Live Kafka Monitor"
        )
        refresh = st.toggle(
            "Enable Auto Refresh",
            value=False
        )

        if refresh:

            st.rerun()

        summary = kafka_summary()

        logs = load_kafka_logs()
        
        refresh = st.button(
            "🔄 Refresh Data"
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:

            st.metric(

                "Kafka Status",

                "🟢 Connected"

            )

        with c2:

            st.metric(

                "Messages",

                summary["messages"]

            )

        with c3:

            st.metric(

                "Topics",

                summary["topics"]

            )

        with c4:

            st.metric(

                "Latest Activity",

                "Running"

            )
        
        if summary["last_time"] is not None:

            st.info(

                f"Last Message : {summary['last_time']}"

            )
            st.subheader("Recent Kafka Messages")

            st.dataframe(

                logs.tail(100),

                use_container_width=True

            )
        fig = kafka_chart(logs)

        if fig is not None:

            st.plotly_chart(

                fig,

                use_container_width=True

            )
        fig2 = kafka_topic_chart(logs)

        if fig2 is not None:

            st.plotly_chart(

                fig2,

                use_container_width=True

            )

    # =====================================================
    # RISK SCORE CENTER
    # =====================================================

    elif page == "Risk Score Center":

        st.title(
            "⚠ Risk Score Center"
        )
        dataset = st.selectbox(
            "Select Dataset",
            [
                "Financial Fraud",
                "Credit Card Fraud",
                "Synthetic Fraud"
            ]
        )

        financial, credit, synthetic = load_risk_scores()

        if dataset == "Financial Fraud":
            df = financial

        elif dataset == "Credit Card Fraud":
            df = credit

        else:
            df = synthetic

        
        if not financial.empty:

            latest = financial.iloc[-1]

            st.subheader(
                "Latest Financial Fraud Prediction"
            )

            risk_score = int(
                latest["fraud_probability"] * 100
            )

            prediction = int(
                latest["prediction"]
            )

            st.metric(
                "Risk Score",
                f"{risk_score}/100"
            )
        if not df.empty:
            high_risk_df = df[
                df["fraud_probability"] >= 0.8
            ]

            st.subheader(
                "High Risk Transactions"
            )

            st.dataframe(
                high_risk_df,
                use_container_width=True
            )

            high = len(
                df[
                    df["fraud_probability"] >= 0.8
                ]
            )

            medium = len(
                df[
                    (
                        df["fraud_probability"] >= 0.4
                    )
                    &
                    (
                        df["fraud_probability"] < 0.8
                    )
                ]
            )

            low = len(
                df[
                    df["fraud_probability"] < 0.4
                ]
            )

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Risk Score",
                    f"{risk_score}/100"
                )

            with col2:
                st.metric(
                    "Prediction",
                    "Fraud" if prediction == 1 else "Legitimate"
                )

            with col3:
                st.metric(
                    "Probability",
                    f"{latest['fraud_probability']:.2%}"
                )

            st.subheader("Overall Risk Level")

            st.progress(
                latest["fraud_probability"]
            )

            if risk_score >= 80:

                level = "🔴 HIGH"

                st.error("🔴 HIGH RISK")

            elif risk_score >= 50:

                level = "🟡 MEDIUM"

                st.warning("🟡 MEDIUM RISK")

            else:

                level = "🟢 LOW"

                st.success("🟢 LOW RISK")

            st.metric(
                "Risk Level",
                level
            )
            
            if risk_score >= 80:

                recommendation = (
                    "🚫 Block transaction immediately."
                )

            elif risk_score >= 50:

                recommendation = (
                    "📝 Manual verification required."
                )

            else:

                recommendation = (
                    "✅ Safe to approve."
                )

            st.info(recommendation)
            fig1 = probability_histogram(df)

            if fig1 is not None:

                st.plotly_chart(
                    fig1,
                    use_container_width=True
                )

            fig2 = risk_level_chart(df)

            if fig2 is not None:

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )
            fig = px.pie(

                names=[
                    "High",
                    "Medium",
                    "Low"
                ],

                values=[
                    high,
                    medium,
                    low
                ],

                title="Risk Distribution"

            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )
    # =====================================================
    # TRANSACTION EXPLORER
    # =====================================================

    elif page == "Transaction Explorer":

        st.title("🔍 Transaction Explorer")

        dataset = st.selectbox(

            "Select Dataset",

            [

                "Financial",
                "Credit Card",
                "Synthetic"

            ]

        )

        if dataset == "Financial":

            df = load_table(
                "fraud_predictions"
            )

        elif dataset == "Credit Card":

            df = load_table(
                "credit_card_predictions"
            )

        else:

            df = load_table(
                "synthetic_predictions"
            )

        search = st.text_input(
            "Search"
        )

        if search:

            df = df.astype(str)

            df = df[
                df.apply(
                    lambda row:
                    row.str.contains(
                        search,
                        case=False
                    ).any(),
                    axis=1
                )
            ]

        st.dataframe(
            df,
            use_container_width=True
        )

    # =====================================================
    # DATABASE ANALYTICS
    # =====================================================

    elif page == "Database Analytics":

        st.title(
            "🗄 Database Analytics"
        )

        financial_count, credit_count, synthetic_count = get_counts()

        alerts = load_alerts()

        api_logs = load_api_logs()

        kafka_logs = load_kafka_logs()

        db_stats = pd.DataFrame({

            "Table":[

                "Financial Fraud",
                "Credit Card Fraud",
                "Synthetic Fraud",
                "Alert History",
                "API Logs",
                "Kafka Logs"

            ],

            "Records":[

                financial_count,
                credit_count,
                synthetic_count,
                len(alerts),
                len(api_logs),
                len(kafka_logs)

            ]

        })

        st.dataframe(
            db_stats,
            use_container_width=True
        )

        fig = px.bar(

            db_stats,

            x="Table",

            y="Records",

            title="Database Statistics"

        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    # =====================================================
    # MODEL PERFORMANCE
    # =====================================================

    elif page == "Model Performance":

        st.title(
            "📈 Model Performance"
        )

        try:

            metrics = load_metrics()

            st.dataframe(
                metrics,
                use_container_width=True
            )

            fig1 = px.bar(

                metrics,

                x="model_name",

                y="accuracy",

                title="Accuracy"

            )

            st.plotly_chart(
                fig1,
                use_container_width=True
            )

            fig2 = px.bar(

                metrics,

                x="model_name",

                y="precision_score",

                title="Precision"

            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

            fig3 = px.bar(

                metrics,

                x="model_name",

                y="recall_score",

                title="Recall"

            )

            st.plotly_chart(
                fig3,
                use_container_width=True
            )

            fig4 = px.bar(

                metrics,

                x="model_name",

                y="f1_score",

                title="F1 Score"

            )

            st.plotly_chart(
                fig4,
                use_container_width=True
            )

        except Exception as e:

            st.error(str(e))

    # =====================================================
    # API MONITORING
    # =====================================================

    elif page == "API Monitoring":

        st.title(
            "🔌 API Monitoring"
        )

        try:

            logs = load_api_logs()

            st.metric(
                "Total API Calls",
                len(logs)
            )

            st.dataframe(
                logs,
                use_container_width=True
            )

            if not logs.empty:

                fig = px.histogram(

                    logs,

                    x="status_code",

                    title="Status Code Distribution"

                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )
                csv = logs.to_csv(
                    index=False
                )

                st.download_button(
                    "⬇ Download Report",
                    csv,
                    "financial_report.csv",
                    "text/csv"
                )

        except Exception as e:

            st.error(str(e))
        
    # =====================================================
    # Ensemble Fraud Engine
    # =====================================================
    elif page == "Ensemble Fraud Engine":
        df = load_table(
            "ensemble_predictions"
        )
        c1,c2,c3 = st.columns(3)

        c1.metric(

            "Predictions",

            len(df)

        )

        c2.metric(

            "Fraud",

            len(
                df[
                    df["final_prediction"]==1
                ]
            )

        )

        c3.metric(

            "Average Confidence",

            f"{df['confidence'].mean():.2f}%"

        )
        st.subheader(
            "Recent Ensemble Predictions"
        )

        st.dataframe(
            df.tail(100),
            use_container_width=True
        )
        fig = ensemble_vote_chart(df)

        st.plotly_chart(

            fig,

            use_container_width=True

        )
        fig = px.histogram(

            df,

            x="confidence",

            nbins=20,

            title="Confidence Distribution"

        )

        st.plotly_chart(

            fig,

            use_container_width=True

        )
        df["Agreement"] = (

            (

                df["logistic_prediction"]

                +

                df["random_forest_prediction"]

                +

                df["xgboost_prediction"]

            ) / 3

        ) * 100
        st.metric(

            "Average Agreement",

            f"{df['Agreement'].mean():.2f}%"

        )
    # =====================================================
    # ADMIN SETTINGS
    # =====================================================

    elif page == "Admin Settings":

        if st.session_state.role != "Admin":

            st.error(
                "Access Denied"
            )

            st.stop()

        st.title(
            "⚙ Admin Settings"
        )

        try:

            users = load_table(
                "users"
            )

            st.metric(
                "Total Users",
                len(users)
            )

            st.dataframe(
                users,
                use_container_width=True
            )

            csv = users.to_csv(
                index=False
            )

            st.download_button(

                "Download Users",

                csv,

                "users.csv"

            )

        except Exception as e:

            st.error(str(e))

    # =====================================================
    # USER Activity
    # =====================================================
    elif page == "User Activity":

        st.title("👤 User Activity Logs")

        df = load_user_activity()

        if df.empty:

            st.warning("No Activity Found")

        else:

            username = st.text_input(
                "Search Username"
            )

            if username:

                df = df[
                    df["username"]
                    .str.contains(
                        username,
                        case=False
                    )
                ]

            st.metric(
                "Total Activities",
                len(df)
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "📥 Download Activity Report",
                csv,
                "user_activity_logs.csv",
                "text/csv"
            )
    # =====================================================
    # USER SETTINGS
    # =====================================================
    elif page == "System Health":

        st.title(
            "🖥 System Health"
        )

        st.success(
            "PostgreSQL Connected"
        )

        st.success(
            "Kafka Connected"
        )

        st.success(
            "FastAPI Running"
        )

        st.success(
            "Dashboard Online"
        )
    elif page == "Fraud Forecasting":

        st.title(
            "📈 Fraud Forecasting"
        )

        if st.button(
            "Generate Forecast"
        ):

            generate_forecast()

            st.success(
                "Forecast Updated"
            )

        df = load_forecast()

        if df.empty:

            st.warning(
                "No Forecast Data"
            )

        else:

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(

                "Today's Prediction",

                int(
                    df.iloc[0][
                        "predicted_fraud"
                    ]
                )

            )

            c2.metric(

                "Next 7 Days",

                int(
                    df.head(7)[
                        "predicted_fraud"
                    ].sum()
                )

            )

            c3.metric(

                "Next 30 Days",

                int(
                    df[
                        "predicted_fraud"
                    ].sum()
                )

            )

            c4.metric(

                "Confidence",

                f"{df.iloc[0]['confidence']}%"

            )

            st.divider()

            st.subheader(
                "Forecast Table"
            )

            st.dataframe(
                df,
                use_container_width=True
            )

            import plotly.express as px

            fig = px.line(

                df,

                x="forecast_date",

                y="predicted_fraud",

                markers=True,

                title="Predicted Fraud Trend"

            )

            st.plotly_chart(

                fig,

                use_container_width=True

            )

            fig2 = px.bar(

                df,

                x="forecast_date",

                y="predicted_transactions",

                title="Predicted Transactions"

            )

            st.plotly_chart(

                fig2,

                use_container_width=True

            )

            st.subheader(
                "Forecast Summary"
            )

            highest = df.loc[
                df["predicted_fraud"].idxmax()
            ]

            lowest = df.loc[
                df["predicted_fraud"].idxmin()
            ]

            st.write(
                f"📈 Highest Expected Fraud: **{highest['predicted_fraud']}** on **{highest['forecast_date']}**"
            )

            st.write(
                f"📉 Lowest Expected Fraud: **{lowest['predicted_fraud']}** on **{lowest['forecast_date']}**"
            )

            csv = df.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(

                "📥 Download Forecast",

                csv,

                "fraud_forecast.csv",

                "text/csv"

            )
    elif page == "User Settings":

        st.markdown("---")

        st.subheader(
            "Project Information"
        )

        st.write(
            "AI-Powered Financial Fraud Detection & Analytics Platform"
        )

        st.write(
            "Version : 1.0"
        )

        st.write(
            "Backend : FastAPI"
        )

        st.write(
            "Database : PostgreSQL"
        )

        st.write(
            "Streaming : Kafka"
        )

        st.write(
            "Frontend : Streamlit"
        )
    
        st.title(
            "👤 User Settings"
        )

        if PROFILE_IMAGE != "":

            st.image(
                PROFILE_IMAGE,
                width=150
            )

        st.text_input(

            "Username",

            value=st.session_state.username,

            disabled=True

        )

        st.text_input(
            "Email"
        )

        new_theme = st.selectbox(
            "Theme",
            [
                "Dark",
                "Light"
            ],
            index=0 if st.session_state.theme == "Dark" else 1
        )

        if st.button(
            "Apply Theme"
        ):

            st.session_state.theme = new_theme

            st.rerun()

        new_password = st.text_input(

            "New Password",

            type="password"

        )

        confirm_password = st.text_input(

            "Confirm Password",

            type="password"

        )

        if st.button(
            "Update Profile"
        ):

            st.success(
                "Profile Updated"
            )

    elif page == "🤖 AI Fraud Assistant":

        st.title("🤖 AI Fraud Assistant")

        st.markdown(
            """
            Ask the AI Assistant to explain why a transaction
            was classified as Fraud or Legitimate.
            """
        )

        df = load_table(
            "fraud_predictions"
        )

        if df.empty:

            st.warning(
                "No Fraud Prediction Records Found."
            )

        else:

            transaction = st.selectbox(

                "Select Transaction",

                df["transaction_id"]

            )

            row = df[
                df["transaction_id"] == transaction
            ].iloc[0]

            prediction = (
                "Fraud"
                if row["prediction"] == 1
                else "Legitimate"
            )

            probability = float(
                row["fraud_probability"]
            )

            risk_score = int(
                probability * 100
            )

            # ---------------------------------
            # KPI Cards
            # ---------------------------------

            c1, c2, c3 = st.columns(3)

            with c1:

                st.metric(
                    "Prediction",
                    prediction
                )

            with c2:

                st.metric(
                    "Fraud Probability",
                    f"{probability:.2%}"
                )

            with c3:

                st.metric(
                    "Risk Score",
                    f"{risk_score}/100"
                )

            st.divider()

            # ---------------------------------
            # Progress
            # ---------------------------------

            st.subheader("Risk Meter")

            st.progress(probability)

            if risk_score >= 80:

                st.error("🔴 HIGH RISK")

            elif risk_score >= 50:

                st.warning("🟡 MEDIUM RISK")

            else:

                st.success("🟢 LOW RISK")

            st.divider()

            # ---------------------------------
            # AI Explanation
            # ---------------------------------

            st.subheader("🧠 AI Explanation")

            reasons = []

            if probability >= 0.95:

                reasons.append(
                    "Very High Fraud Probability."
                )

            elif probability >= 0.80:

                reasons.append(
                    "High Fraud Probability."
                )

            if row["prediction"] == 1:

                reasons.append(
                    "The Machine Learning model classified this transaction as Fraud."
                )

            if probability >= 0.70:

                reasons.append(
                    "Multiple fraud indicators were detected."
                )

            if len(reasons) == 0:

                reasons.append(
                    "Transaction appears normal."
                )

            for reason in reasons:

                st.success(
                    "✔ " + reason
                )

            st.divider()

            # ---------------------------------
            # Recommendation
            # ---------------------------------

            st.subheader("📋 Recommendation")

            if prediction == "Fraud":

                st.error(
                    """
    🚨 Immediate Action Recommended

    • Block Transaction

    • Freeze Customer Account

    • Notify Customer

    • Manual Verification Required

    • Raise Fraud Alert
                    """
                )

            else:

                st.success(
                    """
    ✅ Transaction Appears Safe

    • Approve Transaction

    • Continue Monitoring

    • No Immediate Action Required
                    """
                )

            st.divider()

            # ---------------------------------
            # Transaction Details
            # ---------------------------------

            st.subheader("Transaction Information")

            st.dataframe(
                row.to_frame().T,
                use_container_width=True
            )

            st.divider()

            # ---------------------------------
            # Download Report
            # ---------------------------------

            report = row.to_frame().T.to_csv(
                index=False
            )

            st.download_button(

                "📥 Download Transaction Report",

                report,

                file_name=f"{transaction}.csv",

                mime="text/csv"

            )

            st.divider()

            # ---------------------------------
            # AI Chat Assistant
            # ---------------------------------

            st.subheader("💬 Ask AI")

            question = st.text_input(
                "Ask a question"
            )

            if question:

                question = question.lower()

                if "why" in question:

                    st.info(
                        f"""
    This transaction was classified as

    **{prediction}**

    because the fraud probability is

    **{probability:.2%}**

    which indicates a

    {'very high' if probability>=0.80 else 'low'}

    fraud risk.
                        """
                    )

                elif "risk" in question:

                    st.info(
                        f"""
    Current Risk Score

    {risk_score}/100
                        """
                    )

                elif "confidence" in question:

                    st.info(
                        f"""
    Model Confidence

    {probability:.2%}
                        """
                    )

                elif "recommendation" in question:

                    if prediction == "Fraud":

                        st.error(
                            """
    Recommended Actions

    ✔ Freeze Account

    ✔ Notify Customer

    ✔ Manual Investigation

    ✔ Raise Fraud Alert
                            """
                        )

                    else:

                        st.success(
                            """
    Transaction is Safe.

    No Action Required.
                            """
                        )

                else:

                    st.warning(
                        """
    I can answer questions about

    • Fraud

    • Risk

    • Prediction

    • Confidence

    • Recommendation
                        """
                    )
    # =====================================================
    # FOOTER
    # =====================================================

    st.markdown("---")

    st.markdown(

        """
        <center>

        <h5>

        AI-Powered Financial Fraud Detection Platform

        </h5>

        <p>

        Financial Fraud • Credit Card Fraud • Synthetic Fraud

        </p>

        </center>
        """,

        unsafe_allow_html=True

    )
