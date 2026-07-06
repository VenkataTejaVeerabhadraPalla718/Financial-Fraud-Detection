import streamlit as st


def go_home():
    st.session_state.page = "Home"
    st.rerun()


def show_settings():

    st.markdown(
        """
        <style>

        .settings-banner {
            padding: 28px;
            border-radius: 20px;
            margin-bottom: 22px;
            background: linear-gradient(
                135deg,
                rgba(35, 45, 70, 0.96),
                rgba(70, 105, 165, 0.82)
            );
            color: white;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.22);
        }

        .settings-title {
            font-size: 34px;
            font-weight: 800;
            margin-bottom: 6px;
        }

        .settings-subtitle {
            font-size: 16px;
            opacity: 0.90;
        }

        .section-heading {
            font-size: 24px;
            font-weight: 750;
            margin-top: 25px;
            margin-bottom: 14px;
        }

        .settings-note {
            padding: 18px;
            border-radius: 14px;
            margin-top: 18px;
            background: rgba(70, 105, 165, 0.14);
            border-left: 5px solid #4669a5;
        }

        </style>
        """,
        unsafe_allow_html=True
    )

    if st.button("← Home", key="settings_home"):
        go_home()

    st.markdown(
        """
        <div class="settings-banner">
            <div class="settings-title">⚙️ Platform Settings</div>
            <div class="settings-subtitle">
                Configure dashboard preferences, alert behavior,
                and AI assistant options.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Default values are created only once.
    defaults = {
        "dashboard_theme": "Professional Blue",
        "auto_refresh": False,
        "show_animations": True,
        "email_alerts": False,
        "high_risk_alerts": True,
        "risk_threshold": 70,
        "save_chat": True,
        "show_tooltips": True
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    st.markdown(
        '<div class="section-heading">🎨 Dashboard Preferences</div>',
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:
        theme = st.selectbox(
            "Dashboard Theme",
            [
                "Professional Blue",
                "Dark Mode",
                "Light Mode"
            ],
            index=[
                "Professional Blue",
                "Dark Mode",
                "Light Mode"
            ].index(st.session_state.dashboard_theme)
        )

        show_animations = st.toggle(
            "Enable UI Animations",
            value=st.session_state.show_animations
        )

    with col2:
        auto_refresh = st.toggle(
            "Enable Dashboard Auto Refresh",
            value=st.session_state.auto_refresh
        )

        show_tooltips = st.toggle(
            "Show Dashboard Help Tooltips",
            value=st.session_state.show_tooltips
        )

    st.markdown(
        '<div class="section-heading">🚨 Fraud Alert Preferences</div>',
        unsafe_allow_html=True
    )

    alert_col1, alert_col2 = st.columns(2)

    with alert_col1:
        email_alerts = st.toggle(
            "Enable Email Fraud Alerts",
            value=st.session_state.email_alerts
        )

        high_risk_alerts = st.toggle(
            "Enable High-Risk Transaction Alerts",
            value=st.session_state.high_risk_alerts
        )

    with alert_col2:
        risk_threshold = st.slider(
            "High-Risk Alert Threshold",
            min_value=50,
            max_value=100,
            value=int(st.session_state.risk_threshold),
            step=5,
            help="Transactions with a risk score above this value can be treated as high risk."
        )

        st.info(
            f"Transactions with risk score **{risk_threshold}/100 or above** "
            f"will be considered high risk."
        )

    st.markdown(
        '<div class="section-heading">🤖 AI Assistant Preferences</div>',
        unsafe_allow_html=True
    )

    save_chat = st.toggle(
        "Save AI Assistant Chat History",
        value=st.session_state.save_chat
    )

    st.markdown(
        '<div class="section-heading">💾 Save Changes</div>',
        unsafe_allow_html=True
    )

    if st.button(
        "💾 Save Platform Settings",
        key="save_platform_settings",
        use_container_width=True
    ):
        st.session_state.dashboard_theme = theme
        st.session_state.auto_refresh = auto_refresh
        st.session_state.show_animations = show_animations
        st.session_state.show_tooltips = show_tooltips
        st.session_state.email_alerts = email_alerts
        st.session_state.high_risk_alerts = high_risk_alerts
        st.session_state.risk_threshold = risk_threshold
        st.session_state.save_chat = save_chat

        st.success("Settings saved successfully for this session.")

    st.markdown(
        '<div class="section-heading">ℹ️ Platform Information</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="settings-note">
            <b>AI-Powered Financial Fraud Detection Platform</b><br><br>
            Built using Python, Streamlit, Machine Learning, PostgreSQL,
            Kafka, FastAPI, Plotly, and SHAP Explainable AI.<br><br>
            These settings are currently stored only while the Streamlit
            session is active. Later, they can be stored permanently in
            PostgreSQL for each user account.
        </div>
        """,
        unsafe_allow_html=True
    )