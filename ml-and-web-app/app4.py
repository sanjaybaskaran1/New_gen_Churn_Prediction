import streamlit as st
import pandas as pd
from joblib import load
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sqlite3
import hashlib

# Load the saved ML model
with open("GB.joblib", "rb") as f:
    model = load(f)

# Database setup
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)''')
conn.commit()

# Utility function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# User authentication
def login_user(username, password):
    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hash_password(password)))
    return cursor.fetchone()

# Add new user to database
def add_user(username, password):
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

# Set Streamlit page configuration
st.set_page_config(page_title="Churn Prediction App", layout="wide")

# Sidebar navigation
st.sidebar.header("Navigation")
menu_options = ["Login", "Signup", "Upload Dataset", "Data Insights", "Prediction", "About Churn"]
selected_menu = st.sidebar.radio("Choose an option:", menu_options)

st.sidebar.markdown("---")
st.sidebar.info("Developed by Sanjay using Decision Tree Model")

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "df" not in st.session_state:
    st.session_state.df = None

# ======================== AUTH SECTIONS ===========================

if selected_menu == "Signup":
    st.title("🔑 Signup")
    with st.form("signup_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        confirm_password = st.text_input("🔒 Confirm Password", type="password")
        signup_submit = st.form_submit_button("Sign Up")

    if signup_submit:
        if password != confirm_password:
            st.error("Passwords do not match!")
        elif add_user(username, password):
            st.success("Signup successful! Please log in.")
        else:
            st.error("Username already exists. Please choose a different one.")

elif selected_menu == "Login":
    st.title("🔓 Login")
    with st.form("login_form"):
        username = st.text_input("👤 Username")
        password = st.text_input("🔒 Password", type="password")
        login_submit = st.form_submit_button("Login")

    if login_submit:
        user = login_user(username, password)
        if user:
            st.session_state.authenticated = True
            st.success("Login successful!")
        else:
            st.error("Invalid username or password.")

if st.session_state.authenticated:

    # ======================== MENU SECTIONS ===========================

    if selected_menu == "Upload Dataset":
        st.title("📤 Upload Your Dataset")
        uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

        if uploaded_file:
            st.session_state.df = pd.read_csv(uploaded_file)
            st.success("Dataset successfully uploaded!")
            st.dataframe(st.session_state.df.head())

    elif selected_menu == "Data Insights":
        if st.session_state.df is None:
            st.warning("Please upload a dataset first.")
        else:
            st.title("📊 Enhanced Data Insights")

            # Dataset Overview
            st.markdown("### 🔍 Dataset Overview")
            st.dataframe(st.session_state.df.head())

            # Summary Statistics
            st.markdown("### 📊 Summary Statistics")
            st.write(st.session_state.df.describe())

            # Correlation Heatmap
            st.markdown("### 🔥 Correlation Heatmap")
            numeric_cols = st.session_state.df.select_dtypes(include=['float64', 'int64']).columns
            if len(numeric_cols) > 1:
                fig, ax = plt.subplots(figsize=(10, 6))
                sns.heatmap(st.session_state.df[numeric_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
                st.pyplot(fig)
            else:
                st.info("Not enough numerical columns for correlation heatmap.")

            # Churn Distribution Analysis
            st.markdown("### 📈 Churn Distribution Analysis")
            if 'Churn' in st.session_state.df.columns:
                churn_counts = st.session_state.df['Churn'].value_counts()
                st.bar_chart(churn_counts)

                # Churn vs Numerical Features
                st.markdown("### 🔍 Churn vs Numerical Features")
                selected_feature = st.selectbox("Select a numerical feature", numeric_cols)
                if selected_feature:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    sns.boxplot(data=st.session_state.df, x='Churn', y=selected_feature, ax=ax)
                    st.pyplot(fig)

            else:
                st.warning("No 'Churn' column found in your dataset.")

            # Categorical Feature Distribution
            st.markdown("### 📊 Categorical Feature Distribution")
            categorical_cols = st.session_state.df.select_dtypes(include=['object']).columns
            if len(categorical_cols) > 0:
                selected_cat_col = st.selectbox("Select a categorical feature", categorical_cols)
                if selected_cat_col:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    st.session_state.df[selected_cat_col].value_counts().plot.pie(
                        autopct="%1.1f%%", ax=ax, colors=sns.color_palette("pastel"))
                    ax.set_ylabel("")
                    st.pyplot(fig)
            else:
                st.info("No categorical features available.")

    elif selected_menu == "Prediction":
        st.title("🔮 Churn Prediction")
        if st.session_state.df is None:
            st.warning("Please upload a dataset first.")
        else:
            with st.form("prediction_form"):
                st.write("Enter Customer Details Below")
                user_inputs = {}
                for col in st.session_state.df.columns[:-1]:  # Exclude 'Churn' column
                    if st.session_state.df[col].dtype in ['int64', 'float64']:
                        user_inputs[col] = st.number_input(f"🔢 Enter value for {col}", value=0)
                    else:
                        user_inputs[col] = st.text_input(f"✍️ Enter value for {col}", value="")

                submit_button = st.form_submit_button(label="🔮 Predict")

            if submit_button:
                user_data = pd.DataFrame([user_inputs])
                prediction = model.predict(user_data)
                st.success(f"✅ **Predicted Churn Status:** {'Yes' if prediction[0] == 1 else 'No'}")

    elif selected_menu == "About Churn":
        st.title("📚 About Customer Churn")
        st.markdown("""
        Customer churn refers to when customers stop doing business with a company. 
        Understanding churn helps businesses:
        - Retain valuable customers
        - Enhance customer service
        - Improve profitability
        """)
        st.image("https://images.pexels.com/photos/3183167/pexels-photo-3183167.jpeg?auto=compress&cs=tinysrgb&w=800",
                 use_column_width=True, caption="Customer Focus is Key")
else:
    st.warning("Please log in to access the application features.")
