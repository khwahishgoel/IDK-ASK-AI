import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import PyPDF2
import requests

load_dotenv()
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

API_KEY_GEMINI = "AIzaSyDcUVVpt4d_xqHuQQsAZrVPLognTnQKDSs"
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"

CHUNK_SIZE = 1000

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def extract_text_from_pdf(path):
    text = ""
    try:
        with open(path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        return f"Error reading PDF: {e}"
    return text

def chunk_text(text, chunk_size=CHUNK_SIZE):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def gemini_translate_to_genz(text):
    if not API_KEY_GEMINI:
        return "[API key not configured - set GEMINI_API_KEY in Secrets]"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": "AIzaSyDcUVVpt4d_xqHuQQsAZrVPLognTnQKDSs"
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
        return f"[API Error: {response.status_code}]"
    try:
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return "[Empty response from API]"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded bestie'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected fr fr'}), 400
    
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({'error': 'Only PDFs allowed, no cap'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    
    try:
        text = extract_text_from_pdf(filepath)
        if text.startswith("Error"):
            return jsonify({'error': text}), 400
        
        chunks = chunk_text(text)
        genz_text = ""
        
        for chunk in chunks:
            result = gemini_translate_to_genz(chunk)
            genz_text += result + "\n\n"
        
        os.remove(filepath)
        
        return jsonify({
            'success': True,
            'original': text[:500] + "..." if len(text) > 500 else text,
            'converted': genz_text
        })
    except Exception as e:
        return jsonify({'error': f'Something went wrong: {str(e)}'}), 500

@app.route('/health')
def health():
    return jsonify({'status': 'vibing', 'api_configured': bool(API_KEY_GEMINI)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5005, debug=False)
