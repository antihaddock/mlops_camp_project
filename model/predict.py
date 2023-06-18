# Predict Function for project
# Takes the pickle file from train.py and utilises this inside a flask server to return a prediction based on data provided to the server

import pandas as pd
from flask import Flask, request, jsonify
from pre_process_data import preprocess, best_model


def predict_outcome(df):
    # import the best model from mlflow
    model = best_model('HospitalPrediction')
    # prepocess the df to feed into the model
    X = preprocess(df)
    # make predictions and retun class and probability of prediction    
    y_pred = model.predict(X)
    y_prob = model.predict_proba(X)
        
    return y_pred, y_prob

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
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    