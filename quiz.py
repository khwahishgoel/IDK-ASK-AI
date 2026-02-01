import os
import json
import random
import requests

# ---------------- Gemini API function ----------------
def gemini_generate_question(text, api_key):
    """
    Send the text to Gemini API to generate a single MCQ.
    Returns a dict: {"question": str, "options": [str], "answer": str}
    """
    url = "https://YOUR_GEMINI_ENDPOINT_HERE"  # Replace with correct endpoint
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "prompt": f"Generate a single multiple-choice question (4 options) from the following text. Return in JSON with keys 'question', 'options', 'answer'. Text: {text}",
        "max_tokens": 200
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        # Adjust this based on actual Gemini response format
        question_json = json.loads(result.get("text", "{}"))
        return question_json
    except Exception as e:
        print(f"⚠️ Gemini API error: {e}")
        return None

# ---------------- Quiz logic ----------------
def run_interactive_quiz(genz_text, gemini_api_key):
    print("\n🎮 Brain-Rot Interactive Quiz!\n")
    questions = []
    score = 0
    q_num = 1

    while True:
        question = gemini_generate_question(genz_text, gemini_api_key)
        if not question:
            print("⚠️ Failed to generate question. Try again.")
            continue

        print(f"Q{q_num}: {question['question']}")
        for idx, option in enumerate(question['options'], start=1):
            print(f"  {idx}. {option}")

        answer = input("Your answer (1-4) or 'stop' to quit: ").strip()
        if answer.lower() == "stop":
            break

        try:
            if question['options'][int(answer)-1] == question['answer']:
                print("✅ Correct!\n")
                score += 1
            else:
                print(f"❌ Wrong! Correct answer: {question['answer']}\n")
        except:
            print(f"❌ Invalid input. Correct answer: {question['answer']}\n")

        questions.append(question)
        q_num += 1

    print(f"🎉 Your Score: {score}/{len(questions)}")

    # Save questions to JSON
    output_path = "genz_quiz.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4)
    print(f"✅ Quiz saved to {output_path}")

# ---------------- Example usage ----------------
if __name__ == "__main__":
    # Example Gen Z text (replace with your Gemini output)
    sample_text = """
    Arrays store elements at contiguous memory locations.
    Linked lists consist of nodes pointing to the next node.
    Stacks follow LIFO principle.
    Queues follow FIFO principle.
    """
    gemini_api_key = os.getenv("API_KEY_GEMINI")  # Read API key from .env

    if not gemini_api_key:
        print("⚠️ Please set your Gemini API key in .env")
    else:
        run_interactive_quiz(sample_text, gemini_api_key)
