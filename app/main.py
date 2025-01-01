from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from app.data_processing import process_ftir_data
from app.peak_detection import detect_peaks
from fastapi.responses import FileResponse
from app.functional_groups import identify_functional_group
from datetime import datetime
import matplotlib.pyplot as plt
import os

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Path to save the spectrum image
IMAGE_FOLDER = "spectra_images"

@app.post("/upload_ftir/")
async def upload_ftir(file: UploadFile = File(...)):
    try:
        # Step 1: Process the FTIR data
        wavenumbers, absorbance = process_ftir_data(file)

        # Step 2: Detect local maxima and minima (peaks and valleys)
        maxima, minima = detect_peaks(absorbance)

        # Step 3: Separate and label maxima and minima
        detected_maxima = []
        detected_minima = []

        # Handling maxima
        for i in maxima:
            # Convert numpy data types to native Python types (float)
            wavenumber = float(wavenumbers[i])
            absorbance_value = float(absorbance[i])

            functional_group = identify_functional_group(wavenumber)
            detected_maxima.append({
                "wavenumber": wavenumber,
                "absorbance": absorbance_value,
                "type": "peak",  # Local maxima
                "functional_group": functional_group
            })

        # Handling minima
        for i in minima:
            # Convert numpy data types to native Python types (float)
            wavenumber = float(wavenumbers[i])
            absorbance_value = float(absorbance[i])

            functional_group = identify_functional_group(wavenumber)
            detected_minima.append({
                "wavenumber": wavenumber,
                "absorbance": absorbance_value,
                "type": "valley",  # Local minima
                "functional_group": functional_group
            })

        # Step 4: Generate and save the FTIR spectrum plot
        plt.figure(figsize=(10, 6))
        plt.plot(wavenumbers, absorbance, label="FTIR Spectrum", color="blue")

        # Annotate maxima
        for peak in detected_maxima:
            plt.scatter(peak["wavenumber"], peak["absorbance"], color="red", label="Maxima" if peak == detected_maxima[0] else "")
            plt.annotate(
                f"{peak['functional_group']} ({int(peak['wavenumber'])})",
                (peak["wavenumber"], peak["absorbance"]),
                textcoords="offset points",
                xytext=(0, 10),
                ha='center',
                fontsize=8,
                color="red"
            )

        # Annotate minima
        for valley in detected_minima:
            plt.scatter(valley["wavenumber"], valley["absorbance"], color="green", label="Minima" if valley == detected_minima[0] else "")
            plt.annotate(
                f"{valley['functional_group']} ({int(valley['wavenumber'])})",
                (valley["wavenumber"], valley["absorbance"]),
                textcoords="offset points",
                xytext=(0, -15),
                ha='center',
                fontsize=8,
                color="green"
            )

        plt.xlabel("Wavenumber (cm^-1)")
        plt.ylabel("Absorbance")
        plt.title("FTIR Spectrum with Detected Peaks, Valleys, and Functional Groups")
        plt.legend()
        plt.grid()

        # Save the plot to a file with a unique name based on the file upload
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"ftir_spectrum_{timestamp}.png"
        image_path = os.path.join(IMAGE_FOLDER, image_filename)

        # Save the plot to a file
        plt.savefig(image_path)
        plt.close()

        # Return the detected peaks and the image filename for the frontend to use
        return {
            "detected_maxima": detected_maxima,
            "detected_minima": detected_minima,
            "image_filename": image_filename  # Return the image filename
        }

    except Exception as e:
        return {"error": str(e)}

@app.get("/get_spectrum_image/{image_filename}")
async def get_spectrum_image(image_filename: str):
    image_path = os.path.join(IMAGE_FOLDER, image_filename)
    if os.path.exists(image_path):
        return FileResponse(image_path, media_type="image/png")
    return {"error": "Spectrum image not found."}
