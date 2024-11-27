# -*- coding: utf-8 -*-

# Standard Library Imports
import json
import sys
import subprocess
import zipfile
import shutil
import threading
import os
import mimetypes
import tkinter as tk
from tkinter import Menu, messagebox
from urllib.parse import urlparse
import webbrowser

# Third-Party Imports
import cv2
import pyperclip
import requests
from PIL import Image, ImageTk

# Local Imports
from secondaryWindow import open_secondary_window
from nested_menu import (
    convert_ontology_categories_for_nested_button,
    hierarchy_structure,
    organize_images_for_nested_menu
)
from prepare_project import check_config_file, create_required_folders, download_json_file
from play_video import play_video
from download_test_data import download_test_data
from download_test_results import download_and_unzip_results
from email_button import setup_email_frame, copy_email
from docker_manager_button import open_docker_manager_wrapper

# Global Variable for Docker Images
imagens_docker = None
selected_image = None

# Function to perform the pull of Docker manager
def pull_docker_image():
    try:
        # Run the docker pull command
        result = subprocess.run(["docker", "pull", "pegi3s/docker-manager"], capture_output=True, text=True, check=True)
        # Output the result if the command was successful
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        # Handle errors in case the command fails
        print("An error occurred:", e.stderr)

# Function to Load Docker Images from JSON File
def load_docker_images(json_file_path='JSON'):
    global imagens_docker
    with open(json_file_path, 'rb') as file:
        imagens_docker = json.load(file)

