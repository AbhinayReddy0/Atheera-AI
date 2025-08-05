# app.py

import streamlit as st
from firebase_auth import login, signup, get_user
from shopify_api import get_shopify_orders
from agents.cleaning_agent import run_cleaning
from agents.pattern_agent import run_pattern
from agents.forecast_agent import run_forecast
from agents.reorder_agent import run_reorder
import pandas as pd

st.set_page_config(page_title="Atheera.ai", layout="wide")

# ---------- GLOBAL STYLING ----------
st.markdown("""
    <style>
    body {
        background-color: #0e0e0e;
        color: white;
    }
    .block-container {
        padding-top: 4rem;
    }
    .top-logo {
        position: fixed;
        top: 1rem;
        left: 1rem;
        display: flex;
        align-items: center;
        z-index: 100;
    }
    .top-logo img {
        height: 40px;
        margin-right: 10px;
    }
    .top-logo span {
        font-size: 22px;
        font-weight: 600;
        color: white;
    }
    .main-card {
        background-color: #1c1c1c;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 20px rgba(255,255,255,0.1);
        width: 400px;
        margin: 6rem auto 2rem auto;
    }
    input, .stTextInput > div > div > input {
        background-color: #1e1e1e !important;
        color: white !important;
        border: 1px solid #333;
    }
    .stButton button {
        background-color: #FFD700;
        color: black;
        font-weight: bold;
        border-radius: 5px;
        padding: 8px 16px;
    }
    .cta-section {
        background-color: #1a1a1a;
        text-align: center;
        padding: 3rem;
        border-radius: 12px;
        margin: 3rem auto;
    }
    .cta-section h2 {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
    }
    .cta-section p {
        font-size: 1.2rem;
        color: #cccccc;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    .cta-button button {
        background-color: #FFD700;
        color: black;
        font-weight: 600;
        padding: 12px 24px;
        font-size: 1rem;
        border-radius: 30px;
        border: none;
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)

# ---------- TOP LOGO ----------
st.markdown("""
    <div class="top-logo">
        <img src="https://raw.githubusercontent.com/your-username/your-repo/main/atheera_logo.png" alt="Atheera Logo"/>
        <span>Atheera AI</span>
    </div>
""", unsafe_allow_html=True)

# ---------- CTA HERO SECTION ----------
st.markdown("""
    <div class='cta-section'>
        <h2>Operate with 100% Confidence</h2>
        <p>Streamline your purchasing. Track inventory in real time. Boost your bottom line. (Repeat.)</p>
        <div class='cta-button'>
            <button onclick="location.href='#auth';">Start for free</button>
        </div>
    </div>
""", unsafe_allow_html=True)

# ---------- AUTH ----------
if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.markdown("<div id='auth' class='main-card'>", unsafe_allow_html=True)
    auth_mode = st.radio("Choose mode", ["Login", "Sign Up"], horizontal=True)
    email = st.text_input("📧 Email", placeholder="you@gmail.com")
    password = st.text_input("🔑 Password", type="password", placeholder="Enter password")

    if auth_mode == "Login":
        if st.button("🚀 Login"):
            user = login(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ Invalid login. Please try again.")
    else:
        if st.button("✅ Sign Up"):
            user = signup(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("❌ Signup failed. Try a different email.")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------- MAIN DASHBOARD ----------
st.sidebar.button("🚪 Logout", on_click=lambda: st.session_state.update({"user": None}))

st.markdown(f"<h2 style='text-align: center;'>👋 Welcome, {get_user(st.session_state.user)}</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Start by uploading your data or connecting Shopify below</p>", unsafe_allow_html=True)

st.markdown("<h3 style='margin-top: 2rem;'>📊 Step 1: Upload or Connect Data</h3>", unsafe_allow_html=True)
data = None
option = st.radio("Choose data source", ["Upload CSV", "Connect Shopify"])

if option == "Upload CSV":
    uploaded_file = st.file_uploader("📁 Upload your orders CSV", type="csv")
    if uploaded_file:
        data = pd.read_csv(uploaded_file)
        st.subheader("📦 Uploaded Data Sample")
        st.dataframe(data.head())

elif option == "Connect Shopify":
    shopify_token = st.text_input("🔑 Enter Shopify Access Token")
    shop_url = st.text_input("🌐 Shop URL (e.g. mystore.myshopify.com)")
    if st.button("🛒 Fetch Orders") and shopify_token and shop_url:
        try:
            data = get_shopify_orders(shop_url, shopify_token)
            st.subheader("🛍️ Shopify Orders")
            st.dataframe(data.head())
        except Exception as e:
            st.error(f"❌ Error fetching Shopify data: {e}")

st.markdown("<h3 style='margin-top: 2rem;'>🤖 Step 2: Run AI Inventory Assistant</h3>", unsafe_allow_html=True)

if data is not None and st.button("🚀 Run Full AI Pipeline"):
    with st.spinner("🧹 Running Cleaning Agent..."):
        clean_df, clean_score = run_cleaning(data)
        st.metric("🧼 Cleanliness Score", f"{clean_score}%")

    with st.spinner("🔍 Running SKU Pattern Agent..."):
        pattern_df = run_pattern(clean_df)
        st.subheader("📊 SKU Patterns")
        st.dataframe(pattern_df.head())

    with st.spinner("📈 Running Forecasting Agent..."):
        forecast_df = run_forecast(clean_df)
        st.subheader("📅 30-Day Forecast")
        st.line_chart(forecast_df.set_index("date")["forecast"])

    with st.spinner("📦 Running Reorder Agent..."):
        reorder_df = run_reorder(forecast_df)
        st.subheader("📦 Reorder Recommendations")
        st.dataframe(reorder_df.head())

    st.download_button("📥 Download PO CSV", reorder_df.to_csv(index=False), file_name="purchase_order.csv")
