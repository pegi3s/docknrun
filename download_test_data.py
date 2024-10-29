# downloads test data. used in main window

import os
import json
import requests
import shutil
import zipfile
from tkinter import messagebox
from urllib.parse import urlparse

def download_test_data(selected_image):
    json_file_path = "/opt/JSON"
    output_folder = "/data/Test_data"
    
    try:
        os.makedirs(output_folder, exist_ok=True)

        # Read JSON file to find the link associated with the selected Docker image
        with open(json_file_path, 'r') as file:
            imagens_docker = json.load(file)

        # Get the test_data_url for the selected Docker image
        image_data = next((img for img in imagens_docker if img["name"] == selected_image), None)
        if image_data is None or image_data.get("test_data_url") is None:
            messagebox.showerror("Error", "No test data URL found for the selected image.")
            return

        test_data_url = image_data["test_data_url"]

        # Download the file from the URL
        response = requests.get(test_data_url)
        if response.status_code == 200:
            # Get the original filename from the URL
            parsed_url = urlparse(test_data_url)
            original_filename = os.path.basename(parsed_url.path) or "downloaded_file.bin"

            # Set the full path for the downloaded file
            downloaded_file_path = os.path.join("/tmp", original_filename)

            # Save the downloaded file
            with open(downloaded_file_path, 'wb') as file:
                file.write(response.content)
            print(f"Downloaded the test data file successfully as '{downloaded_file_path}'.")

            # Check if the file is a zip file
            if downloaded_file_path.endswith('.zip'):
                # Unzip the downloaded file to the /data directory
                with zipfile.ZipFile(downloaded_file_path, 'r') as zip_ref:
                    zip_ref.extractall(output_folder)
                print(f"Extracted the test data zip file successfully to '{output_folder}'.")
                messagebox.showinfo("Success", f"Test data extracted to '{output_folder}'")
            else:
                # Move the file to the output directory
                shutil.move(downloaded_file_path, os.path.join(output_folder, original_filename))
                print(f"Saved the test data file successfully to '{output_folder}'.")
                messagebox.showinfo("Success", f"Test data file saved to '{output_folder}'")

        else:
            messagebox.showerror("Error", f"Failed to download the test data file. HTTP status code: {response.status_code}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    finally:
        # Clean up the downloaded file if it exists and isn't in the output directory
        if os.path.exists(downloaded_file_path) and downloaded_file_path.startswith("/tmp"):
            os.remove(downloaded_file_path)