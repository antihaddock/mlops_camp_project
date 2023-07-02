from config_db import credentials, prep_db
from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)
from evidently.report import Report
from pre_process_data import preprocess
from sklearn.metrics import roc_auc_score
from sqlalchemy import create_engine


def check_model_performance(true_labels, predicted_labels, threshold=0.75):
    """_summary_

    Args:
        true_labels (_type_): true labels of the data which predictions are
        generated for
        predicted_labels (_type_): predicted labels from data passed to the ML model

    Returns:
        boolean : returns true if model performance below a threshold default of
        0.75 else returns false
    """
    auc = roc_auc_score(true_labels, predicted_labels)
    if auc < threshold:
        return True
    else:
        return False


def calculate_evidently_metrics(df, prediction):
    """Calculates the ML model performance against reference data. Reports generated are:
            ColumnDriftMetric(),
            DatasetDriftMetric(),
            DatasetMissingValuesMetric(),
        Results are logged into a database for storage

    Args:
        df (_type_): df of data upon which predictions were made
        prediction (_type_): ML model predicted label for the input data
    """

    reference_data = pd.read_csv("./data/train_data.csv")

    # Turning target column into a numeric option
    reference_data["Stay_numeric"] = reference_data["Stay"].map(
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
    reference_data["long_stay"] = reference_data["Stay_numeric"] > 3
    # reference_data['long_stay'] = reference_data['long_stay'].replace({True:1, False:0})
    target_column = reference_data["long_stay"].replace({True: 1, False: 0})

    reference_data = reference_data.drop(["Stay_numeric", "Stay"], axis=1)
    reference_data = preprocess(reference_data)

    num_features = [
        "Hospital_code",
        "Hospital_type_code",
        "City_Code_Hospital",
        "Hospital_region_code",
        "Available_Extra_Rooms_in_Hospital",
        "Department",
        "Ward_Type",
        "Ward_Facility_Code",
        "Bed_Grade",
        "patientid",
        "City_Code_Patient",
        "Type_of_Admission",
        "Severity_of_Illness",
        "Visitors_with_Patient",
        "Age",
        "Admission_Deposit",
        "hosp_patient_same",
        "Gender",
        "Num_hospitals",
        "unique_hospital_visited",
        "prediction",
    ]

    column_mapping = ColumnMapping(
        prediction=target_column,
        numerical_features=num_features,
        # categorical_features=cat_features,
        target=None,
    )

    report = Report(
        metrics=[
            ColumnDriftMetric(column_name=prediction),
            DatasetDriftMetric(),
            DatasetMissingValuesMetric(),
        ]
    )
    report.run(
        reference_data=reference_data, current_data=df, column_mapping=column_mapping
    )

    result = report.as_dict()
    prediction_drift = result["metrics"][0]["result"]["drift_score"]
    num_drifted_columns = result["metrics"][1]["result"]["number_of_drifted_columns"]
    share_missing_values = result["metrics"][2]["result"]["current"][
        "share_of_missing_values"
    ]

    # create a df to insert into the db off the report
    report_metrics = pd.DataFrame(
        {
            "prediction_drift": prediction_drift,
            "num_drifted_columns": num_drifted_columns,
            "share_missing_values": share_missing_values,
        }
    )

    engine = create_engine(credentials)
    prep_db()
    table_name = "evidently_report"

    report_metrics.to_sql(table_name, engine, if_exists="append", index=False)

    needs_retraining = check_model_performance(target_column, prediction)

    return needs_retraining
