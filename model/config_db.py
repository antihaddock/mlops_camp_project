
import datetime
import pandas as pd
from sqlalchemy import create_engine
from evidently.report import Report
from evidently import ColumnMapping
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric



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
    db_user = db_user
    db_password = db_password
    db_host = db_host
    db_port = db_port
    db_name = db_name

    credentials = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    return credentials

def prep_db(credentials):
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
        create table if not exists model_metrics(
            Hospital_code integer,
            Hospital_type_code varchar,
            City_Code_Hospital integer,
            Hospital_region_code  varchar,
            Availabl_Extra_Rooms_in_Hospital integer,
            Department varchar,
            Ward_Type varchar,
            Ward_Facility_Code varchar,
            Bed_Grade integer,
            patientid integer,
            City_Code_Patient integer,
            Type_of_Admission varchar,
            Severity_of_Illness varchar,
            Visitors_with_Patient integer,
            Age varchar,
            Admission_Deposit integer,
            Stay varchar,
            prediction integer,
            generated_at timestamp
        )
    """
    create_evidently_report_table_query = """
        create table if not exists evidently_report(
            prediction_drift integer,
            num_drifted_columns integer,
            share_missing_values integer,
            generated_at timestamp
        )
    
    """
    
    # Create the SQLAlchemy engine
    engine = create_engine(credentials)
    # Create the metrics table if it does not exist
    engine.execute(create_metrics_table_query)
    # Create the report table if it does not exist
    engine.execute(create_evidently_report_table_query)
    
   
def insert_metrics_to_db(df, prediction, credentials, table_name='model_metrics'):
    """ inserts the metrics from our ML model into the postgres database for monitoring

    Args:
        df (_type_): df of data to be inserted
        prediction (_type_): the predicted output from the ML model
        credentials (_type_): credentials for connecting to the db
        table_name (str, optional): optional overwrite of the postgres table name
    """
    engine = create_engine(credentials)
    table_name = table_name
    df['predictions'] = prediction
    # create generated time stamp for df
    df['generated_at'] = datetime.now()
    
    df.to_sql(table_name, engine, if_exists='append', index=False)

def calculate_evidently_metrics(df, prediction):
    """_summary_

    Args:
        df (_type_): _description_
        prediction (_type_): _description_
    """
       
    reference_data = pd.read_csv('./data/train_data.csv')
    
    # get the reference data in the format we need
    # Turning target column into a numeric option
    reference_data['Stay_numeric'] = reference_data['Stay'].map(
    {'0-10': 1,
    '11-20': 2,
    '21-30': 3,
    '31-40': 4,
    '41-50': 5,
    '51-60': 6,
    '61-70': 7,
    '71-80': 8,
    '81-90': 9,
    '91-100': 10,
    'More than 100 Days':11})
    
    # Dichotomise into admitted for Longer then 30 days or not
    reference_data['long_stay'] = df['Stay_numeric']>3
    reference_data['long_stay'] = df['long_stay'].replace({True:1, False:0})
    
    # Remove unneeded columns
    reference_data = reference_data.drop(['Stay', 'Stay_numeric'], axis=1)
    
    
    num_features = ['Hospital_code',
                    'City_Code_Hospital',
                    'Available Extra Rooms in Hospital', 
                    'total_amount', 
                    'Bed Grade',
                    'patientid',  
                    'Admission_Deposit',  
                    'City_Code_Patient',
                    'Visitors with Patient',
                    'long_stay']
    cat_features = ['Hospital_type_code',
                    'Hospital_region_code',
                    'Department', 
                    'Ward_Type',
                    'Ward_Facility_Code',
                    'Type of Admission',
                    'Severity of Illness',
                    'Age']
    
  
    column_mapping = ColumnMapping(
                    prediction='long_stay',
                    numerical_features=num_features,
                    categorical_features=cat_features,
                    target=None
                    )

    report = Report(metrics = [
                    ColumnDriftMetric(column_name='prediction'),
                    DatasetDriftMetric(),
                    DatasetMissingValuesMetric()
                    ])
    report.run(reference_data = reference_data, current_data = df,
	        	column_mapping=column_mapping)
    
    result = report.as_dict()
    prediction_drift = result['metrics'][0]['result']['drift_score']
    num_drifted_columns = result['metrics'][1]['result']['number_of_drifted_columns']
    share_missing_values = result['metrics'][2]['result']['current']['share_of_missing_values']
   
    # create a df to insert into the db off the report
    report_metrics = pd.DataFrame({'prediction_drift': prediction_drift,
                                   'num_drifted_columns': num_drifted_columns,
                                   'share_missing_values': share_missing_values})
    report_metrics['generated_at'] = datetime.now()
    
    engine = create_engine(credentials)
    table_name = 'evidently_report'
       
    report_metrics.to_sql(table_name, engine, if_exists='append', index=False)
    
    
def check_metric_retrain():
        pass