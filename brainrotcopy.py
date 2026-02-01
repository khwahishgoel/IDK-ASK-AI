import os
import PyPDF2
import requests
import json
import tkinter as tk
from tkinter import filedialog
from dotenv import load_dotenv

load_dotenv()

# ===================== CONFIG =====================
API_KEY=os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("⚠️ Gemini API key not found! Check your .env file.")



# Replace this with a model from your ListModels output that supports "generateContent"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

CHUNK_SIZE = 1000  # smaller chunks to prevent empty API responses
# ==================================================

def extract_text_from_pdf(path):
    """
    Extracts text from a PDF file or all PDFs in a folder.
    """
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
    """
    Splits text into smaller chunks to avoid token limits.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def gemini_translate_to_genz(text):
    """
    Sends text to Gemini API and returns Gen Z brainrot version.
    """
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY
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

    data = response.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        print("⚠️ Gemini returned empty output for this chunk.")
        return ""

def select_file():
    """
    Opens a file picker dialog for the user to select a PDF.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the main Tk window
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )
    return file_path

def main():
    if not API_KEY:
        raise ValueError("⚠️ Gemini API key not found! Check your .env file.")

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

    # Save output next to the PDF
    output_path = os.path.join(os.path.dirname(pdf_path), "genz_notes.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(genz_text)

    print(f"\n✅ Gen Z Brain-Rot Version saved to {output_path}")

if __name__ == "__main__":
    main()
