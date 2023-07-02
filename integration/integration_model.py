# Predict Function for project
# Takes the pickle file from train.py and utilises this inside a flask server to return a prediction based on data provided to the server

import pickle

import numpy as np
from flask import Flask, jsonify, request

# import model for use
with open("./model.pkl", "rb") as f_in:
    model = pickle.load(f_in)


def predict_outcome(df):
    """_summary_

    Args:
        df (_type_): dataframe of data for prediction

    Returns:
        y_pred: predicted classes
        y_prob: probabilities of the predicted class
    """
    df = np.array([list(df.values())])
    # make predictions and retun class and probability of prediction
    y_pred = model.predict(df)
    y_prob = model.predict_proba(df)

    return y_pred, y_prob


# The flask app and flask main function
app = Flask("hospital_stay_prediction")


@app.route("/predict_outcome", methods=["POST"])
def predictions():
    """
    Makes predictions on incoming data from ML model
    
    Returns:
        result: json object of the classes and probabilities
        of predicted data from the ML model
    """
    data = request.get_json()
    prediction, prediction_prob = predict_outcome(data)
    result = {"Class": prediction.tolist(), "probability": prediction_prob.tolist()}
    print(result)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
