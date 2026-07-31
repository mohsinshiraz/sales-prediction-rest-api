# =============================================================================
# SuperKart Sales Forecaster - Flask REST API (backend)
#
# Serves the serialized scikit-learn pipeline over HTTP so that any system can
# request a forecast without knowing anything about scikit-learn.
#
# Endpoints:
#   GET  /                 -> welcome message (confirms the service is up)
#   POST /v1/sales         -> online inference: one JSON record in, one value out
#   POST /v1/salesbatch    -> batch inference: a CSV file in, predictions for all
# =============================================================================
# Import necessary libraries
import numpy as np
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
sales_predictor_api = Flask("SuperKart Sales Forecaster")

# Load the trained machine learning model
# Loaded ONCE at start-up rather than per request - loading is expensive, so
# doing it here keeps request latency low.

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
    the predicted sales as a JSON response.
    """
    # Get the JSON data from the request body
    dataset = request.get_json()

    # Extract relevant features from the JSON data
    # The keys below are the model's feature contract - they must match the
    # column names the pipeline was trained on, exactly.
    sample = {
        'Product_Weight': dataset['Product_Weight'],
        'Product_Sugar_Content': dataset['Product_Sugar_Content'],
        'Product_Allocated_Area': dataset['Product_Allocated_Area'],
        'Product_MRP': dataset['Product_MRP'],
        'Store_Size': dataset['Store_Size'],
        'Store_Location_City_Type': dataset['Store_Location_City_Type'],
        'Store_Type': dataset['Store_Type'],
        'Store_Age_Years': dataset['Store_Age_Years'],
        'Product_Type_Category': dataset['Product_Type_Category'],
        'Product_Id_char': dataset['Product_Id_char']

      }

    # Convert the extracted data into a Pandas DataFrame
    # The pipeline expects a 2-D structure, hence the single-element list
    input_data = pd.DataFrame([sample])

    # Make prediction
    # The pipeline imputes, scales and one-hot encodes internally before predicting
    prediction = model.predict(input_data)[0]

    # Convert predicted_price to Python float
    # NumPy floats are not JSON-serialisable, so cast before returning
    prediction = round(float(prediction), 2)

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

    # Make predictions in the DataFrame
    predictions = model.predict(input_data).tolist()
    #predictions = model.predict(input_data[REQUIRED_FEATURES])
    # Attach the predictions to a copy of the input so the caller gets full context back
    # Returning the input row alongside the forecast means downstream systems can
    # join the results straight into a planning table without tracking row order.
    output = input_data.copy()
    output["Predicted_Sales"] = [round(float(value), 2) for value in predictions]

    return jsonify({
        "n_records": int(len(output)),
        "predictions": output.to_dict(orient="records"),
    })
    # Create a dictionary of predictions with product IDs as keys
    #product_ids = input_data['Product_Id_char'].tolist()  # Assuming 'Product_Id' is the Product ID column
    #output_dict = dict(zip(product_ids, predictions))  # Use actuals

    # Return the predictions dictionary as a JSON response
    #return output_dict

# Run the Flask application in debug mode if this script is executed directly
# In the container this block is bypassed - Gunicorn imports the app object
# directly (see the Dockerfile CMD), which is far more robust than Flask's
# built-in development server.
if __name__ == '__main__':
    sales_predictor_api.run(debug=True)
