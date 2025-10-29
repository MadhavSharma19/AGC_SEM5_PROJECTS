import os
import tkinter as tk
from tkinter import scrolledtext
import threading
import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
from openai import OpenAI
import subprocess
import time

# ==================== CONFIGURATION ====================
OPENROUTER_API_KEY = "sk-or-v1-API KEY HERE"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('voice', engine.getProperty('voices')[1].id)  # female voice


# ==================== SPEAK FUNCTION ====================
def speak(text):
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, f"\n🟢 AULI: ", "auli_tag")
    chat_box.insert(tk.END, text + "\n", "auli_text")
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)
    engine.say(text)
    engine.runAndWait()


# ==================== AI CHAT RESPONSE ====================
def chat_with_auli(prompt):
    try:
        response = client.chat.completions.create(
            model="tngtech/deepseek-r1t2-chimera:free",
            messages=[
                {"role": "system", "content": "You are AULI, a multilingual smart desktop assistant."},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"


# ==================== OPEN APPLICATIONS ====================
def open_application(app_name):
    app_name = app_name.lower()
    paths = {
        "word": r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
        "excel": r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
        "powerpoint": r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE",
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "vs code": r"C:\Users\asus\AppData\Local\Programs\Microsoft VS Code\Code.exe",
        "notepad": "notepad.exe",
        "paint": "mspaint.exe",
        "calculator": "calc.exe",
        "file explorer": "explorer.exe",
        "command prompt": "cmd.exe",
        "edge": r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    }

    for key, path in paths.items():
        if key in app_name:
            try:
                os.startfile(path)
                speak(f"Opening {key} for you.")
                return True
            except Exception as e:
                speak(f"Sorry, I couldn’t open {key}. Error: {e}")
                return True
    return False


# ==================== COMMAND HANDLER ====================
def process_command(query):
    query = query.lower().strip()

    # Open applications
    if "open" in query:
        app_name = query.replace("open", "").strip()
        if open_application(app_name):
            return

    # Play Music
    elif "play music" in query:
        speak("What’s your favorite song, Madhav?")
        song = listen_once()
        if song:
            speak(f"Playing {song} on YouTube.")
            webbrowser.open(f"https://www.youtube.com/results?search_query={song}")
        else:
            speak("I couldn’t hear your favorite song.")
        return

    # Time & Date
    elif "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")
        return

    elif "date" in query:
        current_date = datetime.date.today().strftime("%B %d, %Y")
        speak(f"Today’s date is {current_date}.")
        return

    # Websites
    elif "open youtube" in query:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube.")
        return
    elif "open google" in query:
        webbrowser.open("https://google.com")
        speak("Opening Google.")
        return
    elif "open gmail" in query:
        webbrowser.open("https://mail.google.com")
        speak("Opening Gmail.")
        return

    # System commands
    elif "shutdown" in query:
        speak("Shutting down the system in 10 seconds.")
        os.system("shutdown /s /t 10")
        return
    elif "restart" in query:
        speak("Restarting your system now.")
        os.system("shutdown /r /t 5")
        return

    # Exit
    elif any(word in query for word in ["exit", "quit", "close auli", "stop"]):
        speak("Goodbye Madhav! Have a great day.")
        root.destroy()
        return

    # Otherwise, ask AI
    else:
        response = chat_with_auli(query)
        speak(response)


# ==================== VOICE RECOGNITION ====================
def listen_once():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        try:
            audio = recognizer.listen(source, timeout=5)
            return recognizer.recognize_google(audio)
        except Exception:
            return None


def listen_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        speak("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5)
            query = recognizer.recognize_google(audio)
            chat_box.configure(state='normal')
            chat_box.insert(tk.END, f"\n🟣 You: ", "user_tag")
            chat_box.insert(tk.END, query + "\n", "user_text")
            chat_box.configure(state='disabled')
            chat_box.see(tk.END)
            process_command(query)
        except sr.WaitTimeoutError:
            speak("No speech detected.")
        except Exception:
            speak("Sorry, I didn’t catch that.")


# ==================== UI FUNCTIONS ====================
def send_text():
    query = user_input.get()
    if not query.strip():
        return
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, f"\n🟣 You: ", "user_tag")
    chat_box.insert(tk.END, query + "\n", "user_text")
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)
    user_input.delete(0, tk.END)
    threading.Thread(target=lambda: process_command(query)).start()


def start_listening_thread():
    threading.Thread(target=listen_voice).start()


# ==================== UI SETUP ====================
root = tk.Tk()
root.title("AULI - Your Desktop AI Assistant")
root.geometry("900x700")
root.configure(bg="#05081a")

# Header
header = tk.Label(
    root,
    text="✨ AULI - Your Smart Desktop AI Assistant",
    font=("Poppins SemiBold", 22, "bold"),
    bg="#05081a",
    fg="#00ffc6",
    pady=20
)
header.pack(fill=tk.X)

# Chat Box
chat_box = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    bg="#0a1124",
    fg="#e0e0e0",
    font=("Consolas", 12),
    padx=20,
    pady=20,
    relief=tk.FLAT
)
chat_box.pack(padx=25, pady=15, fill=tk.BOTH, expand=True)
chat_box.tag_config("user_tag", foreground="#00b4d8", font=("Consolas", 12, "bold"))
chat_box.tag_config("user_text", foreground="#caf0f8")
chat_box.tag_config("auli_tag", foreground="#00ffb3", font=("Consolas", 12, "bold"))
chat_box.tag_config("auli_text", foreground="#ade8f4")
chat_box.configure(state='disabled')

# Input Frame
input_frame = tk.Frame(root, bg="#05081a")
input_frame.pack(fill=tk.X, padx=20, pady=10)

user_input = tk.Entry(
    input_frame,
    font=("Consolas", 13),
    bg="#101b33",
    fg="#ffffff",
    insertbackground="#00ffc6",
    relief=tk.FLAT,
    bd=5
)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15), ipady=8)

send_btn = tk.Button(
    input_frame,
    text="🚀 Send",
    font=("Poppins SemiBold", 12),
    bg="#00ffc6",
    fg="#0f172a",
    activebackground="#0ea5e9",
    activeforeground="white",
    relief=tk.FLAT,
    command=send_text
)
send_btn.pack(side=tk.LEFT, padx=5, ipadx=15, ipady=6)

voice_btn = tk.Button(
    input_frame,
    text="🎙 Speak",
    font=("Poppins SemiBold", 12),
    bg="#38bdf8",
    fg="#0f172a",
    activebackground="#0ea5e9",
    activeforeground="white",
    relief=tk.FLAT,
    command=start_listening_thread
)
voice_btn.pack(side=tk.LEFT, ipadx=10, ipady=6)

speak("Hello Madhav! I’m AULI — your futuristic AI assistant. I can open apps, play music, and chat with you anytime.")

root.mainloop()

