# downloads test data results

import os
import json
import requests
import zipfile
from tkinter import messagebox

def download_and_unzip_results(selected_image):
    # Define paths and file
    json_file_path = "/opt/JSON"
    output_folder = "/data"
    zip_file_path = "/tmp/results.zip"  # Temporarily store the downloaded zip

    try:
        # Ensure the output directory exists
        os.makedirs(output_folder, exist_ok=True)

        # Read JSON file to find the link associated with the selected Docker image
        with open(json_file_path, 'r') as file:
            imagens_docker = json.load(file)

        # Get the test_results_url for the selected Docker image
        image_data = next((img for img in imagens_docker if img["name"] == selected_image), None)
        if image_data is None or image_data.get("test_results_url") is None:
            messagebox.showerror("Error", "No test results URL found for the selected image.")
            return

        test_results_url = image_data["test_results_url"]

        # Download the zip file from the URL
        response = requests.get(test_results_url)
        if response.status_code == 200:
            with open(zip_file_path, 'wb') as zip_file:
                zip_file.write(response.content)
            print("Downloaded the zip file successfully.")

            # Unzip the downloaded file to the /data directory
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(output_folder)
            print(f"Extracted the zip file successfully to '{output_folder}'.")
            messagebox.showinfo("Success", f"Test data results extracted to '{output_folder}'")

        else:
            messagebox.showerror("Error", f"Failed to download the zip file. HTTP status code: {response.status_code}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    finally:
        # Clean up the zip file if it exists
        if os.path.exists(zip_file_path):
            os.remove(zip_file_path)