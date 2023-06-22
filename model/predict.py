# Predict Function for project
# Takes the pickle file from train.py and utilises this inside a flask server to return a prediction based on data provided to the server

import pandas as pd
from flask import Flask, request, jsonify
from pre_process_data import preprocess, best_model
from pymongo import MongoClient

EVIDENTLY_SERVICE_ADDRESS = 'http://127.0.0.1:5000' 
MONGODB_ADDRESS = "mongodb://127.0.0.1:27017"
mongo_client = MongoClient(MONGODB_ADDRESS)
db = mongo_client.get_database("prediction_service")
collection = db.get_collection("data")

# Helper functions to run the flask app
# 1. predict_outcome - loads and registers best model from mlflow and makes
#    a prediction on incoming data
# 2. save_to_db - Saves the predictions to a database for monitoring of model
#    performance
# 3. send_to_evidently_service - sends prediction results to evidently server
#    for model monitoring

def predict_outcome(df):
    # import the best model from mlflow
    model = best_model('HospitalPrediction')
    # prepocess the df to feed into the model
    X = preprocess(df)
    # make predictions and retun class and probability of prediction    
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)
        
    return y_pred, y_prob

def save_to_db(record, prediction):
    result = record.copy()
    collection.insert_one(result)

def send_to_evidently_service(record, prediction):
    rec = record.copy()
    rec['prediction'] = prediction
    requests.post(f"{EVIDENTLY_SERVICE_ADDRESS}/iterate/taxi", json=[rec])
  
  
    
# The flask app and flask main function
app = Flask('hospital_stay_prediction')

@app.route('/predict_outcome', methods=['POST'])
def predictions():
    data = request.get_json()
    prediction, prediction_prob = predict_outcome(data)
    
    result = {
        'Class': prediction.tolist(),
        'probability': prediction_prob.tolist()
    }
    print(result)
    save_to_db(result)
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    