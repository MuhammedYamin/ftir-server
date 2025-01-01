import pandas as pd
import matplotlib.pyplot as plt

def identify_functional_group(wavenumber):
    """
    Identify the functional group based on the given wavenumber.
    :param wavenumber: The wavenumber value to match.
    :return: A string indicating the functional group.
    """
    if 3200 <= wavenumber <= 3600:
        return "O-H stretch"
    elif 2800 <= wavenumber <= 3100:
        return "C-H stretch"
    elif 1600 <= wavenumber <= 1800:
        return "C=O stretch"
    elif 1000 <= wavenumber <= 1300:
        return "C-O stretch"
    elif 600 <= wavenumber <= 800:
        return "C-H bend"
    else:
        return "Unknown"

def process_csv_and_identify_groups(csv_file):
    """
    Process the uploaded CSV file, identify functional groups for wavenumbers, and return the results.
    :param csv_file: The uploaded CSV file.
    :return: A list of dictionaries containing wavenumber, absorbance, and functional group.
    """
    try:
        # Read the CSV file into a Pandas DataFrame
        df = pd.read_csv(csv_file.file)
        
        # Validate required columns
        if 'Wavenumber' not in df.columns or 'Absorbance' not in df.columns:
            raise ValueError("CSV file must contain 'Wavenumber' and 'Absorbance' columns.")
        
        # Identify functional groups for each wavenumber
        results = []
        for _, row in df.iterrows():
            wavenumber = row['Wavenumber']
            absorbance = row['Absorbance']
            functional_group = identify_functional_group(wavenumber)
            
            results.append({
                "wavenumber": wavenumber,
                "absorbance": absorbance,
                "functional_group": functional_group
            })
        
        return results

    except Exception as e:
        raise ValueError(f"Error processing CSV file: {e}")

def plot_spectrum_with_annotations(df, output_file="spectra_images/ftir_spectrum_plot.png"):
    """
    Generate a plot of the FTIR spectrum with functional group annotations.
    :param df: The DataFrame containing wavenumbers and absorbance values.
    :param output_file: The path to save the plot image.
    """
    if 'Wavenumber' not in df.columns or 'Absorbance' not in df.columns:
        raise ValueError("CSV file must contain 'Wavenumber' and 'Absorbance' columns.")
    
    wavenumbers = df['Wavenumber']
    absorbance = df['Absorbance']
    
    # Create the plot
    plt.figure(figsize=(10, 6))
    plt.plot(wavenumbers, absorbance, label="FTIR Spectrum", color="black")
    plt.gca().invert_xaxis()  # FTIR spectra convention
    
    # Annotate functional groups
    for _, row in df.iterrows():
        wavenumber = row['Wavenumber']
        absorbance_value = row['Absorbance']
        functional_group = identify_functional_group(wavenumber)
        
        if functional_group != "Unknown":
            plt.annotate(
                f"{functional_group} ({int(wavenumber)})",
                (wavenumber, absorbance_value),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center',
                fontsize=8,
                color="red"
            )
    
    # Labels and title
    plt.xlabel("Wavenumber (cm^-1)")
    plt.ylabel("Absorbance")
    plt.title("FTIR Spectrum with Functional Group Annotations")
    plt.grid()
    plt.legend()
    
    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

    return output_file
