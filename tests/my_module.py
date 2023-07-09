# my_module.py

import pandas as pd
from sklearn.preprocessing import LabelEncoder


def read_csv_file(file_path):
    """tests the correct data type is being read in and returned

    Args:
        file_path (_type_): _description_

    Returns:
        _type_: _description_
    """
    return pd.read_csv(file_path)


def pre_processing():
    """
        Tests data is correctly pre processed
    """ 
    df = pd.read_csv("./data/train_data.csv")
    
    df["Stay_numeric"] = df["Stay"].map(
        {
            "0-10": 1,
            "11-20": 2,
            "21-30": 3,
            "31-40": 4,
            "41-50": 5,
            "51-60": 6,
            "61-70": 7,
            "71-80": 8,
            "81-90": 9,
            "91-100": 10,
            "More than 100 Days": 11,
        }
    )

    # Dichotomise into admitted for Longer then 30 days or not
    df["long_stay"] = df["Stay_numeric"] > 3
    df["long_stay"] = df["long_stay"].replace({True: 1, False: 0})

    # Encode categorical variables and treat like ordinal
    le = LabelEncoder()
    columns_to_encode = [
        "Hospital_type_code",
        "Hospital_region_code",
        "Department",
        "Ward_Type",
        "Ward_Facility_Code",
        "Type of Admission",
        "Severity of Illness",
        "City_Code_Patient",
    ]

    for column in columns_to_encode:
        df[column] = le.fit_transform(df[column].values)

    # If hosp and patient are in same city
    df["hosp_patient_same"] = [
        1 if i == j else 0
        for i, j in zip(df["City_Code_Hospital"].values, df["City_Code_Patient"].values)
    ]

    # Gender. 1 -> Female, 0 -> Male
    df["Gender"] = [1 if i == "gynecology" else 0 for i in df["Department"].values]

    # Number of hospitals in a city
    df["Num_hospitals"] = df.groupby(["City_Code_Hospital"])["Hospital_code"].nunique()
    df["Num_hospitals"] = df["Num_hospitals"].fillna(0)

    # number of unique hospitals visited
    df["unique_hospital_visited"] = df.groupby("patientid")["Hospital_code"].transform(
        "nunique"
    )

    class_map = {
        "0-10": 0,
        "11-20": 1,
        "21-30": 2,
        "31-40": 3,
        "41-50": 4,
        "51-60": 5,
        "61-70": 6,
        "71-80": 7,
        "81-90": 8,
        "91-100": 9,
        "More than 100 Days": 10,
    }

    df["Age"] = [(class_map[i] * 10) + 1 for i in df["Age"].values]
    df = df.drop(columns=['Stay'])
    
    return df