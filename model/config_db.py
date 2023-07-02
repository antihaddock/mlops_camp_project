from datetime import datetime

import pandas as pd
import psycopg2
from evidently import ColumnMapping
from evidently.metrics import (
    ColumnDriftMetric,
    DatasetDriftMetric,
    DatasetMissingValuesMetric,
)
from evidently.report import Report
from pre_process_data import preprocess
from sqlalchemy import create_engine


def credentials(db_user, db_password, db_host, db_port, db_name):
    """provides summary for the postgres database we are using

    Args:
        db_user (_type_): username of db
        db_password (_type_): password of db
        db_host (_type_): host ip address of db
        db_port (_type_): host port of db
        db_name (_type_): db name

    Returns:
        credentials: a string for connecting to the db
    """
    credentials = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

    return credentials


def prep_db():
    """
    Creates a table to store the model metrics if it does not exist and a table for
    evidently reports if it does not alredy exist

    Args:
        credentials for the logging onto the database

    Returns:
        null
    """
    # Define your PostgreSQL connection details
    create_metrics_table_query = """
      CREATE TABLE IF NOT EXISTS model_metrics (
            Hospital_code INTEGER,
            Hospital_type_code INTEGER,
            City_Code_Hospital INTEGER,
            Hospital_region_code INTEGER,
            Available_Extra_Rooms_in_Hospital INTEGER,
            Department INTEGER,
            Ward_Type INTEGER,
            Ward_Facility_Code INTEGER,
            Bed_Grade INTEGER,
            patientid INTEGER,
            City_Code_Patient INTEGER,
            Type_of_Admission INTEGER,
            Severity_of_Illness  INTEGER,
            Visitors_with_Patient INTEGER,
            Age INTEGER,
            Admission_Deposit INTEGER,
            hosp_patient_same INTEGER,
            Gender INTEGER,
            Num_hospitals INTEGER,
            unique_hospital_visited INTEGER,
            prediction INTEGER
            )
        """

    create_evidently_report_table_query = """
        create table if not exists evidently_report(
            prediction_drift integer,
            num_drifted_columns integer,
            share_missing_values integer
           
        )
    
    """

    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        host="postgres", database="postgres1", user="user1", password="password1"
    )

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Execute the SQL statement
    cursor.execute(create_metrics_table_query)
    cursor.execute(create_evidently_report_table_query)

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()


def insert_metrics_to_db(
    df, prediction, table_name, db_host, db_name, db_user, db_password
):
    """inserts ml model inputs and prediction into a postgres database

    Args:
        df (_type_): _description_
        table_name (_type_): _description_
        db_host (_type_): _description_
        db_database (_type_): _description_
        db_user (_type_): _description_
        db_password (_type_): _description_
    """
    # Establish a connection to the PostgreSQL database
    conn = psycopg2.connect(
        host=db_host, database=db_name, user=db_user, password=db_password
    )

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Specify the target table name
    table_name = table_name

    df = pd.DataFrame(df, index=[0])
    df["predictions"] = prediction

    # create generated time stamp for df
    # df['generated_at'] = datetime.now()

    # Insert the DataFrame into the table
    for row in df.itertuples(index=False):
        insert_query = f"INSERT INTO {table_name} VALUES {tuple(row)}"
        cursor.execute(insert_query)

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()


def calculate_evidently_metrics(df, prediction):
    """_summary_

    Args:
        df (_type_): _description_
        prediction (_type_): _description_
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

    # num_features = ['Hospital_code',
    #                 'City_Code_Hospital',
    #                 'Available Extra Rooms in Hospital',
    #                 'total_amount',
    #                 'Bed Grade',
    #                 'patientid',
    #                 'Admission_Deposit',
    #                 'City_Code_Patient',
    #                 'Visitors with Patient',
    #                 'long_stay']
    # cat_features = ['Hospital_type_code',
    #                 'Hospital_region_code',
    #                 'Department',
    #                 'Ward_Type',
    #                 'Ward_Facility_Code',
    #                 'Type of Admission',
    #                 'Severity of Illness',
    #                 'Age']

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
            ColumnDriftMetric(column_name="prediction"),
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
    report_metrics["generated_at"] = datetime.now()

    engine = create_engine(credentials)
    table_name = "evidently_report"

    report_metrics.to_sql(table_name, engine, if_exists="append", index=False)


def check_metric_retrain():
    pass
