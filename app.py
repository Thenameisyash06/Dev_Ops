import speech_recognition as sr
import subprocess
import pyautogui
import time
import re
import sys
from datetime import datetime
import pygetwindow as gw
import os
import pygame
import threading
import tkinter as tk
from tkinter import messagebox

recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.0
recognizer.energy_threshold = 300
pygame.mixer.init()

mic_index = 1
listening = False

music_dir = os.path.join(os.path.expanduser("~"), "Music")
playlist = [os.path.join(music_dir, f) for f in os.listdir(music_dir) if f.lower().endswith(".mp3")]
playlist.sort()
current_index = 0

def play_song(index):
    global current_index
    if 0 <= index < len(playlist):
        pygame.mixer.music.load(playlist[index])
        pygame.mixer.music.play()
        print("Now playing:", os.path.basename(playlist[index]))
        current_index = index

def next_song():
    global current_index
    if current_index < len(playlist) - 1:
        current_index += 1
        play_song(current_index)
    else:
        print("End of playlist.")

def previous_song():
    global current_index
    if current_index > 0:
        current_index -= 1
        play_song(current_index)
    else:
        print("Already at the beginning.")

def focus_notepad():
    try:
        for window in gw.getAllWindows():
            if 'notepad' in window.title.lower():
                window.minimize()
                window.restore()
                window.activate()
                time.sleep(0.5)
                return
        print("Notepad window not found.")
    except Exception as e:
        print("Error focusing Notepad:", e)

def play_first_music(source):
    if not playlist:
        print("No MP3 files found in Music folder.")
        return

    play_song(0)

    while True:
        print("Voice Music command: pause, resume, stop, next song, previous song")
        try:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio).lower()

            if "pause" in text:
                pygame.mixer.music.pause()
                print("Music Paused!")
            elif "resume" in text:
                pygame.mixer.music.unpause()
                print("Music Resumed!")
            elif "stop" in text:
                pygame.mixer.music.stop()
                print("Music Stopped!")
                break
            elif "next song" in text:
                next_song()
            elif "previous song" in text:
                previous_song()

        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print("API error:", e)

def notepad_mode(source):
    subprocess.Popen(['notepad.exe'])
    time.sleep(2)
    print("Notepad opened. Start speaking...")

    while listening:
        try:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio).lower()
            print("You said:", text)

            if text == "exit":
                focus_notepad()
                return

            elif re.match(r'^save.*', text):
                focus_notepad()
                pyautogui.hotkey("ctrl", "s")
                time.sleep(1)
                filename = datetime.now().strftime("note_%Y%m%d_%H%M%S.txt")
                pyautogui.write(filename)
                pyautogui.press("enter")

            else:
                focus_notepad()
                pyautogui.write(text + '. ', interval=0.05)

        except sr.UnknownValueError:
            print("Could not understand audio.")
        except sr.RequestError as e:
            print("API error:", e)

def voice_assistant_loop():
    global listening
    with sr.Microphone(device_index=mic_index) as source:
        while listening:
            print("Say 'open notepad' or 'play music'...")
            try:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = recognizer.listen(source)
                command = recognizer.recognize_google(audio).lower()
                print("Command:", command)

                if "open notepad" in command:
                    notepad_mode(source)

                elif "play music" in command:
                    play_first_music(source)

                elif "exit" in command:
                    stop_listening()
                    break

            except sr.UnknownValueError:
                print("Could not understand.")
            except sr.RequestError as e:
                print("API Error:", e)

# ------------------ GUI Setup ------------------
def start_listening():
    global listening
    if not listening:
        listening = True
        thread = threading.Thread(target=voice_assistant_loop)
        thread.daemon = True
        thread.start()
        status_label.config(text="Status: Listening...")

def stop_listening():
    global listening
    listening = False
    status_label.config(text="Status: Stopped")
    pygame.mixer.music.stop()

def exit_app():
    stop_listening()
    root.destroy()

root = tk.Tk()
root.title("Voice Assistant")
root.geometry("400x300")
root.resizable(False, False)

title_label = tk.Label(root, text="Voice Assistant", font=("Arial", 16))
title_label.pack(pady=10)

start_btn = tk.Button(root, text="Start Listening", command=start_listening, width=20, bg="green", fg="white")
start_btn.pack(pady=5)

stop_btn = tk.Button(root, text="Stop Listening", command=stop_listening, width=20, bg="orange", fg="white")
stop_btn.pack(pady=5)

exit_btn = tk.Button(root, text="Exit", command=exit_app, width=20, bg="red", fg="white")
exit_btn.pack(pady=5)

status_label = tk.Label(root, text="Status: Idle", font=("Arial", 12))
status_label.pack(pady=10)

root.mainloop()
