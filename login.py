import pyrebase
import streamlit as st

firebase_config = st.secrets["firebase"]
firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

def login_user(email, password):
    try:
        user = auth.sign_in_with_email_and_password(email, password)
        st.session_state["user"] = user
        return True
    except Exception as e:
        st.error("Login failed. Check credentials.")
        return False

def logout_user():
    st.session_state.pop("user", None)

def is_logged_in():
    return "user" in st.session_state
