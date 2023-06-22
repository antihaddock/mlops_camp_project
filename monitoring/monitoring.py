from evidently import ColumnMapping
from evidently.report import Report
from evidently.metrics import ColumnDriftMetric, DatasetDriftMetric, DatasetMissingValuesMetric

colum_mapping = ColumnMapping(
    target = None,
    prediction = 'prediction',
    numerical_features = num_features,
    categorical_features = cat_features
)

report = Report(metrics=[
    ColumnDriftMetric(column_name='prediction'),
    DatasetDriftMetric(),
    DatasetMissingValuesMetric()
])

report.run(reference_data=train_data, current_data=val_data, column_mapping=column_mapping)

report.show(mode='inline')

result = report.as_dict()

# prediction drift off dictionary
result['metrics'][0]['result']['drift_score']

# number of drifed columns
result['metrics'][1]['result']['number_of_drifted_columns']

# share of missing values
result['metrics'][1]['result']['current']['share_of_missing_values']

