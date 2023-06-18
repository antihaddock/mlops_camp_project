# training ML model using ML Flow
"""

This file will train an a ML Model from several possible model options.
The script takes data from the directory located at ./data/ and exports the model as a pickle
to the ./model/ directory for use. The name of the created model is ml-model.bin

"""
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier

# Read in data for exploration and drop unneeded columns
df = pd.read_csv('../data/train_data.csv', index_col='case_id')

#-------------------- Pre Processing --------------------------------------------------
# Turning target column into a numeric option
df['Stay_numeric'] = df['Stay'].map(
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
df['long_stay'] = df['Stay_numeric']>3
df['long_stay'] = df['long_stay'].replace({True:1, False:0})


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
    "City_Code_Patient"
]

for column in columns_to_encode:
    # if column == "City_Code_Patient":
    #     df[column] = df[column].astype('int')
    # else:
        df[column] = le.fit_transform(df[column].values)

# If hosp and patient are in same city
df['hosp_patient_same'] = [1 if i == j else 0 for i, j in zip(df["City_Code_Hospital"].values, df['City_Code_Patient'].values)]

# Gender. 1 -> Female, 0 -> Male
df["Gender"] = [1 if i=="gynecology" else 0 for i in df["Department"].values]


# Number of hospitals in a city
df["Num_hospitals"] = df.groupby(["City_Code_Hospital"])["Hospital_code"].nunique()
df["Num_hospitals"] = df["Num_hospitals"].fillna(0)

# number of unique hospitals visited
df['unique_hospital_visited']=df.groupby('patientid')['Hospital_code'].transform('nunique')

class_map = {"0-10": 0, "11-20": 1, "21-30": 2, "31-40": 3, "41-50": 4, "51-60": 5, "61-70": 6, "71-80": 7, "81-90": 8, "91-100": 9, "More than 100 Days": 10}
#class_map_rev = {0: "0-10", 1: "11-20", 2: "21-30", 3: "31-40", 4: "41-50", 5: "51-60", 6: "61-70", 7: "71-80", 8: "81-90", 9: "91-100", 10: "More than 100 Days"}

df["Age"] = [(class_map[i]*10)+1 for i in df["Age"].values]


#------------------- Drop na's at the end of this proces ------------------------------------------

# drop any left over na's
df = df.dropna()


# Remove unneeded columns
df = df.drop(['Stay'], axis=1)


# -------------- Test Train split and create numeric target variable --------------------------------
# Test train split
y = df['long_stay']
X = df.drop(['long_stay',  'Stay_numeric'], axis=1)

# split into test and train
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size=0.2)




# ------------------ Train ML Models and store results in ML Flow --------------------------------------------------------- 
# We will use the Scikit Learn wrapper of xgb to avoid needing to create matrix and label encode the Y variables
# these parameters have been found following EDA and modelling in notebook.ipynb
def train_test_model(model, X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test):
       
    #tracking_uri = "../mlflow_models/"
    tracking_uri = 'http://127.0.0.1:8000' 
    mlflow.set_tracking_uri(tracking_uri)
    with mlflow.start_run(run_name='HospitalPrediction'):
            mlflow.log_param("model_name", type(model).__name__)
            model = model

            # Fit the model to the training data
            model.fit(X_train, y_train)

              # Predict the target variable for the test set
            y_pred = model.predict(X_test)

            # Create and print the confusion matrix
            cm = confusion_matrix(y_test, y_pred, normalize='true')
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



# ------------- train models and save them to Mlflow -------------------------------------------------------

if __name__ == "__main__":
    models = [LogisticRegression(), RandomForestClassifier(), XGBClassifier()]

    for model in models:
           train_test_model(model)