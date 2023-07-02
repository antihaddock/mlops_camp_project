import mlflow
import pandas as pd
from sklearn.preprocessing import LabelEncoder


def preprocess(df):
    """
    Args:
        df (_type_): _description_

    Returns:
        df: a pre processed dataset that converts columns into numeric variables
        or one hot encodes variables for use.

        The df returned will be in a format which can be fed into the ML model inside
        predict.py
    """
    # process the incoming dictionary and handle the case_id column
    df = pd.DataFrame.from_dict([df])
    # drop any  missing values
    df = df.dropna()
    df = df.reset_index()
    df = df.drop(["case_id", "index"], axis=1)

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


# return the best model stored in mlflow
def best_model(experiment_name):
    """
     Args:
        experiment_name (_type_):the name of the experiment to pass to mlflow

    Returns:
        model: Loads the model with the best AUC value saved into MLflow for use
    """

    tracking_uri = "http://mlflow-container:8000"
    mlflow.set_tracking_uri(tracking_uri)
    experiment_id = mlflow.get_experiment_by_name(experiment_name).experiment_id
    runs = mlflow.search_runs(experiment_ids=[experiment_id])

    # make sure it isnt a failed run
    runs = runs[runs["status"] != "FAILED"]

    # Filter the runs based on the specified run_name
    best_run = runs.loc[runs["metrics.auc_score"].idxmax()]

    # Get the artifact URI for the best run
    artifact_uri = best_run["artifact_uri"]

    # Get the run_id of the best run
    run_id = best_run["run_id"]
    # Load the model using the artifact URI
    model = mlflow.sklearn.load_model(f"runs:/{run_id}/model")

    # Register the model for use
    mlflow.register_model(
        model_uri=f"runs:/{run_id}/model", name="hospital_length_of_stay-classifier"
    )

    return model
