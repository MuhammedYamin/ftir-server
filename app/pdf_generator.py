from fastapi import APIRouter, Query
from fastapi.responses import FileResponse
from fpdf import FPDF
from PIL import Image
import os

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # server folder
IMAGE_FOLDER = os.path.join(BASE_DIR, "spectra_images")
PDF_FOLDER = os.path.join(BASE_DIR, "pdf_reports")

os.makedirs(PDF_FOLDER, exist_ok=True)

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "FTIR Analysis Report", ln=True, align="C")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

@router.get("/download_pdf/")
def download_pdf(
    image_filename: str = Query(..., description="Name of the FTIR spectrum image file"),
    maxima: str = Query(..., description="Detected maxima data as JSON string"),
    minima: str = Query(..., description="Detected minima data as JSON string")
):
    import json

    try:
        detected_maxima = json.loads(maxima)
        detected_minima = json.loads(minima)
    except Exception:
        return {"error": "Invalid JSON data for maxima or minima"}
    


    if not image_filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        image_filename += '.png'  # or whatever extension you use

    pdf = PDFReport()
    pdf.add_page()

    # Add spectrum image
    image_path = os.path.join(IMAGE_FOLDER, image_filename)

    if os.path.exists(image_path):
        # Resize image to fit width
        image = Image.open(image_path)
        width, height = image.size
        max_width = 180  # mm in PDF units (approx)
        ratio = max_width / width
        new_height = height * ratio

        pdf.image(image_path, x=15, y=30, w=max_width, h=new_height)
        pdf.ln(new_height + 10)
    else:
        pdf.cell(0, 10, "Spectrum image not found.", ln=True)

    # Add detected maxima table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Detected Peaks (Maxima):", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(20, 10, "No.", 1)
    pdf.cell(40, 10, "Wavenumber", 1)
    pdf.cell(40, 10, "Absorbance", 1)
    pdf.cell(60, 10, "Functional Group", 1)
    pdf.cell(30, 10, "Type", 1)
    pdf.ln()

    for idx, peak in enumerate(detected_maxima, 1):
        pdf.cell(20, 10, str(idx), 1)
        pdf.cell(40, 10, f"{peak.get('wavenumber', 'N/A')}", 1)
        pdf.cell(40, 10, f"{peak.get('absorbance', 'N/A')}", 1)
        pdf.cell(60, 10, peak.get('functional_group', 'N/A'), 1)
        pdf.cell(30, 10, peak.get('type', 'N/A'), 1)
        pdf.ln()

    pdf.ln(5)

    # Add detected minima table
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Detected Minima:", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(20, 10, "No.", 1)
    pdf.cell(40, 10, "Wavenumber", 1)
    pdf.cell(40, 10, "Absorbance", 1)
    pdf.cell(60, 10, "Functional Group", 1)
    pdf.cell(30, 10, "Type", 1)
    pdf.ln()

    for idx, valley in enumerate(detected_minima, 1):
        pdf.cell(20, 10, str(idx), 1)
        pdf.cell(40, 10, f"{valley.get('wavenumber', 'N/A')}", 1)
        pdf.cell(40, 10, f"{valley.get('absorbance', 'N/A')}", 1)
        pdf.cell(60, 10, valley.get('functional_group', 'N/A'), 1)
        pdf.cell(30, 10, valley.get('type', 'N/A'), 1)
        pdf.ln()

    # Save PDF
    pdf_filename = f"FTIR_Report_{image_filename.split('.')[0]}.pdf"
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
    pdf.output(pdf_path)

    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_filename)
