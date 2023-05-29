# Predict Function for project
# Takes the pickle file from train.py and utilises this inside a flask server to return a prediction based on data provided to the server

import mlflow
import pandas as pd
from flask import Flask, request, jsonify




# return the best model stored in mlflow
def best_model():
    # search mlflow for best model
    runs = mlflow.search_runs()
    # find te best run by auc score
    best_run = runs.loc[runs['metrics.auc_score'].idxmax()]
    #return the uri
    artifact_uri = best_run['artifact_uri']

    # Load the model using the artifact URI
    model = mlflow.sklearn.load_model(artifact_uri + "/model")

    return model


app = Flask('hopsital_stay_prediction')


@app.route('/predict_outcome', methods=['POST'])
def predict_outcomes():
    data = request.get_json()
    #df = pd.read_json(data)
    prediction, prediction_prob = predict_outcome(data, dv, model)
    
    result = {
        'Class': prediction.tolist(),
        'probability': prediction_prob.tolist()
    }

    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    