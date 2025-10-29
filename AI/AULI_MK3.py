import os
import tkinter as tk
from tkinter import scrolledtext
import threading
import pyttsx3
import speech_recognition as sr
import webbrowser
import datetime
from openai import OpenAI

# ==================== CONFIGURATION ====================
OPENROUTER_API_KEY = "sk-or-v1-API KEY HERE"

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('voice', engine.getProperty('voices')[1].id)  # female-like voice


# ==================== CORE FUNCTIONS ====================
def speak(text):
    chat_box.configure(state='normal')
    chat_box.insert(tk.END, f"\n🟢 AULI: ", "auli_tag")
    chat_box.insert(tk.END, text + "\n", "auli_text")
    chat_box.configure(state='disabled')
    chat_box.see(tk.END)
    engine.say(text)
    engine.runAndWait()


def chat_with_deepseek(prompt):
    try:
        response = client.chat.completions.create(
            model="tngtech/deepseek-r1t2-chimera:free",
            timeout=25,
            messages=[
                {"role": "system", "content": "You are AULI, a multilingual intelligent desktop AI assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error communicating with DeepSeek API: {e}"


def process_command(query):
    query = query.lower().strip()

    # --- Smart Website Opener ---
    if ".com" in query or ".in" in query or ".org" in query:
        site = query.split()[-1]
        if not site.startswith("http"):
            site = "https://" + site
        webbrowser.open(site)
        speak(f"Opening {site}.")
        return

    # --- Basic commands ---
    if "open youtube" in query:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube.")
    elif "open google" in query:
        webbrowser.open("https://google.com")
        speak("Opening Google.")
    elif "open instagram" in query:
        webbrowser.open("https://instagram.com")
        speak("Opening Instagram.")
    elif "open facebook" in query:
        webbrowser.open("https://facebook.com")
        speak("Opening Facebook.")
    elif "open twitter" in query or "open x" in query:
        webbrowser.open("https://twitter.com")
        speak("Opening Twitter.")
    elif "open linkedin" in query:
        webbrowser.open("https://linkedin.com")
        speak("Opening LinkedIn.")
    elif "time" in query:
        current_time = datetime.datetime.now().strftime("%I:%M %p")
        speak(f"The time is {current_time}.")
    elif any(word in query for word in ["exit", "stop", "quit", "close"]):
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
            chat_box.configure(state='normal')
            chat_box.insert(tk.END, f"\n🟣 You: ", "user_tag")
            chat_box.insert(tk.END, query + "\n", "user_text")
            chat_box.configure(state='disabled')
            chat_box.see(tk.END)
            process_command(query)
        except sr.WaitTimeoutError:
            speak("No speech detected.")
        except Exception:
            speak("Sorry, I didn't catch that. Please repeat.")


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
root.geometry("850x650")
root.configure(bg="#0f172a")

# Rounded window corners and drop shadow
root.wm_attributes('-alpha', 0.98)
root.wm_attributes("-topmost", False)

# ==================== HEADER ====================
header = tk.Label(
    root,
    text="💫 AULI - Your Smart Desktop Assistant",
    font=("Poppins SemiBold", 20, "bold"),
    bg="#0f172a",
    fg="#00ffc6",
    pady=15
)
header.pack(fill=tk.X)

# ==================== CHAT BOX ====================
chat_box = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    bg="#141b2d",
    fg="#e0e0e0",
    font=("Consolas", 12),
    padx=15,
    pady=15,
    relief=tk.FLAT
)
chat_box.pack(padx=20, pady=15, fill=tk.BOTH, expand=True)
chat_box.tag_config("user_tag", foreground="#00b4d8", font=("Consolas", 12, "bold"))
chat_box.tag_config("user_text", foreground="#caf0f8")
chat_box.tag_config("auli_tag", foreground="#00ffb3", font=("Consolas", 12, "bold"))
chat_box.tag_config("auli_text", foreground="#ade8f4")
chat_box.configure(state='disabled')

# ==================== INPUT FRAME ====================
input_frame = tk.Frame(root, bg="#0f172a")
input_frame.pack(fill=tk.X, padx=20, pady=10)

user_input = tk.Entry(
    input_frame,
    font=("Consolas", 13),
    bg="#1e293b",
    fg="#ffffff",
    insertbackground="#ffffff",
    relief=tk.FLAT,
    bd=4
)
user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15), ipady=8)

send_btn = tk.Button(
    input_frame,
    text="➤ Send",
    font=("Poppins SemiBold", 12, "bold"),
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
    text="🎤 Speak",
    font=("Poppins SemiBold", 12, "bold"),
    bg="#38bdf8",
    fg="#0f172a",
    activebackground="#0ea5e9",
    activeforeground="white",
    relief=tk.FLAT,
    command=start_listening_thread
)
voice_btn.pack(side=tk.LEFT, ipadx=10, ipady=6)

# ==================== GREETING ====================
speak("Hello Madhav! I'm AULI — your personal AI desktop assistant. How can I help you today?")

root.mainloop()

