import tkinter as tk
import pyperclip

def copy_email():
    email = "uhbwi@gmail.com"
    pyperclip.copy(email)
    print("Email copied to clipboard:", email)

# Create main window
root = tk.Tk()
root.title("Email Box")
root.geometry("1280x720")

# Create frame for email box
email_frame = tk.Frame(root, bg="white", bd=2, relief="groove", width=250, height=150)
email_frame.place(relx=0.05, rely=0.75, relwidth=0.2, relheight=0.15)

# Email label
email_label = tk.Label(email_frame, text="Our Email", bg="white", padx=5, pady=5)
email_label.pack()

# Email address
email_address = tk.Label(email_frame, text="uhbwi@gmail.com", bg="white", padx=5, pady=5)
email_address.pack()

# Button
button = tk.Button(email_frame, text="Copy Email", command=copy_email, bg="blue", fg="white", padx=10, pady=3)
button.pack()

root.mainloop()
