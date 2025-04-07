StudyBuddy
==========

A smart, offline-friendly desktop app that lets you load PDF files, ask questions about them, and get summaries — powered by a local AI model (like LLaMA 3 via Ollama).

------------------------
✨ Features
------------------------

- 🖼️ PDF viewer with accurate page rendering (not just plain text!)
- 🧠 Summarize entire documents with one click
- 💬 Chat with an AI assistant about your document
- 🔍 Zoom in/out buttons for better readability
- ✅ Works offline (uses local LLMs via Ollama)

------------------------
📦 Installation
------------------------

1. Clone the repo:

    git clone https://github.com/your-username/StudyBuddy.git
    cd StudyBuddy

2. Install dependencies:

    pip install -r requirements.txt

3. Install Ollama for LLM functionality:

    Visit https://ollama.com and install Ollama for your OS.
    Then pull a model. Mistral is recommended but Llamma3 will work too, just slower:

    ollama run mistral

------------------------
🚀 Usage
------------------------

    python ui.py

- Use "📂 Open PDF" to load a document
- Click "🧠 Summarize Document" to generate a summary
- Ask questions in the chat panel — the AI will use the summary or full text

------------------------
🧠 Powered By
------------------------

- PyMuPDF (for extracting text and rendering PDFs)
- Pillow (for displaying PDF pages as images)
- CustomTkinter (modern UI)
- Ollama (for local language models)

------------------------
🔮 Planned Features
------------------------

- Flashcard generator
- Study quiz mode
- Save highlights and notes
- Browser extension
- Auto-scrolling and search
- Cleaner mobile/compact layout

------------------------
👨‍💻 Author
------------------------

Made by Kyle Tobin  
GitHub: https://github.com/kyle-tobin46
