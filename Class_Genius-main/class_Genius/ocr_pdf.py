from PIL import Image
import pytesseract
from fpdf import FPDF

def image_to_pdf(image_path, pdf_path):
    text = pytesseract.image_to_string(Image.open(image_path))

    # 🔒 FIX: remove unsupported unicode characters
    safe_text = text.encode("latin-1", "ignore").decode("latin-1")

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 8, safe_text)
    pdf.output(pdf_path)

    return safe_text
