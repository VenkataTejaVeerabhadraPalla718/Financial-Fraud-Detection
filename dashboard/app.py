import streamlit as st


# ==========================================================
# PAGE CONFIGURATION
# Must be the first Streamlit command.
# ==========================================================

st.set_page_config(
    page_title="Financial Fraud Detection Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ==========================================================
# SAFE PAGE IMPORTS
# ==========================================================

PAGE_IMPORT_ERRORS = {}


def safe_import(module_name, function_name):
    """
    Import a page function safely.
    If a file/function has an issue, the main dashboard still runs.
    """
    try:
        module = __import__(
            module_name,
            fromlist=[function_name]
        )
        return getattr(module, function_name)

    except Exception as error:
        PAGE_IMPORT_ERRORS[module_name] = str(error)
        return None


show_fraud_alerts = safe_import(
    "modules.fraud_alerts",
    "show_fraud_alerts"
)

show_risk_center = safe_import(
    "modules.risk_center",
    "show_risk_center"
)

show_transaction_explorer = safe_import(
    "modules.transaction_explorer",
    "show_transaction_explorer"
)

show_database_analytics = safe_import(
    "modules.database_analytics",
    "show_database_analytics"
)

show_model_performance = safe_import(
    "modules.model_performance",
    "show_model_performance"
)

show_ensemble_engine = safe_import(
    "modules.ensemble_engine",
    "show_ensemble_engine"
)

show_ai_assistant = safe_import(
    "modules.ai_assistant",
    "show_ai_assistant"
)

show_reports = safe_import(
    "modules.reports",
    "show_reports"
)

show_financial_fraud = safe_import(
    "modules.financial_fraud",
    "show_financial_fraud"
)

show_credit_card_fraud = safe_import(
    "modules.credit_card",
    "show_credit_card"
)

show_synthetic_fraud = safe_import(
    "modules.synthetic",
    "show_synthetic"
)

show_kafka_monitor = safe_import(
    "modules.realtime_monitor",
    "show_realtime_monitor"
)

show_settings = safe_import(
    "modules.settings",
    "show_settings"
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "page" not in st.session_state:
    st.session_state.page = "Home"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = True


# ==========================================================
# GLOBAL CSS
# ==========================================================

st.markdown(
    """
    <style>

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1450px;
    }

    .main-title {
        text-align: center;
        font-size: 42px;
        font-weight: 850;
        margin-bottom: 8px;
        color: #ffffff;
    }

    .main-subtitle {
        text-align: center;
        font-size: 18px;
        margin-bottom: 10px;
        color: rgba(255, 255, 255, 0.82);
    }

    .home-banner {
        padding: 42px 30px;
        border-radius: 24px;
        margin-bottom: 30px;
        background: linear-gradient(
            135deg,
            #002b5c,
            #0059b3,
            #0078d4
        );
        box-shadow: 0px 10px 28px rgba(0, 0, 0, 0.22);
    }

    .section-title {
        font-size: 27px;
        font-weight: 800;
        margin-top: 28px;
        margin-bottom: 16px;
    }

    /* Only dashboard menu buttons use this large style */
    div[data-testid="stButton"] > button[kind="secondary"] {
        border-radius: 14px;
        font-weight: 700;
    }

    .dashboard-menu-button div[data-testid="stButton"] > button {
        width: 100%;
        min-height: 145px;
        border-radius: 16px;
        font-size: 17px;
        font-weight: 700;
        border: 1px solid rgba(255, 255, 255, 0.18);
        background: rgba(255, 255, 255, 0.08);
        color: white;
        transition: 0.25s;
        box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.12);
    }

    .dashboard-menu-button div[data-testid="stButton"] > button:hover {
        transform: translateY(-5px);
        border: 1px solid #4da3ff;
        background: rgba(0, 89, 179, 0.85);
        box-shadow: 0px 10px 24px rgba(0, 0, 0, 0.24);
    }

    .footer-text {
        text-align: center;
        opacity: 0.72;
        margin-top: 35px;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# NAVIGATION HELPERS
# ==========================================================

def open_page(page_name):
    st.session_state.page = page_name
    st.rerun()


def render_menu_button(label, key, page_name):
    """
    Creates one dashboard card-style button.
    """
    st.markdown(
        '<div class="dashboard-menu-button">',
        unsafe_allow_html=True
    )

    clicked = st.button(
        label,
        key=key,
        use_container_width=True
    )

    st.markdown(
        "</div>",
        unsafe_allow_html=True
    )

    if clicked:
        open_page(page_name)


def show_missing_page(page_title, module_name):
    """
    Shows an understandable error instead of stopping the complete dashboard.
    """
    st.error(
        f"Unable to open **{page_title}**."
    )

    error_message = PAGE_IMPORT_ERRORS.get(
        module_name,
        "The page file or required function is missing."
    )

    st.code(error_message)

    if st.button("← Back to Home", key=f"back_{page_title}"):
        open_page("Home")


def run_page(page_function, page_title, module_name):
    """
    Runs the selected page safely.
    """
    if page_function is None:
        show_missing_page(
            page_title,
            module_name
        )
        return

    try:
        page_function()

    except Exception as error:
        st.error(
            f"An error occurred while opening **{page_title}**."
        )

        st.exception(error)

        if st.button(
            "← Back to Home",
            key=f"error_back_{page_title}"
        ):
            open_page("Home")


# ==========================================================
# HOME PAGE
# ==========================================================

def show_home():

    st.markdown(
        """
        <div class="home-banner">
            <div class="main-title">
                🛡️ AI-Powered Financial Fraud Detection Platform
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-title">🔍 Fraud Detection Modules</div>',
        unsafe_allow_html=True
    )

    row1_col1, row1_col2, row1_col3 = st.columns(3)

    with row1_col1:
        render_menu_button(
            "💰\nFinancial Fraud Detection",
            "financial_fraud",
            "Financial Fraud Detection"
        )

    with row1_col2:
        render_menu_button(
            "💳\nCredit Card Fraud Detection",
            "credit_card_fraud",
            "Credit Card Fraud Detection"
        )

    with row1_col3:
        render_menu_button(
            "🏦\nSynthetic Fraud Detection",
            "synthetic_fraud",
            "Synthetic Fraud Detection"
        )

    st.markdown(
        '<div class="section-title">📊 Intelligence and Monitoring</div>',
        unsafe_allow_html=True
    )

    row2_col1, row2_col2, row2_col3 = st.columns(3)

    with row2_col1:
        render_menu_button(
            "🚨\nFraud Alerts Center",
            "fraud_alerts",
            "Fraud Alerts"
        )

    with row2_col2:
        render_menu_button(
            "⚠️\nRisk Score Center",
            "risk_center",
            "Risk Score Center"
        )

    with row2_col3:
        render_menu_button(
            "📡\nReal-Time Kafka Monitor",
            "kafka_monitor",
            "Kafka Monitor"
        )

    row3_col1, row3_col2, row3_col3 = st.columns(3)

    with row3_col1:
        render_menu_button(
            "🔍\nTransaction Explorer",
            "transaction_explorer",
            "Transaction Explorer"
        )

    with row3_col2:
        render_menu_button(
            "🔬\nEnsemble Fraud Engine",
            "ensemble_engine",
            "Ensemble Fraud Engine"
        )

    with row3_col3:
        render_menu_button(
            "🤖\nAI Fraud Assistant",
            "ai_assistant",
            "AI Assistant"
        )

    st.markdown(
        '<div class="section-title">🗄️ Analytics, Reports and Settings</div>',
        unsafe_allow_html=True
    )

    row4_col1, row4_col2, row4_col3 = st.columns(3)

    with row4_col1:
        render_menu_button(
            "📈\nModel Performance Center",
            "model_performance",
            "Model Performance"
        )

    with row4_col2:
        render_menu_button(
            "🗄️\nDatabase Analytics",
            "database_analytics",
            "Database Analytics"
        )

    with row4_col3:
        render_menu_button(
            "📄\nFraud Intelligence Reports",
            "reports",
            "Reports"
        )

    row5_col1, row5_col2, row5_col3 = st.columns(3)

    with row5_col1:
        render_menu_button(
            "⚙️\nSettings",
            "settings",
            "Settings"
        )

    with row5_col2:
        render_menu_button(
            "🏠\nRefresh Dashboard",
            "refresh_home",
            "Home"
        )

    with row5_col3:
        st.markdown(
            '<div class="dashboard-menu-button">',
            unsafe_allow_html=True
        )

        logout_clicked = st.button(
            "🚪\nLogout",
            key="logout",
            use_container_width=True
        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        if logout_clicked:
            st.session_state.logged_in = False
            st.session_state.page = "Home"
            st.rerun()

    st.markdown(
        """
        <div class="footer-text">
            AI-Powered Financial Fraud Detection and Analytics Platform<br>
            Built using Streamlit, Machine Learning, PostgreSQL, Kafka,
            FastAPI and SHAP Explainable AI.
        </div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# LOGOUT PAGE
# ==========================================================

def show_logout_page():

    st.markdown(
        """
        <div class="home-banner">
            <div class="main-title">
                👋 You Have Logged Out
            </div>

            
        </div>
        """,
        unsafe_allow_html=True
    )

    _, middle_column, _ = st.columns([1, 1, 1])

    with middle_column:
        if st.button(
            "🔐 Login Again",
            key="login_again",
            use_container_width=True
        ):
            st.session_state.logged_in = True
            st.session_state.page = "Home"
            st.rerun()


# ==========================================================
# PAGE ROUTING
# ==========================================================

if not st.session_state.logged_in:
    show_logout_page()

elif st.session_state.page == "Home":
    show_home()

elif st.session_state.page == "Financial Fraud Detection":
    run_page(
        show_financial_fraud,
        "Financial Fraud Detection",
        "modules.financial_fraud"
    )

elif st.session_state.page == "Credit Card Fraud Detection":
    run_page(
        show_credit_card_fraud,
        "Credit Card Fraud Detection",
        "modules.credit_card"
    )

elif st.session_state.page == "Synthetic Fraud Detection":
    run_page(
        show_synthetic_fraud,
        "Synthetic Fraud Detection",
        "modules.synthetic"
    )

elif st.session_state.page == "Fraud Alerts":
    run_page(
        show_fraud_alerts,
        "Fraud Alerts Center",
        "modules.fraud_alerts"
    )

elif st.session_state.page == "Risk Score Center":
    run_page(
        show_risk_center,
        "Risk Score Center",
        "modules.risk_center"
    )

elif st.session_state.page == "Kafka Monitor":
    run_page(
        show_kafka_monitor,
        "Real-Time Kafka Monitor",
        "modules.realtime_monitor"
    )

elif st.session_state.page == "Transaction Explorer":
    run_page(
        show_transaction_explorer,
        "Transaction Explorer",
        "modules.transaction_explorer"
    )

elif st.session_state.page == "Ensemble Fraud Engine":
    run_page(
        show_ensemble_engine,
        "Ensemble Fraud Engine",
        "modules.ensemble_engine"
    )

elif st.session_state.page == "AI Assistant":
    run_page(
        show_ai_assistant,
        "AI Fraud Assistant",
        "modules.ai_assistant"
    )

elif st.session_state.page == "Model Performance":
    run_page(
        show_model_performance,
        "Model Performance Center",
        "modules.model_performance"
    )

elif st.session_state.page == "Database Analytics":
    run_page(
        show_database_analytics,
        "Database Analytics",
        "modules.database_analytics"
    )

elif st.session_state.page == "Reports":
    run_page(
        show_reports,
        "Fraud Intelligence Reports",
        "modules.reports"
    )

elif st.session_state.page == "Settings":
    run_page(
        show_settings,
        "Settings",
        "modules.settings"
    )

else:
    st.session_state.page = "Home"
    st.rerun()