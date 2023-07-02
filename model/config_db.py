import pandas as pd
import psycopg2



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

    # Insert the DataFrame into the table
    for row in df.itertuples(index=False):
        insert_query = f"INSERT INTO {table_name} VALUES {tuple(row)}"
        cursor.execute(insert_query)

    # Commit the changes to the database
    conn.commit()

    # Close the cursor and the database connection
    cursor.close()
    conn.close()


