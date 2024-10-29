# -*- coding: utf-8 -*-

# Functions for building the Docker command

def setUpRunCBox(command):
    # Pattern to be replaced
    pattern = "/your/data/dir:/data "
    # Find the pattern position in string
    first_index = command.find(pattern)
    # If pattern is found
    if first_index != -1:
        # Returns string after the pattern
        final_command = command[first_index + len(pattern):]
        return final_command
    else:
        # If pattern is not found return the original string
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
    index_pegi3s = fullRunCom.find(image)   
    char_count = count_chars_from_pegi3s_to_end(basis)

    # If Docker image name not found
    if index_pegi3s == -1:
        return "Error: Docker image name not found"

    # Removes everything up to Docker image name
    updated_fullRunCom = fullRunCom[index_pegi3s + char_count:]
    
    return updated_fullRunCom

def count_chars_from_pegi3s_to_end(basis):
    # Find position of "pegi3s" at the base
    index_pegi3s = basis.find("pegi3s")

    # If "pegi3s" is not found returns 0
    if index_pegi3s == -1:
        return 0

    # Counts the number of characters from "pegi3s" until the end of the base
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
