import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from groq import Groq
from dotenv import load_dotenv

# 🌍 Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("🚨 API Key is missing! Set it in Streamlit Secrets or a .env file.")
    st.stop()

# 🎨 Streamlit UI Styling
st.set_page_config(page_title="📈 AI Dashboard Generator", page_icon="📊", layout="wide")
st.title("📊 AI-Powered Financial Dashboard Generator")

# 🗂 Upload Excel File
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
if not uploaded_file:
    st.info("Please upload an Excel file with columns: Date, Revenue, Expense, Profit, Headcount.")
    st.stop()

# 🧾 Load Data
df = pd.read_excel(uploaded_file)
expected_cols = {"Date", "Revenue", "Expense", "Profit", "Headcount"}
if not expected_cols.issubset(set(df.columns)):
    st.error(f"❌ Excel file must contain the following columns: {expected_cols}")
    st.stop()

# 📅 Convert date
df['Date'] = pd.to_datetime(df['Date'])
df.sort_values('Date', inplace=True)

# 📈 Chart Section
st.subheader("📊 Auto-Generated Charts")
with st.expander("Line Charts"):
    fig, ax = plt.subplots(figsize=(12, 5))
    for col in ['Revenue', 'Expense', 'Profit']:
        ax.plot(df['Date'], df[col], label=col)
    ax.set_title("Revenue vs Expense vs Profit Over Time")
    ax.legend()
    st.pyplot(fig)

with st.expander("📉 Headcount Over Time"):
    fig, ax = plt.subplots(figsize=(12, 4))
    sns.lineplot(data=df, x='Date', y='Headcount', marker='o', ax=ax)
    ax.set_title("Headcount Over Time")
    st.pyplot(fig)

with st.expander("💡 Revenue & Profit Distribution"):
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    sns.histplot(df['Revenue'], kde=True, ax=axs[0])
    axs[0].set_title("Revenue Distribution")
    sns.histplot(df['Profit'], kde=True, ax=axs[1])
    axs[1].set_title("Profit Distribution")
    st.pyplot(fig)

# 🤖 AI Commentary Section
st.subheader("🧠 AI-Generated Insights")
client = Groq(api_key=GROQ_API_KEY)

# Send full dataset to AI as JSON
data_for_ai = df.to_json(orient="records")

prompt = f"""
You are the Head of FP&A at a SaaS company. Your task is to analyze the full budget dataset and provide:
- Key insights from the data.
- Areas of concern and key drivers for variance.
- A CFO-ready summary using the Pyramid Principle.
- Actionable recommendations to improve financial performance.

Here is the full dataset in JSON format:
{data_for_ai}
"""

response = client.chat.completions.create(
    messages=[
        {"role": "system", "content": "You are a financial planning and analysis (FP&A) expert, specializing in SaaS companies."},
        {"role": "user", "content": prompt}
    ],
    model="llama3-8b-8192",
)

ai_commentary = response.choices[0].message.content
st.markdown("### 📖 AI Commentary")
st.write(ai_commentary)
