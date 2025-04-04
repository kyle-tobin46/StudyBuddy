import tkinter as tk
from tkinter import filedialog, scrolledtext
import tkinter.messagebox as msg
import os
import fitz
import threading
from llm import ask_llama3_stream, is_ollama_running
from preprocessor import preprocess_document

# === Global state ===
processed_chunks = []

# === Read and clean PDF ===
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

# === Open PDF ===
def open_pdf():
    global processed_chunks

    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not file_path:
        return

    text_area.config(state=tk.NORMAL)
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, "Loading PDF...\nPlease wait.")
    text_area.update_idletasks()

    pages = read_pdf(file_path)
    if pages:
        full_text = "\n\n".join(pages)
        text_area.delete("1.0", tk.END)
        text_area.insert(tk.END, full_text)
        text_area.config(state=tk.DISABLED)

        file_name = os.path.basename(file_path)
        filename_label.config(text=f"📄 {file_name}")

        processed_chunks = []  # clear any old summaries

# === Manual summarization ===
def summarize_document():
    global processed_chunks

    text_area.config(state=tk.NORMAL)
    text_area.update_idletasks()

    # Fallback: treat entire text as a single page (works for now)
    pages = [text_area.get("1.0", tk.END)]

    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, "\n🤖 Summarizing document... please wait.\n", "ai")
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)

    def run_summary():
        global processed_chunks
        processed_chunks = preprocess_document(pages, summarize=True, max_chars=750, max_chunks=3)

        summary_text = "\n\n".join(
            f"• {c['summary']}" for c in processed_chunks if c["summary"]
        ).strip()

        chat_log.config(state=tk.NORMAL)
        chat_log.insert(tk.END, "\n📄 Summary of Document:\n", "summary")
        chat_log.insert(tk.END, summary_text + "\n", "ai")
        chat_log.config(state=tk.DISABLED)
        chat_log.see(tk.END)

    threading.Thread(target=run_summary, daemon=True).start()

# === Chat ===
def send_chat():
    user_input = chat_entry.get().strip()
    if not user_input:
        return

    chat_entry.delete(0, tk.END)

    if not is_ollama_running():
        msg.showerror("Ollama Not Running", "Please start Ollama to use StudyBuddy's AI assistant.")
        return

    if processed_chunks:
        context = "\n\n".join(chunk["summary"] for chunk in processed_chunks if chunk["summary"])
    else:
        context = text_area.get("1.0", tk.END)[:2000]

    prompt = f"Answer this question using the following context:\n\n{context}\n\nQuestion: {user_input}"

    # === Write message + thinking text ===
    chat_log.config(state=tk.NORMAL)
    chat_log.insert(tk.END, f"\n🧑‍💻 You: {user_input}\n", "user")
    thinking_index = chat_log.index(tk.END)
    chat_log.insert(tk.END, "🤖 AI: Thinking...\n", "ai")
    chat_log.config(state=tk.DISABLED)
    chat_log.see(tk.END)
    chat_log.update_idletasks()  # Force it to render before stream starts

    def stream_response():
        chat_log.config(state=tk.NORMAL)
        # Remove "Thinking..." line
        chat_log.delete(thinking_index, f"{thinking_index} +1 line")

        for token in ask_llama3_stream(prompt):
            chat_log.insert(tk.END, token, "ai")
            chat_log.see(tk.END)
            chat_log.update_idletasks()

        chat_log.config(state=tk.DISABLED)

    threading.Thread(target=stream_response, daemon=True).start()


# === GUI ===
root = tk.Tk()
root.title("StudyBuddy")
center_window(root, 1000, 700)
root.lift()
root.attributes('-topmost', True)
root.after_idle(root.attributes, '-topmost', False)
root.focus_force()

# === Styling ===
bg_color = "#1c1c1c"
fg_color = "#393939"
accent_color = "#393939"
font_family = "Helvetica"

root.configure(bg=bg_color)

# === Layout ===
main_frame = tk.Frame(root, bg=bg_color)
main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

# === LEFT: PDF viewer ===
pdf_frame = tk.Frame(main_frame, bg=bg_color)
pdf_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

filename_label = tk.Label(pdf_frame, text="No file selected", font=(font_family, 14, "bold"), fg="white", bg=bg_color)
filename_label.pack(anchor="w")

open_button = tk.Button(
    pdf_frame, text="📂 Open PDF", command=open_pdf,
    font=(font_family, 12), bg="black", fg=accent_color,
    relief="flat", padx=10, pady=5
)
open_button.pack(anchor="w", pady=(5, 5))

summarize_button = tk.Button(
    pdf_frame, text="🧠 Summarize Document", command=summarize_document,
    font=(font_family, 12), bg="#444", fg=accent_color,
    relief="flat", padx=10, pady=5
)
summarize_button.pack(anchor="w", pady=(0, 10))

text_area = scrolledtext.ScrolledText(
    pdf_frame,
    wrap=tk.WORD,
    font=(font_family, 12),
    bg=accent_color,
    fg="#C6C6C6",
    insertbackground=fg_color,
    borderwidth=0
)
text_area.pack(fill=tk.BOTH, expand=True)
text_area.config(state=tk.DISABLED)

# === RIGHT: Chat ===
chat_frame = tk.Frame(main_frame, bg=bg_color, width=350)
chat_frame.pack(side=tk.RIGHT, fill=tk.Y)

chat_log = tk.Text(chat_frame, font=(font_family, 11), bg="#2e2e2e", fg=fg_color, wrap=tk.WORD, borderwidth=0)
chat_log.pack(fill=tk.BOTH, expand=True, pady=(0, 5), padx=(10, 0))
chat_log.config(state=tk.DISABLED)
chat_log.tag_config("user", foreground="#C6C6C6", font=(font_family, 11, "bold"))
chat_log.tag_config("ai", foreground="#00A400", font=(font_family, 11))
chat_log.tag_config("summary", foreground="#66ffcc", font=(font_family, 11, "bold"))

chat_input_frame = tk.Frame(chat_frame, bg=bg_color)
chat_input_frame.pack(fill=tk.X, padx=(10, 0), pady=(0, 10))

chat_entry = tk.Entry(chat_input_frame, font=(font_family, 12), bg="#2e2e2e", fg="#C6C6C6", insertbackground=fg_color)
chat_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
chat_entry.bind("<Return>", lambda event: send_chat())

send_button = tk.Button(chat_input_frame, text="Send", command=send_chat, bg="#444", fg=accent_color, font=(font_family, 12), padx=10, pady=4, relief="flat")
send_button.pack(side=tk.RIGHT, padx=(5, 0))

# === Launch ===
root.mainloop()
