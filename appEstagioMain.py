# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 09:38:13 2024

@author: diogo
"""

import tkinter as tk
import webbrowser
import subprocess
import json
from tkinter import messagebox
from tkinter import Menu
from PIL import Image, ImageTk
from secondaryWindow import open_secondary_window
from editDockerImages import open_dockerManager
from sortImandCatNestedMenu import hierarchy_structure
from sortImandCatNestedMenu import convert_CatOntToNestedMenu
from sortImandCatNestedMenu import organize_images_Nested_Menu
import cv2
import threading
import pyperclip
import requests

# Acrescentar /data à frente do os.getcwd() para passar a funcionar as imagens docker
# Carregar o JSON
# json_url = "https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/metadata.json"
# json_response= requests.get(json_url)

# if json_response.status_code == 200:
#     # Get the content of the file as bytes
#     json_data = json_response.content
#     # If the content is text, decode it
#     imagens_docker_notloaded = json_data.decode('utf-8')
#     imagens_docker= json.loads(imagens_docker_notloaded)
# else:
#     print(f"Failed to get the file. Status code: {json_response.status_code}")
    

with open('novoJson.txt', 'rb') as file:
    imagens_docker = json.load(file)
    
# import traceback


# try:
#     with open('novoJSON.txt', 'rb') as file:
#         imagens_docker = json.load(file)
# except json.JSONDecodeError as e:
#     # Imprime o traceback para ver a linha exata onde o erro ocorreu
#     traceback.print_exc()


# Link do pegi3s
def open_link(event):
    webbrowser.open("https://pegi3s.github.io/dockerfiles/")

# Faz a conexão com o outro software desenvolvido
def run_DockerManager():
    subprocess.run(["python", "editDockerImages.py"])


def center_window(window, width, height):
    # Get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # Calculate position for the window
    x_screen = (screen_width - width) // 2
    y_screen = ((screen_height - height) // 2)-50

    # Set geometry
    window.geometry(f"{width}x{height}+{x_screen}+{y_screen}")
    
    
# Cria a window
window = tk.Tk()
window.title("Manage Docker Images")
# Set window size
window_width = 1600
window_height = 900

# Center the window
center_window(window, window_width, window_height)

# Cria a caixa azul acima da janela
blue_box_frame = tk.Frame(window, bg="#007bff")
blue_box_frame.place(relx=0, rely=0, relwidth=1, relheight=0.25)

# Cria a caixa azul no fim da janela
blue_box_frame_bot = tk.Frame(window, bg="#007bff")
blue_box_frame_bot.place(relx=0, rely=0.85, relwidth=1, relheight=0.15)

# Organização da caixa azul com o titulo e subtitulo
greeting = tk.Label(blue_box_frame, text="Bioinformatics Docker Images Project", fg="white", font=("sans-serif", 30), background="#007bff")
subtitle = tk.Label(blue_box_frame, text="Phenotypic Evolution Group - IBMC/i3S", fg="white", font=("sans-serif", 15), background="#007bff")

# Vai buscar a imagem do pegi3s
image_path = "pegi3s_logo.png"
original_image = Image.open(image_path)

# Resize da imagem
width = int(original_image.width * 0.7)
height = int(original_image.height * 0.7)
resized_image = original_image.resize((width, height), Image.ANTIALIAS)

# Converte a imagem para pdoer ser utilizada
i3s_image = ImageTk.PhotoImage(resized_image)

# Torna a imagem um butão
logo_label = tk.Label(blue_box_frame, image=i3s_image, cursor="hand2")
logo_label.image = i3s_image  # Keep a reference to the image to prevent it from being garbage collected
logo_label.bind('<Button-1>', open_link)



def handle_image_selection(image_name):
    global imageSelected
    image_names = [image["name"] for image in imagens_docker]  # Lista de todos os nomes de imagens no JSON
    if image_name in image_names:
        image_data = next(image for image in imagens_docker if image["name"] == image_name)  # Dados da imagem correspondente ao nome
        docButtton.config(command=lambda: webbrowser.open(image_data["manual_url"]))
        title_label.config(text=image_name)
        place_buttons()
        imageSelected = image_name
        pegi3sButton.config(command=lambda: webbrowser.open(image_data["pegi3s_url"]))
        githubButton.config(command=lambda: webbrowser.open(image_data["github_url"]))
        description_label.config(text=image_data["description"], wraplength=800)
        description_label.update()
    else:
        messagebox.showwarning("Warning", "Selected image not found in JSON.")
    

def show_context_menu(event):
    context_Cat_menu.tk_popup(event.x_root, event.y_root)

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


###############ABRE OS FICHEIROS DA ONTOLOGIA########################
###############ORGANIZAÇÃO DAS CATEGORIAS#################
obo_url = "https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/dio.obo"
obo_response= requests.get(obo_url)
if obo_response.status_code == 200:
    # Get the content of the file as bytes
    obo_data = obo_response.content
    # If the content is text, decode it
    obo_text_data = obo_data.decode('utf-8')
else:
    print(f"Failed to get the file. Status code: {obo_response.status_code}")
    
###############ORGANIZAÇÃO DAS IMAGENS NAS CATEGORIAS################

diaf_url = "https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/dio.diaf"
diaf_response = requests.get(diaf_url)

if diaf_response.status_code == 200:
    # Get the content of the file as bytes
    diaf_data = diaf_response.content
    # If the content is text, decode it
    diaf_text_data = diaf_data.decode('utf-8')
else:
    print(f"Failed to get the file. Status code: {diaf_response.status_code}")


# Diferentes funcções para criar o nested menu com as imagens nas categorias corretas
ont_Sorted_Cat = hierarchy_structure(obo_text_data)
catNestedMenu = convert_CatOntToNestedMenu(ont_Sorted_Cat)
imNestedMenu = organize_images_Nested_Menu(diaf_text_data , catNestedMenu)


# Create a button
onthology_button = tk.Button(window, text="Select an image", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)
onthology_button.pack(pady=50)

# Create a context menu
context_Cat_menu = Menu(window, tearoff=0)

# Populate the context menu with options from the array
for option in imNestedMenu:
    if isinstance(option, dict):
        for key, value in option.items():
            context_Cat_menu.add_cascade(label=key, menu=create_submenu(context_Cat_menu, value))
    else:
        context_Cat_menu.add_command(label=option, command=lambda opt=option: update_button_text(opt))

# Bind the button to show the context menu on left-click
onthology_button.bind("<Button-1>", show_context_menu)


def show_warning():
    messagebox.showwarning("Warning", "WIP")

def open_secondary_window_wrapper():
    open_secondary_window(imageSelected)
        
def open_dockerManager_wrapper():
    open_dockerManager()
    
def test_Data(selected_option):
    image_data = next(image for image in imagens_docker if image["name"] == selected_option)
    testDatalink = image_data["test_invocation_specific"]
    if testDatalink == "NN":
        messagebox.showwarning("Warning", "This image doesnt require test data")
        
    else:
        webbrowser.open(testDatalink)
         
    
# Butões da App
docButtton = tk.Button(window, text="Open Documentation", command=show_warning, bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)  # abre os docs das imagens
githubButton = tk.Button(window, text="Open Github", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)  # Abre a página do github
pegi3sButton = tk.Button(window, text="Open pegi3s", command=show_warning, bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)  # Abre a página do pegi3s da imagem
testDataButton = tk.Button(window, text="Test Data", command=lambda: test_Data(imageSelected), bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)  # Github com os ficheiros de Input
resultsButton = tk.Button(window, text="Test Data Results", command=show_warning, bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)  # GitHub com os resultados do programa
runFILEBUTTON = tk.Button(window, text="Open Run Page", command=open_secondary_window_wrapper, bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)

def on_enter(event):
    title_label.config(fg="#3498db", font=("sans-serif", 40, "underline"))
    canvas.itemconfig(triangle_canvas, outline='#3498db', fill= '#3498db')  # Change outline color of the circle


def on_leave(event):
    title_label.config(fg="black", font=("sans-serif", 40))
    canvas.itemconfig(triangle_canvas, outline='black')  # Restore outline color of the circle


def place_buttons():
    # Place the buttons
    docButtton.place(relx=0.98, rely=0.3, anchor=tk.E)
    pegi3sButton.place(relx=0.98, rely=0.35, anchor=tk.E)
    githubButton.place(relx=0.98, rely=0.4, anchor=tk.E)
    testDataButton.place(relx=0.35, rely=0.815, anchor=tk.CENTER)
    resultsButton.place(relx=0.65, rely=0.815, anchor=tk.CENTER)
    runFILEBUTTON.place(relx=0.5, rely=0.815, anchor=tk.CENTER)
    onthology_button.place(relx=2, rely=2)
    onthology_button.bind("<Button-1>", show_context_menu)
    title_label.bind("<Button-1>", show_context_menu)
    title_label.bind("<Enter>", on_enter)
    title_label.bind("<Leave>", on_leave)
    title_label.update()
    delete_canvas(canvas)
    create_dropdown_menu_but(title_label.winfo_x(), title_label.winfo_y(), title_label.winfo_width())

    
onthology_button.place(relx=0.1, rely=0.3, anchor=tk.CENTER)
greeting.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
subtitle.place(relx=0.5, rely=0.35, anchor=tk.CENTER)
logo_label.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

# Create the title label
title_label = tk.Label(window, text="", fg="black", font=("sans-serif", 40))
title_label.place(relx=0.5, rely=0.3, anchor=tk.CENTER)


#######PARA CRIAR O BUTÃO PARA ESCOLHER OUTRA IMAGEM DOCKER####################
canvas = tk.Canvas(window, width=50, height=50)

# Add the canvas with the circle and the "V" inside it
def create_dropdown_menu_but (x, y, width):
    global triangle_canvas
    canvas.place(x=x+width, y=y+10)
    
    # Coordinates for the inverted triangle
    points = [25, 35, 35, 15, 15, 15]
    
    # Draw the inverted triangle
    triangle_canvas = canvas.create_polygon(points, fill= '#3498db', outline='black', width=3)
    
    # Bind the click event to the inverted triangle
    canvas.tag_bind(triangle_canvas, "<Button-1>", show_context_menu)
    # Bind hover events
    canvas.tag_bind(triangle_canvas, "<Enter>", on_enter)
    canvas.tag_bind(triangle_canvas, "<Leave>", on_leave)

def delete_canvas(canvas):
    canvas.delete("all")
    canvas = tk.Canvas(window, width=50, height=50)


description_label = tk.Label(window,  fg="black", font=("sans-serif", 14), state="disabled")
description_label.place(relx=0.5, rely=0.37, anchor=tk.N, width=800)

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

    # Bind the stop_video function to the window's close event
    root.protocol("WM_DELETE_WINDOW", stop_video)
    
play_video(window, "docker_explainVideo.mp4") #SUBSTITUIR AQUI O VIDEO


def copy_email():
    email = "pegi3sdocker@gmail.com"
    pyperclip.set_clipboard("xclip")
    pyperclip.copy(email)
    print("Email copied to clipboard:", email)

# Create frame for email box
email_frame = tk.Frame(window, bg="white", bd=2, relief="groove", width=250, height=150)
email_frame.place(relx=0.2, rely=0.865, relwidth=0.15, relheight=0.12)

# Email label
email_label = tk.Label(email_frame, text="Contact Us", bg="white", padx=5, pady=2, font=("Helvetica", 14, "bold"), fg="black")
email_label.place(relx=0.5, rely=0.15, anchor="center")

# Email address
email_address = tk.Label(email_frame, text="pegi3sdocker@gmail.com", bg="white", padx=5, pady=2)
email_address.place(relx=0.5, rely=0.4, anchor="center")

# Button
email_button = tk.Button(email_frame, text="Copy Email", bg="#007bff", fg="white", padx=10, pady=2, command = lambda:copy_email())
email_button.place(relx=0.5, rely=0.75, anchor="center")

dockerManager_button = tk.Button(window, text="My Docker Images", command=open_dockerManager_wrapper, width=250, height=150, bg = "white")

dockerManager_button.place(relx=0.7, rely=0.865, relwidth=0.15, relheight=0.12)



window.mainloop()
