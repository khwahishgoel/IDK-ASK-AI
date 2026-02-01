# IDK-ASK-AI

# Brainrot — Simple local README

About
This is a small project that uses environment variables to keep API keys separate from code. It provides local utilities for text-to-speech and simple app logic.

Quick setup (local)
1. Create a local `.env` file in the project root (do not commit it):
	GEMINI_API_KEY=your_real_key_here

2. Install dependencies (if any). If you're using pip and a requirements file exists, run:
	pip install -r requirements.txt

3. Run the app (example):
	python/python3 app.py
4. If you want to just run the backend:
   python/python3 brainrot.py

Config and secrets
- The project expects the GEMINI_API_KEY to be provided as an environment variable.
- For local development put your key in a `.env` file or export it in your shell.
- Do not commit your `.env` or any real API keys.

#IDKaskAI
because notes don't stick
