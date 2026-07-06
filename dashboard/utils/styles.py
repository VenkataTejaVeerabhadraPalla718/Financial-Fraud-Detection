import streamlit as st

theme = st.sidebar.selectbox(
    "Theme",
    ["Dark","Light"]
)

def load_styles():


    st.markdown(
        """
        <style>

        .stApp {
            background-color: #0f172a;
        }

        section[data-testid="stSidebar"] {
            background-color: #111827;
        }

        .kpi-card {

            background: linear-gradient(
                135deg,
                #1e293b,
                #0f172a
            );

            padding: 20px;

            border-radius: 15px;

            color: white;

            text-align: center;

            box-shadow:
                0px 4px 15px rgba(
                    0,
                    0,
                    0,
                    0.5
                );
        }

        .title {

            color: white;

            text-align: center;

            font-size: 42px;

            font-weight: bold;

        }

        .subtitle {

            color: #94a3b8;

            text-align: center;

        }

        </style>
        """,
        unsafe_allow_html=True
    )
