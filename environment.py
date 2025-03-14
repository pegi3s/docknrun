# Prepares the needed folders and files.
import json
import os
import sys
from dataclasses import dataclass
from typing import Dict, Final, List, Any

import requests

DEFAULT_BASE_PATH: Final[str] = "/data"
DEFAULT_CONFIG_FILE_NAME: Final[str] = "config"
DEFAULT_OUTPUT_FOLDER_NANE: Final[str] = "output"
DEFAULT_TEST_DATA_FOLDER_NAME: Final[str] = "test/data"
DEFAULT_TEST_RESULTS_FOLDER_NAME: Final[str] = "test/results"
DEFAULT_DOCUMENTATION_FOLDER_NAME: Final[str] = "docs"
DEFAULT_PAST_INVOCATIONS_FOLDER_NAME: Final[str] = "past_invocations"
DEFAULT_USER_NOTES_FOLDER_NAME: Final[str] = "user_notes"
DEFAULT_EXECUTABLE_FILES_FOLDER_NAME: Final[str] = "executable_files"
DEFAULT_METADATA_PATH: Final[str] = "/opt"
DEFAULT_METADATA_FILE_NAME: Final[str] = "metadata.json"


@dataclass(frozen=True)
class DocknrunPaths:
    base_path: str
    output_folder_path: str
    test_data_folder_path: str
    test_results_folder_path: str
    doc_past_invocations_path: str
    doc_executable_files_path: str
    doc_user_notes_path: str
    metadata_path: str
    config_file_path: str
    metadata_file_path: str

    @staticmethod
    def build_default_paths() -> "DocknrunPaths":
        return DocknrunPaths(
            base_path=DEFAULT_BASE_PATH,
            output_folder_path=f"{DEFAULT_BASE_PATH}/{DEFAULT_OUTPUT_FOLDER_NANE}",
            test_data_folder_path=f"{DEFAULT_BASE_PATH}/{DEFAULT_TEST_DATA_FOLDER_NAME}",
            test_results_folder_path=f"{DEFAULT_BASE_PATH}/{DEFAULT_TEST_RESULTS_FOLDER_NAME}",
            doc_past_invocations_path=f"{DEFAULT_BASE_PATH}/{DEFAULT_DOCUMENTATION_FOLDER_NAME}/{DEFAULT_PAST_INVOCATIONS_FOLDER_NAME}",
            doc_executable_files_path=f"{DEFAULT_BASE_PATH}/{DEFAULT_DOCUMENTATION_FOLDER_NAME}/{DEFAULT_EXECUTABLE_FILES_FOLDER_NAME}",
            doc_user_notes_path=f"{DEFAULT_BASE_PATH}/{DEFAULT_DOCUMENTATION_FOLDER_NAME}/{DEFAULT_USER_NOTES_FOLDER_NAME}",
            metadata_path=f"{DEFAULT_METADATA_PATH}",
            config_file_path=f"{DEFAULT_BASE_PATH}/{DEFAULT_CONFIG_FILE_NAME}",
            metadata_file_path=f"{DEFAULT_METADATA_PATH}/{DEFAULT_METADATA_FILE_NAME}",
        )

    def list_dir_paths(self) -> List[str]:
        return [
            self.base_path,
            self.output_folder_path,
            self.test_data_folder_path,
            self.test_results_folder_path,
            self.doc_past_invocations_path,
            self.doc_executable_files_path,
            self.doc_user_notes_path,
            self.metadata_path
        ]


def check_config_file(paths: DocknrunPaths) -> None:
    if not os.path.isfile(paths.config_file_path):
        print("Config file not found! Please provide a configure file at the working directory!")
        sys.exit(0)


def load_config_file(config_path: str = f"{DEFAULT_BASE_PATH}/{DEFAULT_CONFIG_FILE_NAME}") -> Dict[str, str]:
    with open(config_path, "r") as config_file:
        return {key.strip(): value.strip() for key, value in
                [line.split("=", 1) for line in config_file.readlines()]}


def get_file_paths(base_path: str = "/data") -> DocknrunPaths:
    config_file_path = os.path.join(base_path, DEFAULT_CONFIG_FILE_NAME)
    config = load_config_file(config_file_path)

    if "documentation_folder" in config:
        documentation_folder_path = config["documentation_folder"].strip()

        if not documentation_folder_path.startswith("/"):
            documentation_folder_path = os.path.join(base_path, documentation_folder_path)
    else:
        documentation_folder_path = DEFAULT_DOCUMENTATION_FOLDER_NAME

    # Define the folder paths
    return DocknrunPaths(
        base_path=base_path,
        output_folder_path=os.path.join(base_path, DEFAULT_OUTPUT_FOLDER_NANE),
        test_data_folder_path=os.path.join(base_path, DEFAULT_TEST_DATA_FOLDER_NAME),
        test_results_folder_path=os.path.join(base_path, DEFAULT_TEST_RESULTS_FOLDER_NAME),
        doc_past_invocations_path=os.path.join(documentation_folder_path, DEFAULT_PAST_INVOCATIONS_FOLDER_NAME),
        doc_user_notes_path=os.path.join(documentation_folder_path, DEFAULT_USER_NOTES_FOLDER_NAME),
        doc_executable_files_path=os.path.join(documentation_folder_path, DEFAULT_EXECUTABLE_FILES_FOLDER_NAME),
        metadata_path=DEFAULT_METADATA_PATH,
        config_file_path=config_file_path,
        metadata_file_path=os.path.join(DEFAULT_METADATA_PATH, DEFAULT_METADATA_FILE_NAME)
    )


# Create required folders
def create_required_folders(paths: DocknrunPaths) -> None:
    # Create the folders if they don't already exist
    for folder in paths.list_dir_paths():
        os.makedirs(folder, exist_ok=True)


# Download JSON file from pegi3s GitHub
def download_json_file(paths: DocknrunPaths) -> None:
    # URL to the raw JSON file on GitHub
    url = "https://raw.githubusercontent.com/pegi3s/dockerfiles/master/metadata/metadata.json"

    # Define the folder and file path
    file_path = paths.metadata_file_path

    try:
        # Fetch the content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Save the content to a file named "Json.txt" in the "/opt" folder
        with open(file_path, "wb") as file:
            file.write(response.content)

    except PermissionError:
        print(f"Permission denied: You need root or sudo access to write to '{paths.metadata_path}'")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


def load_docker_images(paths: DocknrunPaths) -> Any:
    with open(paths.metadata_file_path, "rb") as file:
        return json.load(file)
