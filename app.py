import streamlit as st
import snowflake.connector
import pandas as pd
import os

# Load config from Streamlit secrets
sf_config = st.secrets["snowflake"]

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=sf_config["user"],
    password=sf_config["password"],
    account=sf_config["account"],
    warehouse=sf_config["warehouse"],
    database=sf_config["database"],
    schema=sf_config["schema"],
    role=sf_config.get("role", None)
)

st.title("📤 Upload Sales File to Snowflake")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    # Use original file name
    temp_file_path = uploaded_file.name
    with open(temp_file_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    cs = conn.cursor()

    try:
        # Upload to internal stage
        put_command = f"PUT file://{os.path.abspath(temp_file_path)} @sales_stage_v1 AUTO_COMPRESS=TRUE"
        cs.execute(put_command)
        st.success("✅ File uploaded to Snowflake internal stage!")

        # Ingest into table
        gzip_name = uploaded_file.name + ".gz"
        copy_command = f"""
        COPY INTO RAW.SALES_RAW
        FROM @sales_stage_v1
        FILE_FORMAT = (TYPE = 'CSV' SKIP_HEADER = 1)
        PATTERN = '.*{gzip_name}';
        """
        cs.execute(copy_command)
        st.success("✅ Data ingested into RAW.SALES_RAW!")

        # Preview data
        preview_query = "SELECT * FROM RAW.SALES_RAW LIMIT 100"
        df = pd.read_sql(preview_query, conn)
        df.columns = [col.lower() for col in df.columns]

        st.subheader("👀 Data Preview")
        st.dataframe(df)

        st.markdown("---")
        st.subheader("📊 Sales Dashboard")

        # Convert order_date
        df['order_date'] = pd.to_datetime(df['order_date'], errors='coerce')

        # Date range filter
        min_date, max_date = df['order_date'].min(), df['order_date'].max()
        date_range = st.date_input("Select Order Date Range", [min_date, max_date])

        # Filter data
        filtered_df = df[
            (df['order_date'].dt.date >= date_range[0]) &
            (df['order_date'].dt.date <= date_range[1])
        ]

        # Revenue calculation
        filtered_df['revenue'] = filtered_df['quantity'] * filtered_df['price']

        # KPIs
        total_orders = filtered_df.shape[0]
        total_quantity = filtered_df['quantity'].sum()
        total_revenue = filtered_df['revenue'].sum()

        col1, col2, col3 = st.columns(3)
        col1.metric("🧾 Total Orders", total_orders)
        col2.metric("📦 Quantity Sold", int(total_quantity))
        col3.metric("💰 Total Revenue", f"${total_revenue:,.2f}")

        # Bar chart
        st.subheader("💹 Revenue by Product")
        product_revenue = filtered_df.groupby("product_id")["revenue"].sum().sort_values(ascending=False)
        st.bar_chart(product_revenue)

    except Exception as e:
        st.error(f"❌ Error: {e}")
    finally:
        cs.close()
        conn.close()
        os.remove(temp_file_path)
