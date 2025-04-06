import customtkinter as ctk
import tkinter.filedialog as filedialog
import tkinter.messagebox as msg
import tkinter as tk
import os
import fitz
import io
import threading
from PIL import Image, ImageTk
from llm import ask_llama3_stream, is_ollama_running
from preprocessor import preprocess_document

# === Global state ===
processed_chunks = []
current_pdf_path = None
image_refs = []  # prevent garbage collection of page images

# === Setup ===
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("StudyBuddy")

# Center the window
window_width, window_height = 1000, 700
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
app.geometry(f"{window_width}x{window_height}+{x}+{y}")
app.after(200, lambda: app.lift())

# === PDF rendering as images ===
def render_pdf_as_images(file_path):
    global image_refs
    image_refs.clear()

    doc = fitz.open(file_path)
    for widget in image_frame.winfo_children():
        widget.destroy()

    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=150)  # high-quality render
        img_data = pix.tobytes("ppm")
        image = Image.open(io.BytesIO(img_data))
        photo = ImageTk.PhotoImage(image)

        label = tk.Label(image_frame, image=photo, bg="#1c1c1c")
        label.image = photo
        label.pack(pady=10)

        image_refs.append(photo)  # prevent garbage collection

    doc.close()

# === Open PDF ===
def open_pdf():
    global processed_chunks, current_pdf_path
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    current_pdf_path = file_path  # Save full path
    render_pdf_as_images(file_path)
    filename_label.configure(text=f"📄 {os.path.basename(file_path)}")
    processed_chunks = []


    render_pdf_as_images(file_path)
    file_name = os.path.basename(file_path)
    filename_label.configure(text=f"📄 {file_name}")
    processed_chunks = []

# === Summarization ===
def summarize_document():
    global processed_chunks
    chat_log.configure(state="normal")
    chat_log.insert("end", "\n🤖 Summarizing document... please wait.\n")
    chat_log.configure(state="disabled")
    chat_log.see("end")

    def run_summary():
        doc = fitz.open(current_pdf_path)
        pages = [page.get_text() for page in doc]
        doc.close()

        processed_chunks = preprocess_document(pages, summarize=True, max_chars=750, max_chunks=3)
        print(f"🧠 Summary chunks: {len(processed_chunks)}")
        print(pages[:1])



        summary_text = "\n\n".join(
            f"• {c['summary']}" for c in processed_chunks if c["summary"]
        ).strip()

        chat_log.configure(state="normal")
        chat_log.insert("end", "\n📄 Summary of Document:\n")
        chat_log.insert("end", summary_text + "\n")
        chat_log.configure(state="disabled")
        chat_log.see("end")

    threading.Thread(target=run_summary, daemon=True).start()

# === Chat ===
def send_chat():
    user_input = chat_entry.get().strip()
    if not user_input:
        return

    chat_entry.delete(0, "end")

    if not is_ollama_running():
        msg.showerror("Ollama Not Running", "Please start Ollama to use StudyBuddy's AI assistant.")
        return

    if processed_chunks:
        context = "\n\n".join(chunk["summary"] for chunk in processed_chunks if chunk["summary"])
    else:
        # fallback to raw text from PDF
        try:
            doc = fitz.open(current_pdf_path)
            pages = [page.get_text() for page in doc]
            context = "\n\n".join(pages)[:3000]  # limit context length
            doc.close()
        except Exception as e:
            context = "No context available due to an error."
            print("Context fallback error:", e)

    prompt = f"Answer this question using the following context:\n\n{context}\n\nQuestion: {user_input}"

    chat_log.configure(state="normal")
    chat_log.insert("end", f"\n🧑‍💻 You: {user_input}\n")
    thinking_index = chat_log.index("end")
    chat_log.insert("end", "🤖 AI: Thinking...\n")
    chat_log.configure(state="disabled")
    chat_log.see("end")
    chat_log.update_idletasks()

    def stream_response():
        chat_log.configure(state="normal")
        chat_log.delete(f"{thinking_index} -1 lines", thinking_index)
        for token in ask_llama3_stream(prompt):
            chat_log.insert("end", token)
            chat_log.see("end")
            chat_log.update_idletasks()
        chat_log.configure(state="disabled")

    threading.Thread(target=stream_response, daemon=True).start()

# === Layout ===

padding_frame = ctk.CTkFrame(app, corner_radius=0, fg_color="transparent")
padding_frame.pack(fill="both", expand=True, padx=10, pady=10)

main_pane = tk.PanedWindow(padding_frame, orient="horizontal", sashwidth=4, bg="#1c1c1c", sashrelief="flat")
main_pane.pack(fill="both", expand=True)

# === LEFT: PDF Viewer ===
left_frame = ctk.CTkFrame(master=main_pane, corner_radius=10)
main_pane.add(left_frame, minsize=400)

filename_label = ctk.CTkLabel(left_frame, text="No file selected", font=ctk.CTkFont(size=14, weight="bold"))
filename_label.pack(anchor="w")

top_controls = ctk.CTkFrame(left_frame, fg_color="transparent")
top_controls.pack(anchor="w", pady=(5, 5))

open_button = ctk.CTkButton(top_controls, text="📂 Open PDF", command=open_pdf, width=120)
open_button.pack(side="left", padx=(0, 5))

summarize_button = ctk.CTkButton(top_controls, text="🧠 Summarize Document", command=summarize_document)
summarize_button.pack(side="left")

# === Scrollable image frame for PDF pages ===
scroll_canvas = tk.Canvas(left_frame, bg="#1c1c1c", highlightthickness=0)
scroll_y = tk.Scrollbar(left_frame, orient="vertical", command=scroll_canvas.yview)
scroll_canvas.configure(yscrollcommand=scroll_y.set)

image_frame = tk.Frame(scroll_canvas, bg="#1c1c1c")
scroll_canvas.create_window((0, 0), window=image_frame, anchor='nw')

def update_scroll_region(event):
    scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

image_frame.bind("<Configure>", update_scroll_region)

scroll_canvas.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")

# === RIGHT: Chat ===
right_frame = ctk.CTkFrame(master=main_pane, corner_radius=10)
main_pane.add(right_frame, minsize=250)

chat_log = ctk.CTkTextbox(right_frame, font=("Helvetica", 11), corner_radius=6, wrap="word")
chat_log.pack(fill="both", expand=True, pady=(0, 5))
chat_log.configure(state="disabled")

chat_input_frame = ctk.CTkFrame(right_frame, fg_color="transparent")
chat_input_frame.pack(fill="x", pady=(0, 10))

chat_entry = ctk.CTkEntry(chat_input_frame, placeholder_text="Ask a question...", font=("Helvetica", 12))
chat_entry.pack(side="left", fill="x", expand=True)
chat_entry.bind("<Return>", lambda e: send_chat())

send_button = ctk.CTkButton(chat_input_frame, text="Send", width=70, command=send_chat)
send_button.pack(side="left", padx=(5, 0))

# === Set initial split
app.after(300, lambda: main_pane.paneconfig(left_frame, width=500))

# === Run the app
app.mainloop()
