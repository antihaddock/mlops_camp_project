import my_module
import pandas as pd


def test_read_csv_file():
    # Create a temporary CSV file for testing
    file_path = "./data/test_data.csv"
    data = pd.read_csv(file_path)
    # file_path.write_text(data)

    # Call the function to read the CSV file
    result = my_module.read_csv_file("./data/test_data.csv")

    # Assert that the result is a pandas DataFrame
    assert isinstance(result, pd.DataFrame)

    # Assert that the DataFrame has the expected shape
    assert result.shape == data.shape
