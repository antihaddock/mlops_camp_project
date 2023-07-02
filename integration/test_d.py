import requests
import pandas as pd

# Local port test options
url = 'http://0.0.0.0:5000/predict_outcome'


df = pd.read_csv('../data/integration_test_data.csv')

# This will run through and provide a prediction against each row in the test_data.csv
for i in range(len(df)):
    client = df.iloc[i].to_dict()

    response = requests.post(url, json=client)
    result = response.json()
    print(result)