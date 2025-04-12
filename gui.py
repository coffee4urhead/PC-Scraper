import tkinter as tk
from PIL import Image, ImageTk
from scraper import begin_scraping
import pygame

root = tk.Tk()
root.title("GUI App for Scraping General GPU Information")
root.geometry("1200x700")

image = Image.open("./images/elf.jpg")
resized_image = image.resize((1200, 700), Image.Resampling.LANCZOS)
background_image = ImageTk.PhotoImage(resized_image)

canvas = tk.Canvas(root, width=1200, height=700, highlightthickness=0)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=background_image, anchor="nw")

label1 = tk.Label(root, text="GPU Web Scraper Program", font=("Comic Sans MS", 16, "bold"), )
label1_window = canvas.create_window(600, 50, anchor="center", window=label1)

label2 = tk.Label(root, text="Search GPU model to scrape information:", font=("Comic Sans MS", 12))
label2_window = canvas.create_window(400, 120, anchor="center", window=label2)

def on_key_press(event):
    enter_pressed_value = entry.get()
    begin_scraping(enter_pressed_value)

entry = tk.Entry(root, width=30, font=("Comic Sans MS", 13, "italic"))
root.bind("<Return>", on_key_press)
entry_window = canvas.create_window(750, 120, anchor="center", window=entry)

def on_submit():
    user_submit_value = entry.get()
    begin_scraping(user_submit_value)

submit_button = tk.Button(root, text="Submit", command=on_submit, width=7, font=("Comic Sans MS", 13, "bold"), height = 1, cursor="hand2", padx=10, pady=5)
submit_button_window = canvas.create_window(650, 180, anchor="center", window=submit_button)

quit_button = tk.Button(root, text="Quit", command=root.destroy, width=7, font=("Comic Sans MS", 13, "bold"), height = 1, cursor="hand2", padx=10, pady=5)
quit_button_window = canvas.create_window(850, 180, anchor="center", window=quit_button)

pygame.mixer.init()
music_playing = False

def toggle_music():
    global music_playing
    if not music_playing:
        pygame.mixer.music.load("./Music/scraping-music.wav")
        pygame.mixer.music.play()
        play_music_button.config(text="Pause")
        music_playing = True
    else:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            play_music_button.config(text="Resume")
        else:
            pygame.mixer.music.unpause()
            play_music_button.config(text="Pause")

play_music_button = tk.Button(root, text="Play Music", command=toggle_music, width=7, font=("Comic Sans MS", 13, "bold"), height=1, cursor="hand2", padx=10, pady=5)
play_button_window = canvas.create_window(750, 180, anchor="center", window=play_music_button)

root.mainloop()
