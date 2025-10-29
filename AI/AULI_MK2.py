import os
import tkinter as tk
from tkinter import scrolledtext
import threading
import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
from openai import OpenAI

# ============== CONFIGURATION ==============
OPENROUTER_API_KEY = "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"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

engine = pyttsx3.init()
engine.setProperty('rate', 175)

# ============== CORE FUNCTIONS ==============
def speak(text):
    text_box.insert(tk.END, f"AULI: {text}\n\n")
    text_box.see(tk.END)
    engine.say(text)
    engine.runAndWait()

def chat_with_deepseek(prompt):
    try:
        response = client.chat.completions.create(
            model="tngtech/deepseek-r1t2-chimera:free",
            timeout=25,  # prevent hanging forever
            messages=[
                {"role": "system", "content": "You are AULI, a multilingual desktop AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error communicating with DeepSeek API: {e}"

def process_command(query):
    query = query.lower()

    if "open youtube" in query:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube.")
    elif "open google" in query:
        webbrowser.open("https://google.com")
        speak("Opening Google.")
    elif "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}.")
    elif any(word in query for word in ["exit", "stop", "quit"]):
        speak("Goodbye! Have a great day.")
        root.destroy()
    else:
        response = chat_with_deepseek(query)
        speak(response)

def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio)
            text_box.insert(tk.END, f"You: {query}\n")
            text_box.see(tk.END)
            process_command(query)
        except sr.WaitTimeoutError:
            speak("No speech detected.")
        except Exception:
            speak("Sorry, I didn't catch that. Please repeat.")

def send_text():
    query = user_input.get()
    if not query.strip():
        return
    text_box.insert(tk.END, f"You: {query}\n")
    user_input.delete(0, tk.END)
    threading.Thread(target=lambda: process_command(query)).start()

def start_listening_thread():
    threading.Thread(target=listen_voice).start()

# ============== TKINTER UI SETUP ==============
root = tk.Tk()
root.title("AULI - Your Desktop AI Assistant")
root.geometry("700x600")
root.configure(bg="#101820")

# ============== CHAT WINDOW ==============
text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, bg="#1a1f2b", fg="#00ffcc",
                                     font=("Consolas", 12), padx=10, pady=10, relief=tk.FLAT)
text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# ============== INPUT FRAME ==============
frame = tk.Frame(root, bg="#101820")
frame.pack(fill=tk.X, padx=10, pady=10)

user_input = tk.Entry(frame, font=("Consolas", 12), bg="#1a1f2b", fg="white",
                      insertbackground="white", relief=tk.FLAT)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

send_btn = tk.Button(frame, text="Send", font=("Consolas", 12, "bold"),
                     bg="#00ffcc", fg="#101820", relief=tk.FLAT, command=send_text)
send_btn.pack(side=tk.LEFT, padx=5)

voice_btn = tk.Button(frame, text="🎤 Speak", font=("Consolas", 12, "bold"),
                      bg="#00ccff", fg="black", relief=tk.FLAT, command=start_listening_thread)
voice_btn.pack(side=tk.LEFT)

# Greeting
speak("Hello, I'm AULI — your personal AI desktop assistant. How can I help you today?")

root.mainloop()
