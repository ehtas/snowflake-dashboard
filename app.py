import streamlit as st
import pandas as pd
import os
from config import SNOWFLAKE_CONFIG
from firebase_helper import login_user, signup_user
import snowflake.connector
from io import BytesIO
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config("📊 Smart Data Insights", layout="wide")
# ----------------------------- Auth Logic -----------------------------
if "user" not in st.session_state:
    st.session_state["user"] = None

def login_ui():
    st.title("🔐 Login to Upload Data")

    auth_mode = st.radio("Choose mode", ["Login", "Sign Up"], horizontal=True)

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login" if auth_mode == "Login" else "Sign Up"):
        if auth_mode == "Login":
            user = login_user(email, password)
        else:
            user = signup_user(email, password)
        
        if user:
            st.session_state.user = user
            st.success(f"✅ {'Logged in' if auth_mode == 'Login' else 'Signed up'} successfully!")
            st.rerun()
        else:
            st.error("❌ Login failed. Check credentials or sign up.")

if not st.session_state["user"]:
    login_ui()
    st.stop()
st.title("📤 Upload Any Dataset for Insightful Analysis")

uploaded_file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if uploaded_file:
    try:
        # Read file
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        # Clean column names
        df.columns = [str(col).strip().lower().replace(" ", "_") for col in df.columns]

        st.subheader("📄 Preview")
        st.dataframe(df.head(100))

        # Type detection
        numeric_cols = df.select_dtypes(include=["int", "float"]).columns.tolist()
        categorical_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()
        datetime_cols = df.select_dtypes(include=["datetime64"]).columns.tolist()

        # Try to infer datetime if not already parsed
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = pd.to_datetime(df[col])
                    datetime_cols.append(col)
                    categorical_cols.remove(col)
                except:
                    pass

        st.markdown("---")
        st.header("📈 Column Summary")

        # Numeric summary
        if numeric_cols:
            st.subheader("🔢 Numeric Columns Summary")
            st.dataframe(df[numeric_cols].describe().T)

        # Categorical summary
        if categorical_cols:
            st.subheader("🔤 Categorical Columns Overview")
            for col in categorical_cols:
                st.markdown(f"**{col}** — top 5 values")
                st.write(df[col].value_counts().head())

        # Date summary
        if datetime_cols:
            st.subheader("📅 Date Columns")
            for col in datetime_cols:
                st.markdown(f"**{col}**")
                st.write(f"Date range: {df[col].min()} → {df[col].max()}")
                st.line_chart(df.set_index(col).resample("D").size())

        st.markdown("---")
        st.header("📊 Smart Visualizations")

        # Histogram for numeric
        if numeric_cols:
            num_col = st.selectbox("📈 Select numeric column for distribution", numeric_cols)
            fig, ax = plt.subplots()
            sns.histplot(df[num_col], kde=True, ax=ax)
            st.pyplot(fig)

        # Bar chart for categorical
        if categorical_cols:
            cat_col = st.selectbox("📊 Select categorical column for frequency", categorical_cols)
            st.bar_chart(df[cat_col].value_counts().head(10))

        # Line chart for time series
        if datetime_cols and numeric_cols:
            time_col = datetime_cols[0]
            num_col = numeric_cols[0]
            df_time = df[[time_col, num_col]].dropna()
            df_time = df_time.groupby(df_time[time_col].dt.date)[num_col].mean()
            st.line_chart(df_time)

    except Exception as e:
        st.error(f"❌ Error processing file: {e}")
