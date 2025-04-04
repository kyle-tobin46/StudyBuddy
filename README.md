# StudyBuddy

**StudyBuddy** is a privacy-first, offline AI app that lets you open a PDF and chat with it like you're talking to the author.

Whether it's a dense research paper, a textbook, or class notes — StudyBuddy helps you summarize, clarify, and understand complex documents in plain language, all while mimicking the author's tone.

---

## Features

- Open any PDF and extract clean, structured text
- Ask questions and receive answers in the author's style
- Summarize sections or the whole document (Cliff Notes mode)
- Fully local — no internet required after setup
- “Open With StudyBuddy” support from right-click menu

---

## Tech Stack

- **Python** — core backend
- **Tkinter** — lightweight local GUI (or Tauri/Electron in future)
- **PyMuPDF** — PDF text extraction
- **FAISS** — local vector search
- **llama-cpp-python** — local LLM backend
- **MiniLM / BGE** — embedding models for similarity search

---

## Getting Started

# 1. Clone the repo
git clone https://github.com/kyle-tobin46/StudyBuddy.git
cd StudyBuddy

# 2. (Optional) Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python main.py

---

## Packaging & Distribution
StudyBuddy will be packaged into a standalone .exe or .app using PyInstaller or Tauri, allowing you to:

- Launch from your desktop

- Right-click → “Open with StudyBuddy” from your file explorer

### Planned Features

-Voice narration with Text-to-Speech

-Flashcard generator

-Study Mode with quizzes

-User highlights and notes

-Browser extension (future)

---

### Contributing
This is a solo side project for now, but suggestions, feedback, or issues are always welcome.

Made by Kyle Tobin
