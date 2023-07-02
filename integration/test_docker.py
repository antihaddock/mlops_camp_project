# pylint: disable=duplicate-code

import json

import pandas as pd
import requests
from deepdiff import DeepDiff

# with open('event.json', 'rt', encoding='utf-8') as f_in:
#     event = json.load(f_in)


url = "http://0.0.0.0:5000/predict_outcome"


df = pd.read_csv("../data/integration_test_data.csv")

# This will run through and provide a prediction against each row in the test_data.csv
for i in range(len(df)):
    client = df.iloc[i].to_dict()

response = requests.post(url, json=client)
actual_response = response.json()
print(actual_response)
expected_response = {
    "Class": [0],
    "probability": [[0.8747006574382459, 0.12529934256175407]],
}


diff = DeepDiff(actual_response, expected_response, significant_digits=1)
print(f"diff={diff}")

assert "type_changes" not in diff
assert "values_changed" not in diff
