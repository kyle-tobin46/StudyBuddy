import fitz


# === Extract Text from PDF ===
def read_pdf(path: str):
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return pages