# Functions for UI Setup
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_screen = (screen_width - width) // 2
    y_screen = ((screen_height - height) // 2) - 50
    window.geometry(f"{width}x{height}+{x_screen}+{y_screen}")

def open_link(event):
    webbrowser.open("https://pegi3s.github.io/dockerfiles/")

def show_warning():
    messagebox.showwarning("Missing info", "Missing info")

def handle_image_selection(image_name):
    global selected_image
    if image_data := next((img for img in imagens_docker if img["name"] == image_name), None):
        update_ui_for_image(image_data)
    else:
        messagebox.showwarning("Warning", "Selected image not found in JSON.")

def update_ui_for_image(image_data):
    global selected_image
    selected_image = image_data["name"]
    doc_button.config(command=lambda: webbrowser.open(image_data["manual_url"]))
    pegi3s_button.config(command=lambda: webbrowser.open(image_data["pegi3s_url"]))
    github_button.config(command=lambda: webbrowser.open(image_data["github_url"]))
    title_label.config(text=selected_image)
    description_label.config(text=image_data["description"], wraplength=800)
    place_buttons()

def open_secondary_window_wrapper():
    open_secondary_window(selected_image)

def show_context_menu(event):
    context_category_menu.tk_popup(event.x_root, event.y_root)

def update_button_text(option):
    onthology_button.config(text=option)
    if option == "Select an image":
        title_label.config(text="")
        description_label.config(text="")
    else:
        handle_image_selection(option)

def create_submenu(parent_menu, options, max_options=20):
    root_menu = Menu(parent_menu, tearoff=0)
    submenu = root_menu

    count_options = 0
    for option in options:
        count_options += 1

        if count_options >= max_options:
            new_submenu = Menu(submenu, tearoff=0)
            submenu.add_separator()
            submenu.add_cascade(label="More...", menu=new_submenu)
            submenu = new_submenu

            count_options = 0

        if isinstance(option, dict):
            for key, value in option.items():
                submenu.add_cascade(label=key, menu=create_submenu(submenu, value, max_options))
        else:
            submenu.add_command(label=option, command=lambda opt=option: update_button_text(opt))

    return root_menu

def fetch_data_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content.decode("utf-8")
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return ""

# Event Handlers
def on_enter(event):
    title_label.config(fg="#3498db", font=("sans-serif", 40, "underline"))

def on_leave(event):
    title_label.config(fg="black", font=("sans-serif", 40))

def place_buttons():
    doc_button.place(relx=0.98, rely=0.3, anchor=tk.E)
    pegi3s_button.place(relx=0.98, rely=0.35, anchor=tk.E)
    github_button.place(relx=0.98, rely=0.4, anchor=tk.E)
    test_data_button.place(relx=0.35, rely=0.815, anchor=tk.CENTER)
    results_button.place(relx=0.65, rely=0.815, anchor=tk.CENTER)
    run_file_button.place(relx=0.5, rely=0.815, anchor=tk.CENTER)

# Main Application Setup
if __name__ == "__main__":
    # Initial Configuration Checks
    check_config_file()
    create_required_folders()
    download_json_file()
    load_docker_images()

    # pull docker-manager image
    pull_docker_image()

    # Create Main Window
    window = tk.Tk()
    window.title("Run and manage Docker Images")
    center_window(window, width=1600, height=900)

    # UI Elements
    # Title and Subtitle
    blue_box_frame = tk.Frame(window, bg="#007bff")
    blue_box_frame.place(relx=0, rely=0, relwidth=1, relheight=0.25)
    blue_box_frame_bot = tk.Frame(window, bg="#007bff")
    blue_box_frame_bot.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)
    greeting = tk.Label(blue_box_frame, text="Run Docker Images like a Pro!", fg="white", font=("sans-serif", 30), background="#007bff")
    subtitle = tk.Label(blue_box_frame, text="Bioinformatics Docker Images Project", fg="white", font=("sans-serif", 15), background="#007bff")
    greeting.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
    subtitle.place(relx=0.5, rely=0.35, anchor=tk.CENTER)

    # Logo
    logo_image = Image.open("pegi3s_logo.png").resize((90, 90), Image.ANTIALIAS)
    i3s_image = ImageTk.PhotoImage(logo_image)
    logo_label = tk.Label(blue_box_frame, image=i3s_image, cursor="hand2")
    logo_label.image = i3s_image
    logo_label.bind("<Button-1>", open_link)
    logo_label.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    # Ontology Data Fetching
    obo_text_data = fetch_data_from_url("https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/dio.obo")
    diaf_text_data = fetch_data_from_url("https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/dio.diaf")

    # Ontology Menu Creation
    onthology_sorted_categories = hierarchy_structure(obo_text_data)
    categories_nested_menu = convert_ontology_categories_for_nested_button(onthology_sorted_categories)
    images_nested_menu = organize_images_for_nested_menu(diaf_text_data, categories_nested_menu)

    # Context Menu Setup
    context_category_menu = Menu(window, tearoff=0)
    for option in images_nested_menu:
        if isinstance(option, dict):
            for key, value in option.items():
                context_category_menu.add_cascade(label=key, menu=create_submenu(context_category_menu, value))
        else:
            context_category_menu.add_command(label=option, command=lambda opt=option: update_button_text(opt))

    onthology_button = tk.Button(window, text="Select an image", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised")
    onthology_button.place(relx=0.1, rely=0.3, anchor=tk.CENTER)
    onthology_button.bind("<Button-1>", show_context_menu)

    # Set uniform button width and height for doc, github and pegi3s buttons
    button_width = 16
    button_height = 1

    # Create buttons with consistent width and height
    doc_button = tk.Button(window, text="Open Documentation", command=show_warning, bg="#3498db", fg="white",
                           font=("Helvetica", 10, "bold"), relief="raised", width=button_width, height=button_height)
    github_button = tk.Button(window, text="Open Github", bg="#3498db", fg="white",
                           font=("Helvetica", 10, "bold"), relief="raised", width=button_width, height=button_height)
    pegi3s_button = tk.Button(window, text="Open pegi3s", command=show_warning, bg="#3498db", fg="white",
                           font=("Helvetica", 10, "bold"), relief="raised", width=button_width, height=button_height)

    # Remaining Application Buttons
    test_data_button = tk.Button(window, text="Test Data", command=lambda: download_test_data(selected_image), bg="#3498db", fg="white", font=("Helvetica", 10, "bold"))
    results_button = tk.Button(window, text="Test Data Results", command=lambda: download_and_unzip_results(selected_image), bg="#3498db", fg="white", font=("Helvetica", 10, "bold"))
    run_file_button = tk.Button(window, text="Open Run Page", command=open_secondary_window_wrapper, bg="#3498db", fg="white", font=("Helvetica", 10, "bold"))

    # Additional GUI Elements
    title_label = tk.Label(window, text="", fg="black", font=("sans-serif", 40))
    title_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

    # Dropdown menu button
    description_label = tk.Label(window, fg="black", font=("sans-serif", 14), state="disabled")
    description_label.place(relx=0.5, rely=0.37, anchor=tk.N, width=800)

    # Additional Functions
    play_video(window, "docker_explainVideo.mp4")  # Replace with the appropriate video path
    setup_email_frame(window)

    # Docker Manager Button
    docker_manager_button = tk.Button(window, text="docker-manager", font=("Helvetica", 14, "bold"), command=open_docker_manager_wrapper, width=250, height=150, bg="white")
    docker_manager_button.place(relx=0.7, rely=0.865, relwidth=0.15, relheight=0.12)

    # Start the main loop
    window.mainloop()
