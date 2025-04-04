import tkinter as tk
from tkinter import filedialog, scrolledtext
import fitz  # PyMuPDF
import os

def read_pdf(path):
    doc = fitz.open(path)
    pages = [page.get_text() for page in doc]
    doc.close()
    return pages

def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def open_pdf():
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, "Loading PDF...\nPlease wait.")
    text_area.update_idletasks()

    pages = read_pdf(file_path)
    if pages:
        full_text = "\n\n".join(pages)
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, full_text)

        file_name = os.path.basename(file_path)
        filename_label.config(text=f"📄 {file_name}")

# Main GUI setup
root = tk.Tk()
root.title("StudyBuddy PDF Reader")

# Set and center size
window_width, window_height = 800, 600
center_window(root, window_width, window_height)

# Bring window to front
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)
root.focus_force()

# File name label
filename_label = tk.Label(root, text="No file selected", font=("Arial", 12, "bold"))
filename_label.pack(pady=(10, 0))

# Open button
open_button = tk.Button(root, text="Open PDF", command=open_pdf)
open_button.pack(pady=5)

# Scrollable text area
text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12))
text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()
