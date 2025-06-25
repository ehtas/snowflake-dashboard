# 📊 Streamlit Smart Data Uploader + Insight Dashboard

This project is a **web-based data dashboard** built using [Streamlit](https://streamlit.io/) and [Snowflake](https://www.snowflake.com/), designed to **let users upload CSV/Excel files and generate instant insights**.

✅ Includes:
- Secure **Firebase login/signup** (Google or Email/Password)
- Dynamic data ingestion to **Snowflake internal stage**
- Automatic **data preview + visual insights**
- Advanced summary charts using **Pandas, Seaborn & Streamlit**

---

## 🔄 How The App Evolved

### 🚀 Initial Goal
To create a simple app that:
- Uploads a `.csv` file
- Pushes it to Snowflake
- Shows basic data preview

### 🔐 Then came:
- Google + email **Firebase authentication**
- Ability to **restrict upload to only logged-in users**
- Secure Firebase integration with `secrets.toml`

### 📂 Extended File Support
- Added support for **.xlsx** file uploads
- Smart data preview + error handling for common formatting issues

### 📈 Insights Mode
- KPIs like Total Orders, Quantity, Revenue (if applicable)
- Dynamic charts: bar chart by product or any available field
- Automatically skips irrelevant columns

### 🤖 Future Enhancements (planned for v2):
- Dynamic schema creation in Snowflake (based on uploaded file)
- User-specific upload history
- Admin dashboard with usage stats

---

## 🧰 Tech Stack

| Tech        | Description |
|-------------|-------------|
| **Streamlit** | For web UI and real-time interactivity |
| **Snowflake** | Cloud data warehouse for staging and querying |
| **Firebase Auth** | Google & Email/Password login support |
| **Python (Pandas, Seaborn)** | Data processing and visual insights |
| **GitHub** | For version control and deployment integration |

---

## 🔧 How to Run Locally

1. **Clone the repo:**

```bash
git clone https://github.com/ehtas/snowflake-dashboard.git
cd snowflake-dashboard

2. Install dependencies:

```bash
pip install -r requirements.txt

3. Set up Streamlit Secrets:

Create a .streamlit/secrets.toml file:


[snowflake]
user = "YOUR_USERNAME"
password = "YOUR_PASSWORD"
account = "YOUR_ACCOUNT"
warehouse = "YOUR_WAREHOUSE"
database = "YOUR_DATABASE"
schema = "YOUR_SCHEMA"

[firebase]
api_key = "YOUR_FIREBASE_API_KEY"
auth_domain = "YOUR_PROJECT.firebaseapp.com"
database_url = ""
project_id = "YOUR_PROJECT_ID"
storage_bucket = ""
messaging_sender_id = ""
app_id = ""

4. Run the app:

```bash
streamlit run app.py

📦 Deployment
This app is fully deployable on Streamlit Community Cloud. Just upload your repo and make sure to:

Add your secrets.toml under app settings

Use app.py as the entry point

🙋‍♂️ Author
Ehtasham Ahmed

Let’s connect on https://www.linkedin.com/in/ehta/
Built with ♥ to make data uploads easier and more insightful.

📌 License
MIT License. Feel free to fork, improve, and give credit.