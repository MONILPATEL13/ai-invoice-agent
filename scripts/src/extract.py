"""Step 1: read the text from a PDF."""
import pdfplumber


def extract_text(pdf_file):
    """pdf_file can be a file path or an uploaded file object."""
    with pdfplumber.open(pdf_file) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    text = "\n".join(pages).strip()
    if not text:
        raise ValueError("No text found. This may be a scanned (image) PDF.")
    return text
