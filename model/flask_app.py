# testing the Flask App works locally when predict.py is running
# Test by iterating over all rows of the test dataframe and returning a predicted class for the data

import pandas as pd
import requests

# Local port flask app test options
# url = 'http://127.0.0.1:5000/predict_outcome'

# docker image locally port
url = "http://0.0.0.0:5000/predict_outcome"
# url = 'http://127.0.0.1:5000/predict_outcome'

# Elastic Beanstalk address to interact with the model
# host = 'mlbookcamp-env.eba-msik3tgu.ap-southeast-2.elasticbeanstalk.com'
# url = f'http://{host}/predict_outcome'

df = pd.read_csv("./data/test_data.csv")
# This will run through and provide a prediction against each row in the test_data.csv
for i in range(7):  # range(len(df)):
    client = df.iloc[i].to_dict()
    response = requests.post(url, json=client)
    result = response.json()
    print(result)
