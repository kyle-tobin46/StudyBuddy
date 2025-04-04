import requests
import json

def ask_llama3_stream(prompt):
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "mistral",
        "prompt": prompt,
        "stream": True
    }, stream=True)

    for line in response.iter_lines():
        if line:
            try:
                chunk = json.loads(line.decode("utf-8"))
                if "response" in chunk:
                    yield chunk["response"]
            except json.JSONDecodeError:
                continue  # ignore malformed lines

def is_ollama_running():
    try:
        r = requests.get("http://localhost:11434")
        return r.status_code == 200
    except:
        return False
