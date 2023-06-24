# Predict Function for project
# Takes the pickle file from train.py and utilises this inside a flask server to return a prediction based on data provided to the server

import pandas as pd
from flask import Flask, request, jsonify
from pre_process_data import preprocess, best_model
from config_db import credentials, insert_metrics_to_db, prep_db, calculate_evidently_metrics, check_metric_retrain


# Helper functions to run the flask app
# 1. predict_outcome - loads and registers best model from mlflow and makes
#    a prediction on incoming data
# 2. log_model_performace - Saves the predictions to a database for monitoring of model
#    performance along with the input data


def predict_outcome(df):
    # import the best model from mlflow
    model = best_model('HospitalPrediction')
    # prepocess the df to feed into the model
    X = preprocess(df)
    # make predictions and retun class and probability of prediction    
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)
        
    return y_pred, y_prob

def log_model_performance(df, prediction):
    db_user = db_user
    db_password = db_password
    db_host = db_host
    db_port = db_port
    db_name = db_name
       
    credentials = credentials(db_user, db_password, db_host, db_port, db_name)
    prep_db(credentials)
    insert_metrics_to_db(df, prediction, credentials)
    
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
    log_model_performance(data, prediction)
    calculate_evidently_metrics(data, prediction)
    #check_metric_retrain()
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    