import os
import shutil
import zipfile
from tempfile import TemporaryDirectory
from tkinter import messagebox
from typing import Optional
from urllib.parse import urlparse

import requests

from environment import DocknrunPaths, load_docker_images


def _check_if_link_is_working(url: str) -> Optional[str]:
    try:
        response = requests.head(url, allow_redirects=True)

        return url if 200 <= response.status_code < 400 else None
    except requests.exceptions.RequestException as e:
        return None

def generate_pegi3s_url(image_data) -> Optional[str]:
    return f"https://hub.docker.com/r/pegi3s/{image_data['name']}/"

def generate_github_url(image_data) -> Optional[str]:
    return _check_if_link_is_working(f"https://github.com/pegi3s/dockerfiles/tree/master/{image_data['name']}/")

def generate_source_url(image_data) -> Optional[str]:
    if "source_url" in image_data and len(image_data["source_url"].strip()) == 0:
        return image_data["source_url"]
    else:
        return None

def generate_manual_url(image_data) -> Optional[str]:
    return image_data["manual_url"]


def download_test_data(selected_image: str, paths: DocknrunPaths):
    try:
        # Read JSON file to find the link associated with the selected Docker image
        docker_images = load_docker_images(paths)
        output_path = paths.test_data_folder_path

        # Get the test_data_url for the selected Docker image
        image_data = next((img for img in docker_images if img["name"] == selected_image), None)
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
                    zip_ref.extractall(output_path)
                print(f"Extracted the test data zip file successfully to '{output_path}'.")
                messagebox.showinfo("Success", f"Test data extracted to '{output_path}'")
            else:
                # Move the file to the output directory
                shutil.move(downloaded_file_path, os.path.join(output_path, original_filename))
                print(f"Saved the test data file successfully to '{output_path}'.")
                messagebox.showinfo("Success", f"Test data file saved to '{output_path}'")

        else:
            messagebox.showerror("Error", f"Failed to download the test data file. HTTP status code: {response.status_code}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
    finally:
        # Clean up the downloaded file if it exists and isn't in the output directory
        if os.path.exists(downloaded_file_path) and downloaded_file_path.startswith("/tmp"):
            os.remove(downloaded_file_path)


def download_and_unzip_results(selected_image: str, paths: DocknrunPaths) -> None:
    try:
        # Define paths and file
        docker_images = load_docker_images(paths)
        output_path = paths.test_results_folder_path

        # Get the test_results_url for the selected Docker image
        image_data = next((img for img in docker_images if img["name"] == selected_image), None)
        if image_data is None or image_data.get("test_results_url") is None:
            messagebox.showerror("Error", "No test results URL found for the selected image.")
            return

        test_results_url = image_data["test_results_url"]

        # Download the zip file from the URL
        response = requests.get(test_results_url)
        if response.status_code == 200:
            with TemporaryDirectory() as temp_dir:
                zip_file_path = os.path.join(temp_dir, "results.zip")
                with open(zip_file_path, "wb") as zip_file:
                    zip_file.write(response.content)
                print("Downloaded the zip file successfully.")

                # Unzip the downloaded file to the /data directory
                with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
                    zip_ref.extractall(output_path)
                print(f"Extracted the zip file successfully to '{output_path}'.")
                messagebox.showinfo("Success", f"Test data results extracted to '{output_path}'")
        else:
            messagebox.showerror("Error", f"Failed to download the zip file. HTTP status code: {response.status_code}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
