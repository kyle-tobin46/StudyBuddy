import re
from llm import ask_llama3_stream

# === Clean the raw PDF text ===
def clean_text(text):
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

# === Chunk the full text into manageable pieces ===
def chunk_text(text, max_chars=2000):
    paragraphs = text.split("\n\n")
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < max_chars:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

# === Batch summarize multiple chunks at once ===
def summarize_multiple_chunks(chunks):
    joined = "\n\n".join(f"[Section {i+1}]\n{chunk}" for i, chunk in enumerate(chunks))
    prompt = (
        "Summarize each section below in 1-2 sentences. Return your answers numbered, one per section:\n\n"
        + joined
    )

    response = ""
    for token in ask_llama3_stream(prompt):
        response += token

    return parse_numbered_summaries(response.strip(), len(chunks))

# === Parse LLM response into a list of summaries ===
def parse_numbered_summaries(response_text, num_expected):
    import re
    summaries = [""] * num_expected
    pattern = r'^\s*(\d+)[\.\)]\s*(.+)$'
    matches = re.findall(pattern, response_text, re.MULTILINE)

    if matches:
        for idx_str, summary in matches:
            idx = int(idx_str) - 1
            if 0 <= idx < num_expected:
                summaries[idx] = summary.strip()
    else:
        # fallback: if there's no matching numbers, treat as one big summary
        single_summary = response_text.strip()
        for i in range(num_expected):
            summaries[i] = f"(fallback) {single_summary}"

    return summaries

# === Full preprocessing pipeline ===
def preprocess_document(pages, summarize=True, max_chars=2000, max_chunks=5):
    all_text = [clean_text(p) for p in pages]
    full_text = "\n\n".join(all_text)

    chunks = chunk_text(full_text, max_chars=max_chars)
    chunks = chunks[:max_chunks]  # Limit for speed

    summaries = summarize_multiple_chunks(chunks) if summarize else [None] * len(chunks)

    results = []
    for i, chunk in enumerate(chunks):
        results.append({
            "chunk_index": i,
            "chunk": chunk,
            "summary": summaries[i] if i < len(summaries) else None
        })

    return results
