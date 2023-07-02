# Predict Function for project
# Takes the pickle file from train.py and utilises this inside a flask server to return a prediction based on data provided to the server

import pandas as pd
from config_db import insert_metrics_to_db, prep_db
from evidently_log import calculate_evidently_metrics, check_model_performance
from flask import Flask, jsonify, request
from pre_process_data import best_model, preprocess

# Helper functions to run the flask app
# 1. predict_outcome - loads and registers best model from mlflow and makes
#    a prediction on incoming data
# 2. log_model_performace - Saves the predictions to a database for monitoring of model
#    performance along with the input data


def predict_outcome(df):
    """
    Predicts the outcome of the input data off the ML model

    Args:
        df (_type_): input data in the dtype of a dataframe

    Returns:
        y_pred: predicted classes
        y_prob: probabilities of the predicted class
    """

    # import the best model from mlflow
    model = best_model("HospitalPrediction")
    # prepocess the df to feed into the model
    X = preprocess(df)
    # make predictions and retun class and probability of prediction
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)

    return y_pred, y_prob


def log_model_performance(df, prediction):
    """Logs the results of the ML model into the database
    for storage

    Args:
        df (_type_): df of the input data
        prediction (_type_): prediction from the ML model off the input data
    """
    db_user = "user1"
    db_password = "password1"
    db_host = "postgres"
    db_port = 5432
    db_name = "postgres1"
    table_name = "model_metrics"

    prep_db()
    df = preprocess(df)
    insert_metrics_to_db(
        df, prediction, table_name, db_host, db_name, db_user, db_password
    )


# The flask app and flask main function
app = Flask("hospital_stay_prediction")


@app.route("/predict_outcome", methods=["POST"])
def predictions():
    """
    Implements prediction of outcome from data provided to the ML model

    Returns:
       results: json objects of the results of the ML model predictions
    """
    data = request.get_json()
    prediction, prediction_prob = predict_outcome(data)

    result = {"Class": prediction.tolist(), "probability": prediction_prob.tolist()}
    print(result)
    log_model_performance(data, prediction)
    # calculate_evidently_metrics(df, prediction)
    # check_model_performance()
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
