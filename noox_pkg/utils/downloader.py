import requests
import os

# Default download directory (relative to where script is run or module is imported)
# This is not used by the function itself but can be a reference if this file were run standalone.
# DOWNLOAD_DIR = "downloads"

def download_file(url: str, dest_folder: str, app_name: str, progress_callback=None):
    """
    Downloads a file from a URL to a specified destination folder.
    The downloaded file will be named after the app_name.

    Args:
        url (str): The URL to download the file from.
        dest_folder (str): The folder to save the downloaded file in.
        app_name (str): The name of the application, used for the filename.
        progress_callback (function, optional): A callback function to report progress.
            It should accept three arguments: bytes_downloaded, total_size, percentage.
            total_size might be None if Content-Length is not available.

    Returns:
        bool: True if download was successful, False otherwise.
    """
    if not url or not dest_folder or not app_name:
        print("Error: URL, destination folder, and app name must be provided.")
        return False

    # Ensure the destination folder exists
    try:
        os.makedirs(dest_folder, exist_ok=True)
    except OSError as e:
        print(f"Error creating destination folder {dest_folder}: {e}")
        return False

    file_path = os.path.join(dest_folder, app_name)

    try:
        print(f"Starting download: {app_name} from {url} to {file_path}")
        with requests.get(url, stream=True, timeout=10) as r:
            r.raise_for_status()

            total_size_in_bytes_str = r.headers.get('content-length')
            total_size_in_bytes = None
            if total_size_in_bytes_str:
                total_size_in_bytes = int(total_size_in_bytes_str)
                if progress_callback:
                    progress_callback(0, total_size_in_bytes, 0)
            else:
                print("Warning: Content-Length header not found. Progress percentage will not be available.")
                if progress_callback:
                     progress_callback(0, None, None)

            bytes_downloaded = 0
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        if progress_callback:
                            if total_size_in_bytes:
                                percentage = (bytes_downloaded / total_size_in_bytes) * 100
                                progress_callback(bytes_downloaded, total_size_in_bytes, percentage)
                            else:
                                progress_callback(bytes_downloaded, None, None)

        print(f"Successfully downloaded {app_name} to {file_path}")
        if total_size_in_bytes and bytes_downloaded != total_size_in_bytes:
            print(f"Warning: Downloaded size {bytes_downloaded} does not match Content-Length {total_size_in_bytes}.")

        if progress_callback:
            if total_size_in_bytes:
                 progress_callback(total_size_in_bytes, total_size_in_bytes, 100)
            else: # Final call even if total_size was unknown
                 progress_callback(bytes_downloaded, None, None)

        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {app_name} from {url}: {e}")
    except IOError as e:
        print(f"Error writing file {file_path}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred for {app_name}: {e}")

    return False

if __name__ == '__main__':
    print("Testing downloader.py directly...")

    def my_test_callback(bytes_down, total_bytes, percent):
        if total_bytes and percent is not None:
            print(f"Downloaded: {bytes_down}/{total_bytes} bytes ({percent:.2f}%)")
        else:
            print(f"Downloaded: {bytes_down} bytes (total size unknown)")

    test_url_gitignore = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
    test_dest = "test_downloads_output"
    test_app_name = "Python.gitignore.test" # Use a distinct name for test output

    # Ensure test directory exists
    if not os.path.exists(test_dest):
        os.makedirs(test_dest)
        print(f"Created test directory: {test_dest}")

    print(f"Attempting to download {test_app_name} with progress callback...")
    success = download_file(test_url_gitignore, test_dest, test_app_name, progress_callback=my_test_callback)
    if success:
        print(f"Test download of {test_app_name} successful.")
        assert os.path.exists(os.path.join(test_dest, test_app_name))
        print(f"File {os.path.join(test_dest, test_app_name)} verified to exist.")
    else:
        print(f"Test download of {test_app_name} failed.")

    # Example of a larger file (commented out by default to avoid long tests)
    # test_url_large = "https://releases.ubuntu.com/22.04.3/ubuntu-22.04.3-desktop-amd64.iso.torrent" # Example large file (torrent file, small itself)
    # test_app_name_large = "ubuntu.iso.torrent"
    # print(f"Attempting to download {test_app_name_large} with progress callback...")
    # success_large = download_file(test_url_large, test_dest, test_app_name_large, progress_callback=my_test_callback)
    # if success_large:
    #     print(f"Test download of {test_app_name_large} successful.")
    # else:
    #     print(f"Test download of {test_app_name_large} failed.")

    test_fail_url = "http://example.com/nonexistentfiledefinitelynotthere.zip"
    print(f"\nAttempting to download non_existent_file.zip (expecting failure)...")
    success_fail_test = download_file(test_fail_url, test_dest, "non_existent_file.zip", progress_callback=my_test_callback)
    if not success_fail_test:
        print("Test download failure for non_existent_file.zip as expected.")
    else:
        print("Test download failure for non_existent_file.zip did NOT fail as expected.")
