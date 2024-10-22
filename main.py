# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 09:38:13 2024

@author: diogo
"""

import json
import threading
import tkinter as tk
import webbrowser
from tkinter import Menu
from tkinter import messagebox

import cv2
import pyperclip
import requests
from PIL import Image, ImageTk

from editDockerImages import open_dockerManager
from secondaryWindow import open_secondary_window
from sortImandCatNestedMenu import convert_ontology_categories_for_nested_button
from sortImandCatNestedMenu import hierarchy_structure
from sortImandCatNestedMenu import organize_images_for_nested_menu

with open('novoJson.txt', 'rb') as file:
    imagens_docker = json.load(file)


# Opens the Dockerfiles project's page
def open_link(event):
    webbrowser.open("https://pegi3s.github.io/dockerfiles/")


def center_window(window, width, height):
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate position for the window
    x_screen = (screen_width - width) // 2
    y_screen = ((screen_height - height) // 2) - 50

    # Set geometry
    window.geometry(f"{width}x{height}+{x_screen}+{y_screen}")


def handle_image_selection(image_name):
    global selected_image

    # Lists all the image names
    image_names = [image["name"] for image in imagens_docker]
    if image_name in image_names:
        # Recovers the image's data
        image_data = next(image for image in imagens_docker if image["name"] == image_name)

        doc_button.config(command=lambda: webbrowser.open(image_data["manual_url"]))
        title_label.config(text=image_name)
        place_buttons()
        selected_image = image_name
        pegi3s_button.config(command=lambda: webbrowser.open(image_data["pegi3s_url"]))
        github_button.config(command=lambda: webbrowser.open(image_data["github_url"]))
        description_label.config(text=image_data["description"], wraplength=800)
        description_label.update()
    else:
        messagebox.showwarning("Warning", "Selected image not found in JSON.")


def show_context_menu(event):
    context_category_menu.tk_popup(event.x_root, event.y_root)


def update_button_text(option):
    onthology_button.config(text=option)
    if option == "Select an image":
        title_label.config(text="")
        description_label.config(text="")
    else:
        handle_image_selection(option)


def create_submenu(parent_menu, options):
    submenu = Menu(parent_menu, tearoff=0)
    for option in options:
        if isinstance(option, dict):
            for key, value in option.items():
                submenu.add_cascade(label=key, menu=create_submenu(submenu, value))
        else:
            submenu.add_command(label=option, command=lambda opt=option: update_button_text(opt))

    return submenu


def show_warning():
    messagebox.showwarning("Warning", "WIP")


def open_secondary_window_wrapper():
    open_secondary_window(selected_image)


def open_docker_manager_wrapper():
    open_dockerManager()


def open_test_data_page(selected_option):
    image_data = next(image for image in imagens_docker if image["name"] == selected_option)

    test_data_link = image_data["test_invocation_specific"]
    if test_data_link == "NN":
        messagebox.showwarning("Warning", "This image doesnt require test data")
    else:
        webbrowser.open(test_data_link)


def on_enter(event):
    title_label.config(fg="#3498db", font=("sans-serif", 40, "underline"))
    canvas.itemconfig(triangle_canvas, outline='#3498db', fill='#3498db')  # Change outline color of the circle


def on_leave(event):
    title_label.config(fg="black", font=("sans-serif", 40))
    canvas.itemconfig(triangle_canvas, outline='black')  # Restore outline color of the circle


def place_buttons():
    # Place the buttons
    doc_button.place(relx=0.98, rely=0.3, anchor=tk.E)
    pegi3s_button.place(relx=0.98, rely=0.35, anchor=tk.E)
    github_button.place(relx=0.98, rely=0.4, anchor=tk.E)
    test_data_button.place(relx=0.35, rely=0.815, anchor=tk.CENTER)
    results_button.place(relx=0.65, rely=0.815, anchor=tk.CENTER)
    run_file_button.place(relx=0.5, rely=0.815, anchor=tk.CENTER)
    onthology_button.place(relx=2, rely=2)
    onthology_button.bind("<Button-1>", show_context_menu)
    title_label.bind("<Button-1>", show_context_menu)
    title_label.bind("<Enter>", on_enter)
    title_label.bind("<Leave>", on_leave)
    title_label.update()
    delete_canvas(canvas)
    create_dropdown_menu_button(title_label.winfo_x(), title_label.winfo_y(), title_label.winfo_width())


# Add the canvas with the circle and the "V" inside it
def create_dropdown_menu_button(x, y, width):
    global triangle_canvas
    canvas.place(x=x + width, y=y + 10)

    # Coordinates for the inverted triangle
    points = [25, 35, 35, 15, 15, 15]

    # Draw the inverted triangle
    triangle_canvas = canvas.create_polygon(points, fill="#3498db", outline="black", width=3)

    # Bind the click event to the inverted triangle
    canvas.tag_bind(triangle_canvas, "<Button-1>", show_context_menu)
    # Bind hover events
    canvas.tag_bind(triangle_canvas, "<Enter>", on_enter)
    canvas.tag_bind(triangle_canvas, "<Leave>", on_leave)


def delete_canvas(canvas):
    canvas.delete("all")
    canvas = tk.Canvas(window, width=50, height=50)


def play_video(root, video_path):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_delay = int(1000 / fps)

    # Create the video frame
    video_frame = tk.Frame(root, width=640, height=360)  # Updated to a higher resolution
    video_frame.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

    # Configuring the video display area
    video_label = tk.Label(video_frame, cursor="hand2")
    video_label.pack()
    video_label.bind("<Button-1>", lambda e: webbrowser.open("https://www.youtube.com/@pegi3s"))

    def play():
        while True:
            for i in range(total_frames):
                ret, frame = cap.read()
                if ret:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    frame = cv2.resize(frame, (391, 220), interpolation=cv2.INTER_AREA)  # Using INTER_AREA for resizing
                    img = Image.fromarray(frame)
                    img = ImageTk.PhotoImage(image=img)

                    video_label.config(image=img)
                    video_label.image = img

                    # Frames do video (25ms entre frames / 40 fps)
                    video_label.after(frame_delay)
                    video_label.update()
                else:
                    # If frame not read properly, break the loop
                    break
            # Reset the video capture to the beginning
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Initializing video playback in a separate thread
    thread = threading.Thread(target=play)
    thread.daemon = True
    thread.start()

    # Function to stop video playback and release resources
    def stop_video():
        cap.release()
        root.destroy()

    # Binds the stop_video function to the window's close event
    root.protocol("WM_DELETE_WINDOW", stop_video)


def copy_email():
    email = "pegi3sdocker@gmail.com"
    pyperclip.set_clipboard("xclip")
    pyperclip.copy(email)
    print("Email copied to clipboard:", email)


if __name__ == "__main__":
    # Creates the window
    window = tk.Tk()
    window.title("Manage Docker Images")

    # Sets the window size
    window_width = 1600
    window_height = 900

    # Centers the window
    center_window(window, window_width, window_height)

    # Creates the top blue box
    blue_box_frame = tk.Frame(window, bg="#007bff")
    blue_box_frame.place(relx=0, rely=0, relwidth=1, relheight=0.25)

    # Creates the bottom blue box
    blue_box_frame_bot = tk.Frame(window, bg="#007bff")
    blue_box_frame_bot.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)

    # Organizes the blue boxes, adding the title and subtitle
    greeting = tk.Label(blue_box_frame, text="Bioinformatics Docker Images Project", fg="white",
                        font=("sans-serif", 30),
                        background="#007bff")
    subtitle = tk.Label(blue_box_frame, text="Phenotypic Evolution Group - IBMC/i3S", fg="white",
                        font=("sans-serif", 15),
                        background="#007bff")

    # Opens the pegi3s logo image
    image_path = "pegi3s_logo.png"
    original_image = Image.open(image_path)

    # Resize the image
    width = int(original_image.width * 0.7)
    height = int(original_image.height * 0.7)
    resized_image = original_image.resize((width, height), Image.ANTIALIAS)

    # Converts the logo image
    i3s_image = ImageTk.PhotoImage(resized_image)

    # Converts the image into a button
    logo_label = tk.Label(blue_box_frame, image=i3s_image, cursor="hand2")
    logo_label.image = i3s_image  # Keep a reference to the image to prevent it from being garbage collected
    logo_label.bind("<Button-1>", open_link)

    ############### OPENS THE ONTOLOGY FILES ########################
    ############### CATEGORY ORGANIZATION ###########################
    obo_url = "https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/dio.obo"
    obo_response = requests.get(obo_url)
    if obo_response.status_code == 200:
        # Get the content of the file as bytes
        obo_data = obo_response.content
        # If the content is text, decode it
        obo_text_data = obo_data.decode("utf-8")
    else:
        print(f"Failed to get the file. Status code: {obo_response.status_code}")

    ############### IMAGE ORGANIZATION INTO CATEGORIES ##############
    diaf_url = "https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/dio.diaf"
    diaf_response = requests.get(diaf_url)

    if diaf_response.status_code == 200:
        # Get the content of the file as bytes
        diaf_data = diaf_response.content
        # If the content is text, decode it
        diaf_text_data = diaf_data.decode("utf-8")
    else:
        print(f"Failed to get the file. Status code: {diaf_response.status_code}")

    # Nested menu creation using the categories loaded
    onthology_sorted_categories = hierarchy_structure(obo_text_data)
    categories_nested_menu = convert_ontology_categories_for_nested_button(onthology_sorted_categories)
    images_nested_menu = organize_images_for_nested_menu(diaf_text_data, categories_nested_menu)

    # Creates a button
    onthology_button = tk.Button(window, text="Select an image", bg="#3498db", fg="white",
                                 font=("Helvetica", 10, "bold"),
                                 relief="raised", width=16, height=1)
    onthology_button.pack(pady=50)

    # Creates a context menu
    context_category_menu = Menu(window, tearoff=0)

    # Populate the context menu with options from the array
    for option in images_nested_menu:
        if isinstance(option, dict):
            for key, value in option.items():
                context_category_menu.add_cascade(label=key, menu=create_submenu(context_category_menu, value))
        else:
            context_category_menu.add_command(label=option, command=lambda opt=option: update_button_text(opt))

    # Binds the button to show the context menu on left-click
    onthology_button.bind("<Button-1>", show_context_menu)

    # Application buttons
    doc_button = tk.Button(window, text="Open Documentation", command=show_warning, bg="#3498db", fg="white",
                           font=("Helvetica", 10, "bold"), relief="raised", width=16,
                           height=1)  # abre os docs das imagens
    github_button = tk.Button(window, text="Open Github", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"),
                              relief="raised", width=16, height=1)  # Abre a página do github
    pegi3s_button = tk.Button(window, text="Open pegi3s", command=show_warning, bg="#3498db", fg="white",
                              font=("Helvetica", 10, "bold"), relief="raised", width=16,
                              height=1)  # Abre a página do pegi3s da imagem
    test_data_button = tk.Button(window, text="Test Data", command=lambda: open_test_data_page(selected_image),
                                 bg="#3498db",
                                 fg="white",
                                 font=("Helvetica", 10, "bold"), relief="raised", width=16,
                                 height=1)  # Github com os ficheiros de Input
    results_button = tk.Button(window, text="Test Data Results", command=show_warning, bg="#3498db", fg="white",
                               font=("Helvetica", 10, "bold"), relief="raised", width=16,
                               height=1)  # GitHub com os resultados do programa
    run_file_button = tk.Button(window, text="Open Run Page", command=open_secondary_window_wrapper, bg="#3498db",
                                fg="white",
                                font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)

    onthology_button.place(relx=0.1, rely=0.3, anchor=tk.CENTER)
    greeting.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
    subtitle.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
    logo_label.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    # Creates the title label
    title_label = tk.Label(window, text="", fg="black", font=("sans-serif", 40))
    title_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    ############## CREATION OF A BUTTON TO SELECT A DOCKER IMAGE ####################
    canvas = tk.Canvas(window, width=50, height=50)

    description_label = tk.Label(window, fg="black", font=("sans-serif", 14), state="disabled")
    description_label.place(relx=0.5, rely=0.37, anchor=tk.N, width=800)

    play_video(window, "docker_explainVideo.mp4")  # Replace the video here

    # Creates a frame for email box
    email_frame = tk.Frame(window, bg="white", bd=2, relief="groove", width=250, height=150)
    email_frame.place(relx=0.2, rely=0.865, relwidth=0.15, relheight=0.12)

    # Email label
    email_label = tk.Label(email_frame, text="Contact Us", bg="white", padx=5, pady=2, font=("Helvetica", 14, "bold"),
                           fg="black")
    email_label.place(relx=0.5, rely=0.15, anchor="center")

    # Email address
    email_address = tk.Label(email_frame, text="pegi3sdocker@gmail.com", bg="white", padx=5, pady=2)
    email_address.place(relx=0.5, rely=0.4, anchor="center")

    # Button
    email_button = tk.Button(email_frame, text="Copy Email", bg="#007bff", fg="white", padx=10, pady=2,
                             command=copy_email)
    email_button.place(relx=0.5, rely=0.75, anchor="center")

    docker_manager_button = tk.Button(window, text="My Docker Images", command=open_docker_manager_wrapper, width=250,
                                      height=150, bg="white")
    docker_manager_button.place(relx=0.7, rely=0.865, relwidth=0.15, relheight=0.12)

    window.mainloop()
