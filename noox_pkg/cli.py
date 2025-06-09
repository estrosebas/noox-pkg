# Placeholder for storing loaded app data
loaded_apps_data = {}
DOWNLOAD_DIR = "downloads" # Default download directory

# Import necessary functions
from .utils import json_parser, downloader
import os # For ensuring download directory exists

def handle_import(filepath: str):
    print(f"CLI: Attempting to import from {filepath}...")
    parsed_data = json_parser.load_apps_from_json(filepath)

    global loaded_apps_data
    if parsed_data is not None:
        loaded_apps_data = parsed_data
        print(f"Successfully imported {len(loaded_apps_data)} apps from {filepath}.")
    else:
        # json_parser already prints specific errors.
        print(f"Import failed from {filepath}. Please check errors above.")
        # Optionally, decide if loaded_apps_data should be cleared on failed import
        # loaded_apps_data = {}

def handle_list_apps():
    print("CLI: Listing loaded applications...")
    if not loaded_apps_data:
        print("No applications loaded. Use 'import <filepath>' first.")
        return
    for app_name, url in loaded_apps_data.items():
        print(f"- {app_name}: {url}")

def handle_download(app_name: str):
    global DOWNLOAD_DIR # Ensure we are using the potentially updated global DOWNLOAD_DIR

    try:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    except OSError as e:
        print(f"Error: Could not create download directory {DOWNLOAD_DIR}. {e}")
        return

    if not loaded_apps_data:
        print("No applications loaded. Use 'import <filepath>' first before downloading.")
        return

    if app_name == "--all":
        if not loaded_apps_data: # This check is technically redundant due to the one above
            print("No applications loaded to download all. Import first.")
            return

        print(f"CLI: Attempting to download all {len(loaded_apps_data)} applications to '{DOWNLOAD_DIR}'...")
        all_successful = True
        for name, url in loaded_apps_data.items():
            print(f"\nStarting download for {name}...")
            success = downloader.download_file(url, DOWNLOAD_DIR, name)
            if success:
                print(f"{name} download completed.")
            else:
                print(f"{name} download failed. Check errors above.")
                all_successful = False

        if all_successful:
            print("\nAll downloads completed successfully.")
        else:
            print("\nSome downloads failed.")

    else:
        if app_name in loaded_apps_data:
            url = loaded_apps_data[app_name]
            print(f"\nStarting download for {app_name} to '{DOWNLOAD_DIR}'...")
            success = downloader.download_file(url, DOWNLOAD_DIR, app_name)
            if success:
                print(f"{app_name} download completed.")
            else:
                print(f"{app_name} download failed. Check errors above.")
        else:
            print(f"Application '{app_name}' not found in the loaded list.")

def handle_set_download_dir(directory: str):
    global DOWNLOAD_DIR

    # Attempt to create the directory immediately to validate it
    try:
        os.makedirs(directory, exist_ok=True)
        # If successful, update DOWNLOAD_DIR and make it absolute
        DOWNLOAD_DIR = os.path.abspath(directory)
        print(f"Download directory set to: {DOWNLOAD_DIR}")
    except OSError as e:
        print(f"Error: Could not create or access directory '{directory}'. {e}")
        print(f"Download directory remains: {os.path.abspath(DOWNLOAD_DIR)}")

# Basic test structure (not run by default, but can be invoked for quick checks)
if __name__ == '__main__':
    # This section is for direct testing of cli.py, not part of the main execution flow.
    # It requires utils to be importable from this context, which might mean adjusting PYTHONPATH
    # or running as a module if utils are in a sub-package not directly visible here.

    print("Testing cli.py functions directly (requires utils to be importable)")

    # Mock objects or simple stubs for parser and downloader for isolated CLI testing
    class MockJsonParser:
        def load_apps_from_json(self, filepath):
            print(f"[MockJsonParser] Loading from {filepath}")
            if filepath == "test_success.json":
                return {"App1": "http://example.com/app1.zip", "App2": "http://example.com/app2.exe"}
            elif filepath == "test_empty.json":
                return {}
            else:
                print(f"[MockJsonParser] Error: File {filepath} not found or invalid.")
                return None

    class MockDownloader:
        def download_file(self, url, dest_folder, app_name):
            print(f"[MockDownloader] Simulating download: {app_name} from {url} to {dest_folder}/{app_name}")
            if "fail" in app_name.lower():
                return False
            # Create a dummy file to simulate download
            os.makedirs(dest_folder, exist_ok=True)
            with open(os.path.join(dest_folder, app_name + ".mock"), "w") as f:
                f.write("mock content")
            return True

    # Replace actual utils with mocks for this test block
    json_parser = MockJsonParser()
    downloader = MockDownloader()

    # Test data directory
    test_data_dir = "cli_test_data"
    os.makedirs(test_data_dir, exist_ok=True)

    print("\n--- Test handle_set_download_dir ---")
    new_download_path = os.path.join(test_data_dir, "my_test_downloads")
    handle_set_download_dir(new_download_path)
    assert DOWNLOAD_DIR == os.path.abspath(new_download_path)
    assert os.path.exists(DOWNLOAD_DIR)

    print("\n--- Test handle_import (success) ---")
    handle_import("test_success.json")
    assert len(loaded_apps_data) == 2
    assert "App1" in loaded_apps_data

    print("\n--- Test handle_list_apps ---")
    handle_list_apps()

    print("\n--- Test handle_download (specific app) ---")
    handle_download("App1")
    assert os.path.exists(os.path.join(DOWNLOAD_DIR, "App1.mock"))

    print("\n--- Test handle_download (app not found) ---")
    handle_download("AppNonExistent")

    print("\n--- Test handle_download (--all) ---")
    # Add an app that should fail download for testing mixed results
    loaded_apps_data["AppFail"] = "http://example.com/appfail.zip"
    handle_download("--all")
    assert os.path.exists(os.path.join(DOWNLOAD_DIR, "App2.mock"))
    assert os.path.exists(os.path.join(DOWNLOAD_DIR, "AppFail.mock")) # Mock downloader creates it anyway


    print("\n--- Test handle_import (failure) ---")
    handle_import("test_fail.json")
    # Assuming import failure doesn't clear previously loaded data, as per current impl.
    assert len(loaded_apps_data) == 3


    print("\n--- Test handle_import (empty json) ---")
    handle_import("test_empty.json")
    assert len(loaded_apps_data) == 0


    print("\nCLI direct test completed.")
    # Clean up test directory
    # import shutil
    # shutil.rmtree(test_data_dir)
    # print(f"Cleaned up {test_data_dir}")
