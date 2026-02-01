import requests
from pydub import AudioSegment
import io
import os



def elevenlabs_tts_full(text, output_path, api_key, voice_id="EXAVITQu4vr4xnSDxMaL", chunk_size=500):
    """
    Convert text to speech in chunks and combine into one MP3.
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {"xi-api-key": api_key, "Content-Type": "application/json"}
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    final_audio = AudioSegment.empty()

    for i, chunk in enumerate(chunks):
        if not chunk.strip():  # skip empty chunks
            continue
        payload = {"text": chunk, "voice": voice_id, "model": "eleven_monolingual_v1"}
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200 and len(response.content) > 0:
            audio_chunk = AudioSegment.from_file(io.BytesIO(response.content), format="mp3")
            final_audio += audio_chunk
        else:
            print(f"⚠️ TTS error on chunk {i+1}: {response.text}")

    if len(final_audio) > 0:
        final_audio.export(output_path, format="mp3")
        print(f"✅ Full audio saved to {output_path}")
    else:
        print("⚠️ No audio generated. Check API key or chunk size.")
