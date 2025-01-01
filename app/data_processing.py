import pandas as pd
import io

def process_ftir_data(file):
    # Read the uploaded file into a pandas DataFrame
    contents = file.file.read()
    df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

    # Check if the CSV file contains the necessary columns (wavenumber and absorbance)
    if 'Wavenumber' not in df.columns or 'Absorbance' not in df.columns:
        raise ValueError("CSV must contain 'Wavenumber' and 'Absorbance' columns")
    
    wavenumbers = df['Wavenumber'].values
    absorbance = df['Absorbance'].values
    
    return wavenumbers, absorbance
