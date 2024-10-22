# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 09:46:17 2024

@author: diogo
"""

import tkinter as tk
from tkinter import messagebox
import json
import webbrowser
import os
import runCommandFunctions
from functionsForImagesOptions import findImageVersions
from tkinter import filedialog
from datetime import datetime
import requests
import subprocess
import threading
import time

###UM ERRO QUE VAI EXISTIR, em latest invocations vai ser complicado ir buscar os dados para substituir. So se no latest Invocatio file que se criar, se guarde num campo abaixo esse mesmo nome. Em principio deixo para o proximo, boa sorte.

#DEIXOU DE DAR A PARTE DE COMUNICAR COM O WINDOWS AJUDA

def open_secondary_window(image_selected):


    # # Carregar o JSON
    # json_url = "https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/metadata.json"
    # json_response= requests.get(json_url)

    # if json_response.status_code == 200:
    #     # Get the content of the file as bytes
    #     json_data = json_response.content
    #     # If the content is text, decode it
    #     imagens_docker = json_data.decode('utf-8')
    # else:
    #     print(f"Failed to get the file. Status code: {json_response.status_code}")

    with open('novoJson.txt', 'rb') as file:
        imagens_docker = json.load(file)

    image_data = next(image for image in imagens_docker if image["name"] == image_selected)  # Dados da imagem correspondente ao nome

    # Function to handle file selection
    def choose_file(entry):
        file_path = filedialog.askopenfilename(initialdir="/data")
        entry.delete(0, "end")  # Clear any existing text
        entry.insert(0, file_path)  # Insert the selected file path
        return file_path


    # Create secondary (or popup) window.
    secondary_window = tk.Toplevel()
    secondary_window.title("Secondary Window")
    secondary_window.config(width=700, height=817)

    # Título da página
    input_title_label = tk.Label(secondary_window, text=image_selected, fg="black", font=("sans-serif", 25))
    input_title_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
    input_title_label.update()


    #COLOCAR DOIS SUBMENUS, UM COM AS IMAGENS RECOMENDADAS (NOVO JSON) E COM TODAS AS IMAGENS
    # Function to handle menu option selection
    def menu_option_selected(option):
        selected_option.set(option)

    # Function to show context menu
    def show_context_menu(event):
        context_menu.post(event.x_root, event.y_root)

    # Butão do context menu
    menu_button = tk.Button(secondary_window, text="Menu", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)
    menu_button.place(x = input_title_label.winfo_x() + input_title_label.winfo_width() + 5, y = input_title_label.winfo_y() + 10)
    menu_button.bind("<Button-1>", show_context_menu)

    # Cria o context menu
    context_menu = tk.Menu(secondary_window, tearoff=0)

    response = requests.get("http://evolution6.i3s.up.pt/static/pegi3s/dockerfiles/images-and-tags.txt")
    if response.status_code == 200:
        imagePullsList = response.text
        imageVersions = findImageVersions(image_selected, imagePullsList)
    else:
        print("Falha ao buscar o texto.")

    for imageVersion in imageVersions:
        if imageVersion != "latest":
            difVers = image_selected + ":" + imageVersion
            selected_option = tk.StringVar(value=difVers)
            context_menu.add_command(label=difVers, command=lambda v=difVers: menu_option_selected(v))

    def update_menu_option():
        menu_button.config(text=selected_option.get()) #Há um erro no adops porque lista como adops-gui, mas damos o nome da imagem de adops no json e na ontologia

    update_menu_option()

    # Update the menu button to reflect the default selection

    selected_option.trace("w", lambda *args: update_menu_option())

    docButtton = tk.Button(secondary_window, text="Open Documentation", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1) #abre os docs das imagens
    docButtton.config(command=lambda: webbrowser.open(image_data["manual_url"]))

    pegi3sButton = tk.Button(secondary_window, text="Open pegi3s", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1) #Abre a página do pegi3s da imagem
    pegi3sButton.config(command=lambda: webbrowser.open(image_data["pegi3s_url"]))

    docButtton.place(relx=0.3, rely=0.14, anchor=tk.CENTER)
    pegi3sButton.place(relx=0.7, rely=0.14, anchor=tk.CENTER)

    prevInputName = None

    def choose_file_input(entry, file_type):
        global prevInputName
        file_path = choose_file(entry)
        file_path = file_path.replace("/data", "", 1)
        rumParamsNoInput = runCTextBox.get("1.0", tk.END)
        try:
            runParamsWithInput = runCommandFunctions.set_up_Input_Name(rumParamsNoInput, prevInputName, file_path, "/" + file_type+"Folder")
        except NameError:
            runParamsWithInput = runCommandFunctions.set_up_Input_Name(rumParamsNoInput, "/" + file_type+"Folder", file_path, "/" + file_type+"Folder")
        prevInputName = file_path
        runCTextBox.delete("1.0", tk.END)
        runCTextBox.insert(tk.END, runParamsWithInput)


    #WARNING PARA O UTILIZADOR QUANDO HOUVER MAIS QUE 3 FICHEIROS
    canvas_warning = tk.Canvas(secondary_window, width=25, height=25)

    def warningmore3FileTypes(x, y, width, canvas_warning):
        canvas_warning = tk.Canvas(secondary_window, width=25, height=25)
        canvas_warning.place(x=x+width, y=y)

        # Draw the circle
        canvas_circle = canvas_warning.create_oval(3, 3, 23, 23, fill="#FF7F7F", outline="black", width=2)

        # Draw the question mark inside the circle
        canvas_text = canvas_warning.create_text(13, 13, text="!", font=("Helvetica", 12, "bold"), fill="black")

        canvas_warning.tag_bind(canvas_circle, "<Button-1>", lambda event, canvas=canvas_warning, x=x, y=y: show_context_menu_tooltip(event, "Change the directory path on the parameters box of the other file types"))
        canvas_warning.tag_bind(canvas_text, "<Button-1>", lambda event, canvas=canvas_warning, x=x, y=y: show_context_menu_tooltip(event, "Change the directory path on the parameters box of the other file types"))


    # Criação dos botões e campos de entrada
    butSelectFileType1 = tk.Button(secondary_window, bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)
    butSelectFileType2 = tk.Button(secondary_window, bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)
    butSelectFileType3 = tk.Button(secondary_window, bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)
    frame_No_Input = tk.Frame(secondary_window, width=480, height=85, bg="lightblue")

    def placeInputButtons(input_data_types, canvas):
        nonlocal butSelectFileType1, butSelectFileType2, butSelectFileType3, frame_No_Input

        if input_data_types == [""]:
            # Criando um frame que será a caixa menor dentro da janela principal
            frame_No_Input.place(relx=0.05, rely=0.22, anchor=tk.NW)

            # Criando um rótulo com o texto e centralizando-o dentro do frame
            label = tk.Label(frame_No_Input, text="This image doesn't require input", font=("Arial", 14), bg="lightblue")
            label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        else:
            # Primeiro botão e campo de entrada
            butSelectFileType1.config(text="Select a " + input_data_types[0] + " file", command=lambda: choose_file_input(input_FileType_entry1, input_data_types[0]))
            butSelectFileType1.place(relx=0.05, rely=0.23)
            input_FileType_entry1 = tk.Entry(secondary_window, width=30, font=("Helvetica", 12))  # O local onde vai estar o path do botão específico
            input_FileType_entry1.place(relx=0.3, rely=0.25, anchor=tk.W)

            # Segundo botão e campo de entrada, se houver
            if len(input_data_types) > 1:
                butSelectFileType2.config(text="Select a " + input_data_types[1] + " file", command=lambda: choose_file_input(input_FileType_entry1, input_data_types[1]))
                butSelectFileType2.place(relx=0.05, rely=0.28)
                input_FileType_entry2 = tk.Entry(secondary_window, width=30, font=("Helvetica", 12))  # O local onde vai estar o path do botão específico
                input_FileType_entry2.place(relx=0.3, rely=0.3, anchor=tk.W)

            # Terceiro botão e campo de entrada, se houver
            if len(input_data_types) > 2:
                butSelectFileType3.config(text="Select a " + input_data_types[2] + " file", command=lambda: choose_file_input(input_FileType_entry1, input_data_types[2]))
                butSelectFileType3.place(relx=0.05, rely=0.33)
                input_FileType_entry3 = tk.Entry(secondary_window, width=30, font=("Helvetica", 12))  # O local onde vai estar o path do botão específico
                input_FileType_entry3.place(relx=0.3, rely=0.35, anchor=tk.W)
            if len(input_data_types) > 3:
                input_label.update()
                warningmore3FileTypes(input_label.winfo_x(), input_label.winfo_y(), input_label.winfo_width(), canvas)

    #################### INPUT DO DOCUMENTO##############################
    input_label = tk.Label(secondary_window, text="Input", fg="black", font=("sans-serif", 12))
    input_label.place(relx=0.05, rely=0.2, anchor=tk.W)

    ###################################Que desafio#####################
    input_data_types = None
    if "input_data_type" in image_data:
        input_data_types = image_data["input_data_type"]
        placeInputButtons(input_data_types, canvas_warning)

    # Label for output
    output_label = tk.Label(secondary_window, text="Output", fg="black", font=("sans-serif", 12))
    output_label.place(relx=0.05, rely=0.4, anchor=tk.W)
    output_label.update()


    def on_output_entry_click(event):
        if output_text_box.get("1.0", tk.END).strip() == "Output File Name":
            output_text_box.delete("1.0", tk.END)
            output_text_box.configure(fg="black")

    def on_output_focus_out(event):
        if not output_text_box.get("1.0", tk.END).strip():
            output_text_box.insert("1.0", "Output File Name")
            output_text_box.configure(fg="grey")


    output_text_box = tk.Text(secondary_window, width=60, fg="grey", height = 1)
    output_text_box.insert("1.0", "Output File Name")  # Texto dentro da caixa
    output_text_box.bind("<FocusIn>", on_output_entry_click)
    output_text_box.bind("<FocusOut>", on_output_focus_out)
    output_text_box.place(relx=0.05, rely=0.45, anchor=tk.W)
    output_text_box.update()

    #FuncaoPara Verificar se existem espaços (nao pode existir no nome do ficheiro output)
    def contains_space(s):
        return " " in s
    # Variável global
    prevOutputName = None


    # Função que atualiza o RUNCBox com o novo nome de output
    def output_button():
        global prevOutputName
        newOutputName = output_text_box.get("1.0", tk.END).strip()
        if newOutputName == "" or newOutputName == "Output File Name":
            messagebox.showwarning("Warning", "No output name given to your files")
        elif contains_space(newOutputName):
            messagebox.showwarning("Warning", "The output name mustan't have space")

        else:
            rumParamsNotUpdated = runCTextBox.get("1.0", tk.END)
            try:
                print(prevOutputName)
                runParamUpdated = runCommandFunctions.set_up_Ouput_Name(rumParamsNotUpdated, prevOutputName, newOutputName)
            except NameError:
                runParamUpdated = runCommandFunctions.set_up_Ouput_Name(rumParamsNotUpdated, "outputFolder", newOutputName)
            prevOutputName = newOutputName
            runCTextBox.delete("1.0", tk.END)
            runCTextBox.insert(tk.END, runParamUpdated)

    #Button to replace the output in the command
    output_choose_button = tk.Button(secondary_window, text="Push", command=lambda: output_button(), bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)
    output_choose_button.place(x = output_text_box.winfo_x() + output_text_box.winfo_width() + 5, y = output_text_box.winfo_y(), height=output_text_box.winfo_height())

    def on_closing():
        global prevOutputName
        prevOutputName = None
        print("Morreu")
        secondary_window.destroy()

    # Bind the closing event of the secondary window
    secondary_window.protocol("WM_DELETE_WINDOW", on_closing)


    # Label Developer Notes
    dnLABEL = tk.Label(secondary_window, text="Developer Notes", fg="black", font=("sans-serif", 12))
    dnLABEL.place(relx=0.05, rely=0.5, anchor=tk.W)

    # Text Box User Notes
    dnTextBox = tk.Text(secondary_window, width=60, height=3.5)
    dnTextBox.place(relx=0.05, rely=0.57, anchor=tk.W)


    #This section is meant to populate the Developer Notes
    dn_UseVer = image_data["useful"]
    dn_bug= image_data["bug_found"]
    dn_notWork = image_data["not_working"]
    dn_noLTested = image_data["no_longer_tested"]
    dn_recLastTest = image_data["recommended_last_tested"]
    dn_comments = image_data["comments"] #
    # Convert lists to strings
    dn_UseVer_str = ", ".join(dn_UseVer)
    dn_bug_str = ", ".join(dn_bug)
    dn_notWork_str = ", ".join(dn_notWork)
    dn_noLTested_str = ", ".join(dn_noLTested)
    dn_comments_str = "\n".join(dn_comments)

    # Join the strings
    developer_notesNF = ("The following versions are still useful: " + dn_UseVer_str +
                         "\nA bug has been found in the following versions: " + dn_bug_str +
                         "\nThese versions no longer work: " + dn_notWork_str +
                         "\nThe following versions are no longer tested: " + dn_noLTested_str +
                         "\nThe recommended version has been last tested on: " + dn_recLastTest +
                         "\n" + dn_comments_str)


    if image_data["podman"] == "untested":
        developer_notesP = developer_notesNF + "Image untested for podman"
    elif image_data["podman"] == "tested":
        developer_notesP = developer_notesNF + "Image tested for podman"
    else:
        developer_notesP = developer_notesNF + "Image doesn't work for podman"

    if image_data["singularity"] == "untested":
        developer_notes = developer_notesP + "\nImage untested for singularity"
    elif image_data["singularity"] == "tested":
        developer_notes = developer_notesP + "\nImage tested for singularity"
    else:
        developer_notes = developer_notesP + "\nImage doesn't work for singularity"


    dnTextBox.insert(tk.END, developer_notes)
    dnTextBox.config(state=tk.DISABLED)

    # Label User Notes
    unLABEL = tk.Label(secondary_window, text="User Notes", fg="black", font=("sans-serif", 12))
    unLABEL.place(relx=0.05, rely=0.64, anchor=tk.W)

    # Text Box User Notes
    unTextBox = tk.Text(secondary_window, width=60, height=3.5)
    unTextBox.place(relx=0.05, rely=0.71, anchor=tk.W)

    #Section to get info from the config file. Dir that is obtained is the directory that is gonna be placed inside the run command, plus latest invo and user_notes
    with open("/data/config", "r") as file:
        config_data = file.read()
        # Dividir a string nos delimitadores ',' e '='
        parts = config_data.split('\n')

        # Inicializar as variáveis
        run_dir_path = None
        past_invocations_path = None
        user_notes_path = None
        executable_file_path = None

        # Processar cada parte para extrair os valores
        for part in parts:
            key, value = part.split('=')
            if key == 'dir':
                run_dir_path = value
            elif key == 'past_invocations':
                past_invocations_path = value
            elif key == 'user_notes':
                user_notes_path = value
            elif key == 'executable_files':
                 executable_file_path = value
            else:
                pass


    #Porque é que não fica fora do working dir?
    def create_folder_if_not_exists(parent_folder, folder_name):
        folder_path = os.path.join(parent_folder, folder_name)
        folder_path = "/data" + folder_path
        print(folder_path)
        if not os.path.exists(folder_path):
            print("Folder Created = "+ folder_path)
            os.makedirs(folder_path)
        else:
            print(f"Folder '{folder_name}' already exists in '{parent_folder}' folder.")

    # folderUserNotes = os.getcwd() + "/User_Notes"
    create_folder_if_not_exists(user_notes_path, "User_Notes")

    #Verifica se Dentro da WD existe um folder de Latest Invocations, se não existir, cria
    create_folder_if_not_exists(past_invocations_path, "Latest_Invocations")

    #Verifica se Dentro da WD existe um folder de Executable Files, se não existir, cria
    create_folder_if_not_exists(executable_file_path, "Executable_Files")

    # Para verificar se existem latest invocations da imagem atual:
    folderLatestInvo = past_invocations_path + "/Latest_Invocations"
    folderImageSelectedLI = image_selected + "_LatestInvocations"

    # Para verificar se existem latest invocations da imagem atual:
    folderExecutFiles = past_invocations_path + "/Executable_Files"
    folderImageSelectedEXE = image_selected + "_Executable_Files"



    def load_user_notes():
        file_path = os.path.join("/data", user_notes_path, "User_Notes", image_selected+".txt")
        file_path = "/data" + file_path
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                unTextBox.insert(tk.END, content)

    def save_user_notes():
        file_path = os.path.join( user_notes_path, "User_Notes", image_selected+".txt")
        file_path = "/data" + file_path
        with open(file_path, "w", encoding="utf-8") as file:
            content = unTextBox.get("1.0", tk.END)
            file.write(content)
            secondary_window.destroy()

    load_user_notes()

    secondary_window.protocol("WM_DELETE_WINDOW", save_user_notes)



    def about_the_image_widget(x, y, width):
        canvas = tk.Canvas(secondary_window, width=25, height=25)
        canvas.place(x=x+width, y=y)

        # Draw the circle
        canvas_circle = canvas.create_oval(3, 3, 23, 23, fill="light blue", outline="black", width=2)

        # Draw the question mark inside the circle
        canvas_text = canvas.create_text(13, 13, text="?", font=("Helvetica", 12, "bold"), fill="black")

        canvas.tag_bind(canvas_circle, "<Button-1>", lambda event, canvas=canvas, x=x, y=y: show_context_menu_tooltip(event, "Change the parameters below as you better see fit"))
        canvas.tag_bind(canvas_text, "<Button-1>", lambda event, canvas=canvas, x=x, y=y: show_context_menu_tooltip(event, "Change the parameters below as you better see fit"))



    def show_context_menu_tooltip(event, text):
        # Create a context menu
        context_menu = tk.Menu(secondary_window, tearoff=0, background='light yellow', borderwidth=1, relief='solid', activebackground="light yellow", activeforeground="black")
        context_menu.add_command(label=text)

        # Display the context menu
        context_menu.post(event.x_root, event.y_root)

    # Create the title label for Text Box 2
    runCLABEL = tk.Label(secondary_window, text="Run command", fg="black", font=("sans-serif", 12))
    runCLABEL.place(relx=0.05, rely=0.79, anchor=tk.W)
    runCLABEL.update()
    about_the_image_widget(runCLABEL.winfo_x(), runCLABEL.winfo_y(), runCLABEL.winfo_width())


    # Create the second text box
    runCTextBox = tk.Text(secondary_window, width=60, height=3.5)
    runCTextBox.place(relx=0.05, rely=0.87, anchor=tk.W)
    runCommandBasis = image_data["invocation_general"]
    parametersCom = image_data["usual_invocation_specific"]
    # displayRunC = runCommandFunctions.setUpRunCBox(runCommand)
    if parametersCom == "":
        runCTextBox.insert(tk.END, "This image doesnt require user input")
        runCTextBox.config(state=tk.DISABLED)
    else:
        runCTextBox.insert(tk.END, parametersCom)




    def get_text_data_invocation_command():
        global fullRunCommand
        #Via dar set up ao test_data_invocation depednendo do diretorio
        text_Data_com = image_data["test_invocation_specific"]
        # if directory_entry.get() == "":
        text_Data_dir = runCommandFunctions.setUpTestDataInvo(run_dir_path, text_Data_com)
        # else:
        #     real_dir_path = directory_entry.get()
        #     text_Data_dir = runCommandFunctions.setUpTestDataInvo(real_dir_path, text_Data_com)
        fullRunCommand = text_Data_dir
        runCTextBox.delete("1.0", tk.END)
        runCTextBox.insert(tk.END, text_Data_dir)

    # Butão da test_data_invocation
    tdButton = tk.Button(secondary_window, text="Test Data Invocation", command=lambda: get_text_data_invocation_command(), bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1)
    tdButton.place(relx=0.75, rely=0.84, anchor=tk.W)

    def choose_LatestInvocation():
        create_folder_if_not_exists(folderLatestInvo, folderImageSelectedLI)
        fileDir = "/data" + past_invocations_path + "/Latest_Invocations" + "/" + image_selected + "_LatestInvocations"
        file_path = filedialog.askopenfilename(initialdir = fileDir, title="Choose a Latest Invocation", filetypes=(("Arquivos de texto", "*.txt"), ("Todos os arquivos", "*.*")))
        if file_path:
        # Extrai o texto do arquivo selecionado
            with open(file_path, 'r') as file:
                text_from_file = file.read()
                setUpLatestInvoRunBox(text_from_file)
        # else:
            # print("Nenhum arquivo selecionado.")

    def setUpLatestInvoRunBox(latestInvoCom):
        comBasis = image_data["invocation_general"]
        # latInvoUpdCom = latestInvoCom.replace(comBasis, "")
        lastInvoUpdCom = runCommandFunctions.remove_basis(latestInvoCom, comBasis, "pegi3s/"+image_selected)
        runCTextBox.delete("1.0", tk.END)
        runCTextBox.insert(tk.END, lastInvoUpdCom)


    # Latest Invo Button
    liButton = tk.Button(secondary_window, text="Latest Invocation", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1, command=lambda: choose_LatestInvocation())
    liButton.place(relx=0.75, rely=0.9, anchor=tk.W)


    def updateFullRunCom(directory_path, runCommandBasis): #Adicionar verificação do directory Path
        global fullRunCommand
        runParametersUser = runCTextBox.get("1.0", tk.END)
        runCommandBasisUpdated = runCommandBasis.replace(image_selected, selected_option.get())
        fullRunCommand = runCommandFunctions.createFullRunC(directory_path, runCommandBasisUpdated, runParametersUser)

    updateFullRunCom(run_dir_path, runCommandBasis) #Util para comando sem parametros

        #Esta secção tem muit codigo morto, em teoria, apenas funciona com a parte do else da forma como alterei o código
    def run_CheckIfTestInvo():
        user_Input = runCTextBox.get("1.0", tk.END)
        test_Data_Invo = image_data["test_invocation_specific"]
        # if directory_entry.get() == "":
        test_Data_Invo_Upd = runCommandFunctions.setUpTestDataInvo(run_dir_path, test_Data_Invo)
        # else:
        #     real_dir_path = directory_entry.get()
        #     test_Data_Invo_Upd = runCommandFunctions.setUpTestDataInvo(real_dir_path, test_Data_Invo)
        # test_Data_Invo_Upd = runCommandFunctions.setUpTestDataInvo(directory_path, test_Data_Invo) #Adicionar verificação do directory path
        if user_Input == test_Data_Invo_Upd:
            print("TEST DATA INVO: /n" + test_Data_Invo_Upd)
            return test_Data_Invo_Upd
        else:
            # if directory_entry.get() == "":
            updateFullRunCom(run_dir_path, runCommandBasis)
            print("Dir Path: " + run_dir_path)

            print(fullRunCommand)
            return fullRunCommand

    if image_data["gui"] == True:
        subprocess.run("xhost +", shell=True, check=True)



    def run_command(command):
        def update_text_box(line):
            info_running_text_box.config(state="normal")  # Ativar para permitir a edição
            info_running_text_box.insert("end", line + "\n")  # Adicionar texto
            info_running_text_box.see("end")  # Rolagem automática para a parte inferior
            info_running_text_box.config(state="disabled")  # Desativar novamente

        start_time = time.time()

        # Esconder o layout se necessário
        if hide_layout():
            hide_layout()

        # Abrir o processo e ler a saída linha por linha
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        for line in process.stdout:
            update_text_box(line.strip())  # Atualizar a caixa de texto

        # Aguardar até que o processo seja concluído
        process.wait()

        end_time = time.time()
        runtime = end_time - start_time

        #Mostra o butão para voltar tudo ao normal
        if display_b2NButton(runtime):
            display_b2NButton(runtime)

    def run_button():
        run_Com = run_CheckIfTestInvo()
        create_file_in_folder(folderLatestInvo, folderImageSelectedLI, image_selected, run_CheckIfTestInvo(), ".txt")
        thread = threading.Thread(target=run_command, args=(run_Com,))
        thread.start()

    # Butão de Run
    runButton = tk.Button(secondary_window, text="Run", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1, command=lambda: run_button())
    runButton.place(relx=0.2, rely=0.96, anchor=tk.CENTER)



    #Função que cria um file dentro de um certo diretório com o nome da imagem atual
    def create_file_in_folder(parent_folder, folder_name, file_name, content, file_type):
        folder_path = os.path.join(parent_folder, folder_name)
        folder_path = "/data" + folder_path
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        current_time = datetime.now().strftime("_%d-%m-%Y_%Hh%Mm%Ss")
        fileTimeName = file_name + current_time + file_type #Acrescentei aqui o file type para reutilizalão de codigo
        file_path = os.path.join(folder_path, fileTimeName)

        with open(file_path, 'w') as file:
            file.write(content)


    # Executable File, alterado para agora criar um ficheiro .sh
    shButton = tk.Button(secondary_window, text="Create executable file", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1, command=lambda: create_file_in_folder(folderExecutFiles, folderImageSelectedEXE, image_selected, run_CheckIfTestInvo(), ".sh"))
    shButton.place(relx=0.7, rely=0.96, anchor=tk.CENTER)


    #Secção com as partes para quando estiver a correr a imagem Docker
    # Mostra que esta a correr
    running_text = tk.Label(secondary_window, text="Running:", fg="black", font=("sans-serif", 25))
    # Criar uma caixa de texto grande não interativa
    info_running_text_box = tk.Text(secondary_window, state=tk.DISABLED, height=30, width=55)
    b2Norma_button = tk.Button(secondary_window, text="Okay", bg="#3498db", fg="white", font=("Helvetica", 10, "bold"), relief="raised", width=16, height=1, command=lambda: display_layout()) #abre os docs das imagens
    runtime_Label = tk.Label(secondary_window, fg="black", font=("sans-serif", 15))


    def hide_layout():
        input_title_label.place_forget()
        menu_button.place_forget()
        docButtton.place_forget()
        pegi3sButton.place_forget()
        # select_dir_label.place_forget()
        # directory_choose_button.place_forget()
        # directory_entry.place_forget()
        input_label.place_forget()
        # input_choose_button.place_forget()
        # input_entry.place_forget()
        output_label.place_forget()
        output_text_box.place_forget()
        dnLABEL.place_forget()
        dnTextBox.place_forget()
        unLABEL.place_forget()
        unTextBox.place_forget()
        runCTextBox.place_forget()
        runCLABEL.place_forget()
        tdButton.place_forget()
        liButton.place_forget()
        runButton.place_forget()
        shButton.place_forget()
        output_choose_button.place_forget()
        butSelectFileType1.place_forget()
        butSelectFileType2.place_forget()
        butSelectFileType3.place_forget()
        frame_No_Input.place_forget()
        canvas_warning.place_forget()
        running_text.place(relx=0.5, rely=0.1, anchor=tk.CENTER)
        info_running_text_box.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        info_running_text_box.config(state="normal")  # Set state to normal to enable editing
        info_running_text_box.delete("1.0", "end")  # Clear all text from the text box
        info_running_text_box.config(state="disabled")  # Set state back to disabled to disable editing




    def display_b2NButton(runtime):
        runtime_Label.configure(text="Runtime:\n"+ str(runtime) +" seconds")
        runtime_Label.place(relx=0.5, rely=0.9, anchor=tk.CENTER) #Mostra o tempo de execução
        b2Norma_button.place(relx=0.5, rely=0.965, anchor=tk.CENTER) #Butão para voltar tudo ao normal



    def display_layout():
        running_text.place_forget()
        info_running_text_box.place_forget()
        b2Norma_button.place_forget()
        runtime_Label.place_forget()
        input_title_label.place(relx=0.5, rely=0.05, anchor=tk.CENTER)
        menu_button.place(relx=0.85, rely=0.04, anchor=tk.NE)
        docButtton.place(relx=0.3, rely=0.14, anchor=tk.CENTER)
        pegi3sButton.place(relx=0.7, rely=0.14, anchor=tk.CENTER)
        # select_dir_label.place(relx=0.05, rely=0.2, anchor=tk.W)
        # directory_choose_button.place(relx=0.05, rely=0.25, anchor=tk.W, width=100)
        # directory_entry.place(relx=0.3, rely=0.25, anchor=tk.W)
        input_label.place(relx=0.05, rely=0.2, anchor=tk.W)
        # input_choose_button.place(relx=0.05, rely=0.35, anchor=tk.W, width=100)
        # input_entry.place(relx=0.3, rely=0.35, anchor=tk.W)
        output_label.place(relx=0.05, rely=0.4, anchor=tk.W)
        output_text_box.place(relx=0.05, rely=0.45, anchor=tk.W)
        dnLABEL.place(relx=0.05, rely=0.5, anchor=tk.W)
        dnTextBox.place(relx=0.05, rely=0.57, anchor=tk.W)
        unLABEL.place(relx=0.05, rely=0.64, anchor=tk.W)
        unTextBox.place(relx=0.05, rely=0.71, anchor=tk.W)
        runCTextBox.place(relx=0.05, rely=0.87, anchor=tk.W)
        runCLABEL.place(relx=0.05, rely=0.79, anchor=tk.W)
        tdButton.place(relx=0.75, rely=0.84, anchor=tk.W)
        liButton.place(relx=0.75, rely=0.9, anchor=tk.W)
        runButton.place(relx=0.2, rely=0.96, anchor=tk.CENTER)
        shButton.place(relx=0.7, rely=0.96, anchor=tk.CENTER)
        output_choose_button.place(x = output_text_box.winfo_x() + output_text_box.winfo_width() + 5, y = output_text_box.winfo_y(), height=output_text_box.winfo_height())
        if input_data_types is not None:
            placeInputButtons(input_data_types, canvas_warning)




