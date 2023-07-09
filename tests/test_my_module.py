import my_module
import pandas as pd


def test_read_csv_file():
    """
    unit test to check if a csv file is being read
    """
    # Create a temporary CSV file for testing
    file_path = "./data/test_data.csv"
    data = pd.read_csv(file_path)
  
    # Call the function to read the CSV file
    result = my_module.read_csv_file("./data/test_data.csv")

    # Assert that the result is a pandas DataFrame
    assert isinstance(result, pd.DataFrame)

    # Assert that the DataFrame has the expected shape
    assert result.shape == data.shape


def test_pre_processing():
    """
    Unit test to check data is correctly pre processed
    Data returned from preprocessing must be a different format and shape   
    """
    file_path = "./data/test_data.csv"
    data = pd.read_csv(file_path)
    result = my_module.pre_processing()
    
    # test that the shapes of the data and result are not the same    
    assert result.shape != data.shape
    
    # Check all columns pre preprocessed are numeric
    numeric_columns = result.select_dtypes(include=[int, float]).columns
    assert len(numeric_columns) == len(result.columns)