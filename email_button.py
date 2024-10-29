# defines the "Contact us" button in main window 

import tkinter as tk
import pyperclip

#from main_file import copy_email, open_docker_manager_wrapper  # Import any needed functions

def setup_email_frame(window):
    # Creates a frame for the email box
    email_frame = tk.Frame(window, bg="white", bd=2, relief="groove", width=250, height=150)
    email_frame.place(relx=0.2, rely=0.865, relwidth=0.15, relheight=0.12)

    # Email label
    email_label = tk.Label(email_frame, text="Contact Us", bg="white", padx=5, pady=2, font=("Helvetica", 14, "bold"), fg="black")
    email_label.place(relx=0.5, rely=0.15, anchor="center")

    # Email address
    email_address = tk.Label(email_frame, text="pegi3sdocker@gmail.com", bg="white", padx=5, pady=2)
    email_address.place(relx=0.5, rely=0.4, anchor="center")

    # Button
    email_button = tk.Button(email_frame, text="Copy Email", bg="#007bff", fg="white", padx=10, pady=2, command=copy_email)
    email_button.place(relx=0.5, rely=0.75, anchor="center")
    
def copy_email():
    email = "pegi3sdocker@gmail.com"
    pyperclip.set_clipboard("xclip")
    pyperclip.copy(email)
