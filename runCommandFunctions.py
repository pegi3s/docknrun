# -*- coding: utf-8 -*-
"""
Created on Wed Mar 20 09:45:30 2024

@author: diogo
"""


def setUpRunCBox(command):
    # Padrão a ser substituído
    pattern = "/your/data/dir:/data "
    # Encontrando a posição do padrão na string do comando
    first_index = command.find(pattern)
    # Se o padrão for encontrado
    if first_index != -1:
        # Retornar a parte da string após o padrão
        final_command = command[first_index + len(pattern):]
        return final_command
    else:
        # Se o padrão não for encontrado, retornar o comando original
        return command
        
    
def createFullRunC(directory, comB, userC):
    pattern = "/your/data/dir"
    directory_unix = convert_to_unix_style_path(directory)
    comBUpdate = comB.replace(pattern, directory_unix)
    finalCom = comBUpdate + userC
    return finalCom.replace("This image doesnt require user input", "")

def setUpTestDataInvo(directory, test_Data_Com):
    pattern = "/your/data/dir"
    directory_unix = convert_to_unix_style_path(directory)
    testDataComUpdate = test_Data_Com.replace(pattern, directory_unix)
    return testDataComUpdate

    
def convert_to_unix_style_path(windows_path):
    # Replace backslashes with forward slashes
    unix_path = windows_path.replace('\\', '/')
    # Remove colon
    unix_path = unix_path.replace(':', '')
    if unix_path[0].isupper():
        unix_path = unix_path[0].lower() + unix_path[1:]
    return unix_path

def convert_Ubuntu_In_Windows (unix_path):
    prefix = '/mnt/'
    ubuntu_path = prefix + unix_path
    return ubuntu_path
    


def remove_basis(fullRunCom, basis, image):
    index_pegi3s_gbif_gis = fullRunCom.find(image)   
    char_count = count_chars_from_pegi3s_to_end(basis)

    # Se "pegi3s/gbif_gis" não for encontrado, retorna uma mensagem de erro
    if index_pegi3s_gbif_gis == -1:
        return "Erro: 'pegi3s/gbif_gis' não encontrado no fullRunCom."

    # Remove tudo até "pegi3s/gbif_gis"
    updated_fullRunCom = fullRunCom[index_pegi3s_gbif_gis + char_count:]
    
    return updated_fullRunCom

def count_chars_from_pegi3s_to_end(basis):
    # Encontra a posição de "pegi3s" na base
    index_pegi3s = basis.find("pegi3s")

    # Se "pegi3s" não for encontrado na base, retorna 0
    if index_pegi3s == -1:
        return 0

    # Conta o número de caracteres a partir de "pegi3s" até o final da base
    chars_count = len(basis[index_pegi3s:])

    return chars_count

def set_up_Ouput_Name(runParams, prevOutputName, newOutputName):
    updated_runParams1 = runParams.replace("outputFolder", newOutputName)
    updated_runParams2 = updated_runParams1.replace(prevOutputName, newOutputName)
    return updated_runParams2

def set_up_Input_Name(runParams, prevInputName, newInputName, fileType):
    runParamsWithInput = runParams.replace(fileType, newInputName)
    runParamsWithInput = runParams.replace(prevInputName, newInputName)
    return runParamsWithInput
    


