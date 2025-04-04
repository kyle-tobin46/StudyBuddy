from tkinter import Tk, filedialog
import fitz  # PyMuPDF

def read_pdf(path):
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return pages

def select_pdf():
    root = Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )
    return file_path

if __name__ == "__main__":
    pdf_path = select_pdf()
    if pdf_path:
        pages = read_pdf(pdf_path)
        print(f"PDF loaded: {pdf_path}")
        print(f"Total pages: {len(pages)}")
        print("\n--- First Page Preview ---\n")
        print(pages[0][:1000])  # print a snippet of the first page
    else:
        print("No file selected.")
