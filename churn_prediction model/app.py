import streamlit as st
import pandas as pd
import numpy as np
import pickle

# Load the trained model
model = pickle.load(open("model.sav", "rb"))

# Function to align features of new data with trained model
def align_features(new_data, trained_features):
    for col in trained_features:
        if col not in new_data.columns:
            new_data[col] = 0
    return new_data[trained_features]

# Set a custom theme
st.set_page_config(
    page_title="Churn Prediction App",
    page_icon="📊",
    layout="centered",
)

# Main title and subtitle
st.title("📊 Churn Prediction App")
st.markdown(
    """
    **Welcome to the Churn Prediction App!**
    - Upload your customer data in CSV format.
    - Get predictions for customer churn along with probabilities.
    - Download the predictions for further analysis.
    """
)

# Add an image banner
st.image("https://miro.medium.com/v2/resize:fit:1400/1*47xx1oXuebvYwZeB0OutuA.png", use_column_width=True)

# Sidebar for file upload
st.sidebar.header("Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])

# Sidebar info
st.sidebar.info("Ensure your file is in CSV format.")

# Main logic
if uploaded_file is not None:
    try:
        # Load the uploaded file
        input_df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        st.write("### Uploaded Data Preview")
        st.dataframe(input_df.head())

        # Preprocess the input data (one-hot encoding)
        new_df_dummies = pd.get_dummies(input_df)

        # Align the features with the trained model
        trained_features = model.feature_names_in_
        aligned_df = align_features(new_df_dummies, trained_features)

        # Perform prediction
        predictions = model.predict(aligned_df)
        probabilities = model.predict_proba(aligned_df)[:, 1]

        # Display results
        results = input_df.copy()
        results["Churn Prediction"] = predictions
        results["Churn Probability"] = probabilities

        st.write("### Prediction Results")
        st.dataframe(results.style.background_gradient(cmap="coolwarm"))

        # Add a success message with metrics
        churn_count = sum(predictions)
        st.metric("Total Predicted Churns", f"{churn_count} customers")
        st.metric("Churn Probability (Avg.)", f"{np.mean(probabilities):.2f}")

        # Download results as a CSV
        csv = results.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download Predictions as CSV",
            data=csv,
            file_name="churn_predictions.csv",
            mime="text/csv",
        )

        # Fun interactive chart (optional)
        st.write("### Churn Probability Distribution")
        st.bar_chart(results["Churn Probability"])

    except Exception as e:
        st.error(f"An error occurred while processing your file: {e}")
else:
    st.info("Upload a CSV file to see predictions.")

# Add a footer
st.markdown(
    """
    ---
    **Created by [SANJAY BASKARAN]**  
    *Empowering businesses with data-driven decisions!*
    """
)
