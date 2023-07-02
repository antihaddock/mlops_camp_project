# training ML model using ML Flow
"""

This file will train an a ML Model from several possible model options.
The script takes data from the directory located at ./data/ and utilises Mlflow
to monitor model training metrics and store model artifacts.

This is optimised to run with prefect to monitor training data and pre processing

"""
import mlflow
import pandas as pd

# from sklearn.ensemble import RandomForestClassifier
# from xgboost import XGBClassifier
from prefect import flow, task
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from xgboost import XGBClassifier


@task
def read_data(filename: str) -> pd.DataFrame:
    """_summary_

    Args:
        filename (str): _description_

    Returns:
        pd.DataFrame: _description_
    """
    # Read in data for exploration and drop unneeded columns
    df = pd.read_csv(filename, index_col="case_id")

    return df


@task
def pre_process(df) -> pd.DataFrame:
    """
    Pre processes a dataframe into the required format for ML modelling

    Args:
        df (_type_): dataframe to be transformed
    Returns:
        pd.DataFrame: a transformed dataframe
    """
    # -------------------- Pre Processing -----------------------------
    # Turning target column into a numeric option
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

    return df


# ----------------- Drop na's at the end of this proces ----------------


@task
def test_train_split(df):
    """_summary_

    Args:
        df (_type_): dataframe of data to be split into test and train

    Returns:
        X_train, X_test, y_train, y_test: 4 arrays of test and train X and
        Y datasets
    """
    # drop any left over na's
    df = df.dropna()

    # Remove unneeded columns
    df = df.drop(["Stay"], axis=1)

    # -------------- Test Train split and create numeric target variable -------
    # Test train split
    y = df["long_stay"]
    X = df.drop(["long_stay", "Stay_numeric"], axis=1)

    # split into test and train
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, random_state=42, test_size=0.2
    )

    return X_train, X_test, y_train, y_test


# ------------------ Train ML Models and store results in ML Flow -------------
# We will use the Scikit Learn wrapper of xgb to avoid needing to create matrix
# and label encode the Y variables
# these parameters have been found following EDA and modelling in notebook.ipynb
@task
def train_test_model(model, tracking_uri, X_train, y_train, X_test, y_test):
    """_summary_

    Args:
        model (_type_): _description_
        tracking_uri (_type_): _description_
        X_train (_type_): _description_
        y_train (_type_): _description_
        X_test (_type_): _description_
        y_test (_type_): _description_

    Returns:
        _type_: _description_
    """

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment("HospitalPrediction")
    with mlflow.start_run():
        mlflow.log_param("model_name", type(model).__name__)
        model = model

        # Fit the model to the training data
        model.fit(X_train, y_train)

        # Predict the target variable for the test set
        y_pred = model.predict(X_test)

        # Create and print the confusion matrix
        cm = confusion_matrix(y_test, y_pred, normalize="true")
        print("Normalized Confusion Matrix:")
        print(cm)

        # Calculate and print the accuracy score
        accuracy = accuracy_score(y_test, y_pred)
        mlflow.log_metric("accuracy", accuracy)
        print("Accuracy:", accuracy)

        # Calculate the predicted probabilities and AUC score
        y_prob = model.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_prob)
        mlflow.log_metric("auc_score", auc_score)
        print("AUC Score:", auc_score)
        # Save the model as an artifact
        mlflow.sklearn.log_model(model, "model")
    return model


@flow
def main_flow(filename, tracking_uri):
    """_summary_

    Args:
        filename (_type_): filename of the data used in the ml model training
        tracking_uri (_type_): link to the mlflow uri that will be used for by prefect
    """
    df = read_data(filename)
    df = pre_process(df)
    X_train, X_test, y_train, y_test = test_train_split(df)

    # Setup models we want to train
    models = [LogisticRegression(), RandomForestClassifier()]  # , XGBClassifier()]

    for model in models:
        train_test_model(model, tracking_uri, X_train, y_train, X_test, y_test)


# ------------- train models and save them to Mlflow -------------------------------------------------------

if __name__ == "__main__":
    FILE_NAME = "./data/train_data.csv"
    TRACKING_URI = "http://0.0.0.0:8000"
    main_flow(FILE_NAME, TRACKING_URI)
