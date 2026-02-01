import os
import PyPDF2
import requests
import tkinter as tk
from tkinter import filedialog

from tts import elevenlabs_tts_full

# ===================== CONFIG =====================
API_KEY_GEMINI = "AIzaSyBp3i4bca-fNa_Cktn7LgiS9cY6Spk8y-Q"
GEMINI_MODEL = "gemini-2.5-flash"  # Replace with your model
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

CHUNK_SIZE = 1000  # Smaller chunks to prevent API issues

API_KEY_11LABS = "sk_0249bae0ca69ff3a1befe4725be51b0485c64594a197ec77"
VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # Default voice, can replace
# ==================================================

# ---------------- PDF TEXT EXTRACTION ----------------
def extract_text_from_pdf(path):
    text = ""
    if os.path.isdir(path):
        for filename in os.listdir(path):
            if filename.lower().endswith(".pdf"):
                pdf_path = os.path.join(path, filename)
                text += extract_text_from_pdf(pdf_path) + "\n"
    elif os.path.isfile(path) and path.lower().endswith(".pdf"):
        try:
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            print(f"Error reading {path}: {e}")
    else:
        raise ValueError("Please provide a PDF file or folder containing PDFs.")
    return text

def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# ---------------- GEMINI BRAIN-ROT ----------------
def gemini_translate_to_genz(text):
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY_GEMINI
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": f"Rewrite this in Gen Z brainrot slang. Be funny, casual, meme-like, but keep the meaning:\n{text}"
                    }
                ]
            }
        ]
    }
    response = requests.post(GEMINI_URL, headers=headers, json=payload)
    if response.status_code != 200:
        print("Gemini API error!")
        print("STATUS:", response.status_code)
        print("BODY:", response.text)
        return ""
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print("⚠️ Gemini returned empty output for this chunk.")
        return ""

# ---------------- ELEVENLABS TTS ----------------
def elevenlabs_tts(text, output_path):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    headers = {
        "xi-api-key": API_KEY_11LABS,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "voice": VOICE_ID,
        "model": "eleven_monolingual_v1"
    }
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(response.content)
        print(f"✅ Audio saved to {output_path}")
    else:
        print("ElevenLabs TTS error!")
        print("STATUS:", response.status_code)
        print("BODY:", response.text)

# ---------------- FILE SELECTION ----------------
def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

# ---------------- MAIN FUNCTION ----------------
def main():
    print("Select a student notes PDF to convert...")
    pdf_path = select_file()
    if not pdf_path:
        print("No file selected. Exiting.")
        return

    print("\nExtracting text from PDF...")
    notes_text = extract_text_from_pdf(pdf_path)
    print("Original Notes Extracted!\n")

    chunks = chunk_text(notes_text)
    print(f"Text split into {len(chunks)} chunk(s) for processing.\n")

    genz_text = ""
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)}...")
        result = gemini_translate_to_genz(chunk)
        genz_text += result + "\n\n"

    # Save Gen Z text
    output_txt_path = os.path.join(os.path.dirname(pdf_path), "genz_notes.txt")
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(genz_text)
    print(f"\n✅ Gen Z Brain-Rot Version saved to {output_txt_path}")

    # ---------------- TTS ----------------
    # Instead of calling TTS once, split into smaller chunks
    for i, chunk in enumerate(chunk_text(genz_text, 500)):  # 500 chars per TTS chunk
        output_chunk_path = os.path.join(os.path.dirname(pdf_path), f"genz_notes_{i+1}.mp3")
        elevenlabs_tts_full(chunk, output_chunk_path, api_key=API_KEY_11LABS, voice_id=VOICE_ID)


if __name__ == "__main__":
    main()
