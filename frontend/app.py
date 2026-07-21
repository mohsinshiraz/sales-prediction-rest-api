import streamlit as st
import pandas as pd
import requests

# Base URL of the Flask backend
BACKEND_URL = "http://backend:7860"

# Set the title of the Streamlit app
st.title("Sales Prediction")

# Section for online prediction
st.subheader("Online Prediction")

# Collect user input for features
#Product_Id = st.text_input("Product Id.", max_chars=20, help="Enter the product Id.")
Product_Weight = st.number_input("Product Weight", min_value=0.0, help="Enter the product weight (lbs).")
Product_Sugar_Content = st.selectbox("Product sugar content", ["Low Sugar", "Regular", "No Sugar"], help="Enter the product sugar content.")
Product_Allocated_Area = st.number_input("Product allocated area", min_value=0.0, help="Enter the ratio of the allocated display area of the product.")
#Product_Type = st.selectbox("Product type", ["Baking Goods","Breads","Breakfast","Canned","Dairy","Frozen Foods","Fruits and Vegetables","Hard Drinks",
#                                             "Health and Hygiene","Household","Meat","Others","Seafood","Snack Foods","Soft Drinks","Starchy Foods"],
#                            help="Enter the product sugar content.")
Product_MRP = st.number_input("Product MRP", min_value=0.0, help="Enter the maximum retail price of the product.")
#Store_Id = st.text_input("Store Id.", max_chars=10, help="Enter the store Id.")
Store_Size = st.selectbox("Store size", ["High", "Medium", "Small"], help="Enter the size of the store.")
Store_Location_City_Type = st.selectbox("Store size", ["Tier 1", "Tier 2", "Tier 3"], help="Enter the type of city in which the store is located.")
Store_Type = st.selectbox("Store type", ["Departmental Store", "Food Mart","Store_Type","Supermarket Type1","Supermarket Type2"],
                          help="Enter the type of store depending on the products that are being sold.")
Store_Establishment_Year = st.number_input("Store establishment year", min_value=1987, max_value=2025, help="Enter the year in which the store was established.")
Product_Type_Category = st.selectbox("Product Type Category", ["Perishables", "Non Perishables"])
Product_Id_char = st.selectbox("Product Id char", ["FD, "NC", "DR"])



# Convert user input into a DataFrame
input_data = pd.DataFrame([{
    "Product_Weight": Product_Weight,
    "Product_Sugar_Content": Product_Sugar_Content,
    "Product_Allocated_Area": Product_Allocated_Area,
    "Product_MRP": Product_MRP,
    "Store_Size": Store_Size,
    "Store_Location_City_Type": Store_Location_City_Type,
    "Store_Type": Store_Type,
    "Store_Establishment_Year": Store_Establishment_Year,
    "Product_Type_Category": Product_Type_Category,
    "Product_Id_char": Product_Id_char
}])

# Make prediction when the "Predict" button is clicked
if st.button("Predict", type="primary"):
    response = requests.post(f"{BACKEND_URL}/v1/sales", json=input_data.to_dict(orient='records')[0])  # Send data to Flask API
    if response.status_code == 200:
        prediction = response.json()['Predicted Sales']
        st.success(f"Predicted Sales: {prediction}")
    else:
        st.error("Unable to connect to the prediction API.")

# Section for batch prediction
st.subheader("Batch Prediction")

# Allow users to upload a CSV file for batch prediction
uploaded_file = st.file_uploader("Upload CSV file for batch prediction", type=["csv"])

# Make batch prediction when the "Predict Batch" button is clicked
if uploaded_file is not None:
    if st.button("Predict Batch", type="primary"):
        response = requests.post(f"{BACKEND_URL}/v1/salesbatch", files={"file": uploaded_file})  # Send file to Flask API
        if response.status_code == 200:
            predictions = response.json()
            st.success("Batch predictions completed!")
            st.write(predictions)  # Display the predictions
        else:
            st.error("Unable to connect to the prediction API.")
