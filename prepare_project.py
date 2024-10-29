# Prepares the needed folders and files.

import os
import sys
import requests

def check_config_file():
    filepath = "/data/config"
    if not os.path.isfile(filepath):
        print("Config file not found! Please provide a configure file at the working directory!")
        sys.exit(0)

# Create required folders /data/outputFolder and /data/Test_data
def create_required_folders():
    # Define the folder paths
    output_folder_path = "/data/outputFolder"
    test_data_folder_path = "/data/Test_data"
    docker_notebook_latest_invocations_path = "/data/Docker_notebook/Latest_Invocations"
    docker_notebook_user_notes_path = "/data/Docker_notebook/User_Notes"
    docker_notebook_executable_files_path = "/data/Docker_notebook/Executable_Files"
    
    # Create the folders if they don't already exist
    os.makedirs(output_folder_path, exist_ok=True)
    os.makedirs(test_data_folder_path, exist_ok=True)
    os.makedirs(docker_notebook_latest_invocations_path, exist_ok=True)
    os.makedirs(docker_notebook_user_notes_path, exist_ok=True)
    os.makedirs(docker_notebook_executable_files_path, exist_ok=True)

# Download JSON file from pegi3s GitHub
def download_json_file():
    # URL to the raw JSON file on GitHub
    url = 'https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/metadata.json'
    
    # Define the folder and file path
    folder_path = '/opt'
    file_path = os.path.join(folder_path, 'JSON')

    try:
        # Ensure the folder exists (in case of custom paths, usually /opt should exist)
        os.makedirs(folder_path, exist_ok=True)

        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the content to a file named "Json.txt" in the "/opt" folder
        with open(file_path, 'wb') as file:
            file.write(response.content)

    except PermissionError:
        print(f"Permission denied: You need root or sudo access to write to '{folder_path}'")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")