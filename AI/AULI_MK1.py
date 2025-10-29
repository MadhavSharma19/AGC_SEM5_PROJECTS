import os
import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
from openai import OpenAI

# ============== CONFIGURATION ==============
OPENROUTER_API_KEY = "sk-or-v1-API-KEYHERE"  # 🔹 Replace with your actual key

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

engine = pyttsx3.init()
engine.setProperty('rate', 170)  # Speaking speed

# ============== SPEAK FUNCTION ==============
def speak(text):
    print(f"AULI: {text}")
    engine.say(text)
    engine.runAndWait()

# ============== LISTEN FUNCTION ==============
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)
    try:
        print("🧠 Recognizing...")
        query = r.recognize_google(audio)
        print(f"YOU: {query}\n")
        return query
    except Exception:
        speak("Sorry, I didn't catch that. Please repeat.")
        return ""

# ============== CHAT WITH DEEPSEEK ==============
def chat_with_deepseek(prompt):
    try:
        response = client.chat.completions.create(
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {"role": "system", "content": "You are AULI, a smart multilingual AI desktop assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error communicating with DeepSeek API: {e}"

# ============== MAIN LOGIC ==============
def run_auli():
    speak("Hello, I'm AULI — your personal AI desktop assistant. How can I help you today?")

    while True:
        query = listen().lower()
        if not query:
            continue

        # ========== SYSTEM COMMANDS ==========
        if "open youtube" in query:
            webbrowser.open("https://youtube.com")
            speak("Opening YouTube.")
        elif "open google" in query:
            webbrowser.open("https://google.com")
            speak("Opening Google.")
        elif "time" in query:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            speak(f"The time is {current_time}.")
        elif "exit" in query or "stop" in query or "quit" in query:
            speak("Goodbye! Have a great day.")
            break

        # ========== AI RESPONSE ==========
        else:
            response = chat_with_deepseek(query)
            speak(response)

# ============== RUN ==============
if __name__ == "__main__":
    run_auli()

