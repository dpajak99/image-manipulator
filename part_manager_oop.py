import tkinter as tk
from tkinter import messagebox
from db import Database

# Instanciate databse object
db = Database('store.db')

# Main Application/GUI class


class Application(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        master.title('Part Manager')
        # Width height
        master.geometry("700x350")

root = tk.Tk()
app = Application(master=root)
app.mainloop()
