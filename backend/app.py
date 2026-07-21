# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
sales_predictor_api = Flask("SuperKart Sales Forecaster")

# Load the trained machine learning model
model = joblib.load("superkart_sales_forecast_model_v1_0.joblib")

# Define a route for the home page (GET request)
@sales_predictor_api.get('/')
def home():
    """
    This function handles GET requests to the root URL ('/') of the API.
    It returns a simple welcome message.
    """
    return "Welcome to the SuperKart Sales Forecaster API!"

# Define an endpoint for single property prediction (POST request)
@sales_predictor_api.post('/v1/sales')
def predict_sales():
    """
    This function handles POST requests to the '/v1/sales' endpoint.
    It expects a JSON payload containing property details and returns
    the predicted rental price as a JSON response.
    """
    # Get the JSON data from the request body
    property_data = request.get_json()

    # Extract relevant features from the JSON data
    sample = {
        'Product_Weight': dataset['Product_Weight'],
        'Product_Sugar_Content': dataset['Product_Sugar_Content'],
        'Product_Allocated_Area': dataset['Product_Allocated_Area'],
        'Product_MRP': dataset['Product_MRP'],
        'Store_Size': dataset['Store_Size'],
        'Store_Location_City_Type': dataset['Store_Location_City_Type'],
        'Store_Type': dataset['Store_Type'],
        'Product_Id_char': dataset['Product_Id_char'],
        'Store_Establishment_Year': dataset['Store_Establishment_Year'],
        'Product_Type_Category': dataset['Product_Type_Category']
        
      }

    # Convert the extracted data into a Pandas DataFrame
    input_data = pd.DataFrame([sample])

    # Make prediction
    prediction = model.predict(input_data)[0]

    # Convert predicted_price to Python float
    prediction = round(float(prediction), 2)
    # The conversion above is needed as we convert the model prediction (log price) to actual price using np.exp, which returns predictions as NumPy float32 values.
    # When we send this value directly within a JSON response, Flask's jsonify function encounters a datatype error

    # Return the actual price
    return jsonify({'Sales': prediction})


# Define an endpoint for batch prediction (POST request)
@sales_predictor_api.post('/v1/salesbatch')
def predict_sales_batch():
    """
    This function handles POST requests to the '/v1/salesbatch' endpoint.
    It expects a CSV file containing property details for multiple properties
    and returns the predicted sales as a dictionary in the JSON response.
    """
    # Get the uploaded CSV file from the request
    file = request.files['file']

    # Read the CSV file into a Pandas DataFrame
    input_data = pd.read_csv(file)

    # Make predictions for all properties in the DataFrame (get log_prices)
    predictions = model.predict(input_data).tolist()

    # Create a dictionary of predictions with property IDs as keys
    product_ids = input_data['Product_Id'].tolist()  # Assuming 'Product_Id' is the Product ID column
    output_dict = dict(zip(product_ids, predictions))  # Use actuals

    # Return the predictions dictionary as a JSON response
    return output_dict

# Run the Flask application in debug mode if this script is executed directly
if __name__ == '__main__':
    sales_predictor_api.run(debug=True)
