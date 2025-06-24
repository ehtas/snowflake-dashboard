import streamlit as st
import snowflake.connector
import pandas as pd
import os

from io import BytesIO

# Load Snowflake config from secrets
sf_config = st.secrets["snowflake"]

def create_connection():
    return snowflake.connector.connect(
        user=sf_config["user"],
        password=sf_config["password"],
        account=sf_config["account"],
        warehouse=sf_config["warehouse"],
        database=sf_config["database"],
        schema=sf_config["schema"],
        role=sf_config.get("role", None)
    )

def infer_column_types(df):
    type_map = {
        "int64": "INT",
        "float64": "FLOAT",
        "object": "STRING",
        "datetime64[ns]": "TIMESTAMP",
        "bool": "BOOLEAN"
    }
    return [f'"{col}" {type_map[str(dtype)]}' for col, dtype in zip(df.columns, df.dtypes)]

def upload_and_ingest(file, file_type):
    # Load file into DataFrame
    if file_type == "csv":
        df = pd.read_csv(file)
    else:
        df = pd.read_excel(file)

    st.write("✅ File preview:")
    st.dataframe(df.head())

    # Connect to Snowflake
    conn = create_connection()
    cs = conn.cursor()

    try:
        table_name = "DYNAMIC_UPLOAD_TABLE"

        # Build CREATE TABLE statement
        column_defs = ", ".join(infer_column_types(df))
        create_table_sql = f'CREATE OR REPLACE TABLE {table_name} ({column_defs})'
        cs.execute(create_table_sql)

        # Save to temporary CSV for upload
        temp_file_path = "temp_uploaded.csv"
        df.to_csv(temp_file_path, index=False)

        # Upload to stage
        put_command = f"PUT file://{os.path.abspath(temp_file_path)} @%{table_name} AUTO_COMPRESS=TRUE"
        cs.execute(put_command)

        # Ingest using COPY INTO
        copy_command = f"""
        COPY INTO {table_name}
        FROM @%{table_name}
        FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1 FIELD_OPTIONALLY_ENCLOSED_BY = '"')
        ON_ERROR = 'CONTINUE'
        """
        cs.execute(copy_command)

        st.success("🎉 File uploaded and ingested into Snowflake successfully!")

        # Show dashboard
        show_dashboard(df, table_name)

    except Exception as e:
        st.error(f"❌ Error during ingestion: {e}")
    finally:
        cs.close()
        conn.close()
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

def show_dashboard(df, table_name):
    st.subheader("📊 Dashboard")
    if 'date' in df.columns.str.lower().tolist():
        try:
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
            date_col = 'date'
        except:
            date_col = None
    else:
        date_col = None

    st.metric("Total Rows", df.shape[0])
    st.metric("Total Columns", df.shape[1])

    # Show column-wise summary
    st.write("🧾 Summary:")
    st.dataframe(df.describe(include='all'))

    # If numeric columns, show chart
    numeric_cols = df.select_dtypes(include='number').columns
    if len(numeric_cols) >= 1:
        st.subheader("📈 Sample Chart")
        st.bar_chart(df[numeric_cols].head(20))

st.title("🧠 Smart Snowflake Uploader + Dashboard")
file = st.file_uploader("Upload CSV or Excel file", type=["csv", "xlsx"])

if file:
    file_type = "csv" if file.name.endswith(".csv") else "excel"
    upload_and_ingest(file, file_type)
