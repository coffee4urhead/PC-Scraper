from tkinter import *
from tkinter import ttk

root = Tk()
frm = ttk.Frame(root, padding=20)

frm.grid()

ttk.Label(frm, text="GPU Web Scraper Program").grid(column=0, row=0, columnspan=3, pady=10)

ttk.Label(frm, text="Search GPU model to scrape information:").grid(column=0, row=1, pady=10)

entry = ttk.Entry(frm, width=30)
entry.grid(column=1, row=1, padx=10)

def on_submit():
    user_input = entry.get()
    print(f"Submitted text: {user_input}")

ttk.Button(frm, text="Submit", command=on_submit).grid(column=2, row=1, padx=10)

ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=2, pady=20)

root.mainloop()
