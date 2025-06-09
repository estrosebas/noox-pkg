import requests
import os
import sys # For sys.stdout.write and flush

def download_file(url: str, destination_folder: str, app_name: str) -> bool:
    """
    Downloads a file from a URL to a specified destination folder.

    Args:
        url: The URL of the file to download.
        destination_folder: The folder where the file will be saved.
        app_name: The name of the application, used for naming the file.

    Returns:
        True if download is successful, False otherwise.
    """
    try:
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder, exist_ok=True)
            print(f"Created destination folder: {destination_folder}")
    except OSError as e:
        print(f"Error: Could not create destination folder {destination_folder}. {e}")
        return False

    filename = app_name
    # Try to append extension from URL only if app_name doesn't seem to have one
    if '.' not in app_name:
        try:
            url_path_filename = url.split('/')[-1].split('?')[0] # Get filename from URL path, ignore query params
            if '.' in url_path_filename:
                extension = url_path_filename.split('.')[-1]
                # Basic check: not too long, alphanumeric, avoid adding if it's like "main" or "master"
                if len(extension) > 0 and len(extension) <= 4 and extension.isalnum():
                    filename = f"{app_name}.{extension}"
        except Exception:
            # Ignore errors in extension guessing, stick with app_name
            pass
    filepath = os.path.join(destination_folder, filename)

    print(f"Attempting to download {app_name} from {url} to {filepath}")

    try:
        response = requests.get(url, stream=True, timeout=30) # Added timeout
        response.raise_for_status() # Raises HTTPError for bad responses (4XX or 5XX)

        total_size_in_bytes = response.headers.get('content-length')
        bytes_downloaded = 0

        with open(filepath, 'wb') as f:
            if total_size_in_bytes is None: # No content length header
                print(f"Downloading {app_name} (size unknown)...")
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    bytes_downloaded += len(chunk)
                    # Simple progress for unknown size: print MBs downloaded
                    sys.stdout.write(f"\rDownloading {app_name}: {bytes_downloaded / (1024*1024):.2f} MB downloaded...")
                    sys.stdout.flush()
            else:
                total_size_in_bytes = int(total_size_in_bytes)
                if total_size_in_bytes == 0: # Handle zero byte files
                    print(f"Downloading {app_name}: 0% (0/0 bytes)")
                    # Write nothing if content length is 0
                else:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        # Ensure progress doesn't exceed 100% visually if total_size is underestimated
                        progress = min((bytes_downloaded / total_size_in_bytes) * 100, 100)
                        # \r to return to the beginning of the line, end='' to not add a newline
                        sys.stdout.write(f"\rDownloading {app_name}: {progress:.2f}% ({bytes_downloaded}/{total_size_in_bytes} bytes)")
                        sys.stdout.flush()

        sys.stdout.write('\n') # Move to the next line after progress display
        print(f"{app_name} downloaded successfully to {filepath}")
        return True

    except requests.exceptions.HTTPError as e:
        print(f"Error: Failed to download {app_name}. HTTP Error: {e.response.status_code} for URL {url}")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"Error: Failed to download {app_name}. Connection error for URL {url}: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"Error: Failed to download {app_name}. Request timed out for URL {url}: {e}")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to download {app_name}. An error occurred with URL {url}: {e}")
        return False
    except IOError as e:
        print(f"Error: Could not write file {filepath}. {e}")
        # Attempt to remove partially downloaded file
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                print(f"Removed partially downloaded file: {filepath}")
            except OSError as remove_err:
                print(f"Error removing partially downloaded file {filepath}: {remove_err}")
        return False
    except Exception as e: # Catch any other unexpected errors
        print(f"An unexpected error occurred while downloading {app_name} from {url}: {e}")
        if os.path.exists(filepath): # Clean up if file was created
             try:
                os.remove(filepath)
             except OSError: pass # Ignore if removal fails
        return False

if __name__ == '__main__':
    # Test URLs
    # Small file, has content-length
    # test_url_small = "http://ipv4.download.thinkbroadband.com/5MB.zip"
    # Using a smaller, more reliable file for testing from a known source
    test_url_small = "https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore"
    app_name_small = "Python.gitignore"

    # A URL that might not have content-length (example, often dynamic content)
    # For now, using a reliable source that does provide content-length for simplicity of testing success path.
    # A true test for no content-length would need a specific server setup or known URL.
    # This URL below (a redirect usually) often doesn't give content-length directly or gives it for the chunk.
    # test_url_no_cl = "http://httpbin.org/stream/20" # streams 20 lines, no total content-length
    # For now, let's use another small, reliable file.
    test_url_another = "https://raw.githubusercontent.com/github/gitignore/main/LICENSE"
    app_name_another = "LICENSE_Test"

    # Test URL that will result in 404
    test_url_404 = "http://example.com/non_existent_file.zip"
    app_name_404 = "NonExistent"

    # Test URL that is invalid format
    test_url_invalid = "htp://invalid-url"
    app_name_invalid = "InvalidURL"

    destination = "test_downloads_output"

    print("--- Test 1: Successful download (with content-length) ---")
    success1 = download_file(test_url_small, destination, app_name_small)
    print(f"Download 1 successful: {success1}")
    if success1:
        # app_name_small is "Python.gitignore", filename should be "Python.gitignore"
        assert os.path.exists(os.path.join(destination, app_name_small))

    print("\n--- Test 2: Successful download (another file) ---")
    # app_name_another is "LICENSE_Test" (no extension)
    # URL is ".../LICENSE" (no extension)
    # filename should be "LICENSE_Test"
    success2 = download_file(test_url_another, destination, app_name_another)
    print(f"Download 2 successful: {success2}")
    if success2:
        assert os.path.exists(os.path.join(destination, app_name_another))

    print("\n--- Test 3: Download fails (404 Not Found) ---")
    success3 = download_file(test_url_404, destination, app_name_404)
    print(f"Download 3 successful: {success3}")
    assert not success3

    print("\n--- Test 4: Download fails (Invalid URL Scheme) ---")
    success4 = download_file(test_url_invalid, destination, app_name_invalid)
    print(f"Download 4 successful: {success4}")
    assert not success4

    # Test 5: Simulate no write permission (hard to do directly without changing user/mount)
    # We can test folder creation failure if we make destination unwritable
    # For now, this part is manually reviewed. The IOError catch is there.

    print("\n--- Test 6: URL with no obvious extension in its name (e.g. 'COPYING') ---")
    test_url_no_ext = "https://raw.githubusercontent.com/torvalds/linux/master/COPYING"
    app_name_no_ext = "LinuxKernelCopying" # app_name has no extension
    success6 = download_file(test_url_no_ext, destination, app_name_no_ext)
    print(f"Download 6 successful: {success6}")
    if success6:
        # URL "COPYING" has no clear extension part, so filename should remain app_name_no_ext
        assert os.path.exists(os.path.join(destination, app_name_no_ext))

    print("\n--- Test 7: App name with extension, URL with different/no extension ---")
    app_name_with_ext = "MyNotes.txt"
    # URL path "config" has no obvious extension, so app_name_with_ext should be used as is.
    test_url_config = "https://raw.githubusercontent.com/github/gitignore/main/Global/Ansible.gitignore" # using a real file, name is just for test
    success7 = download_file(test_url_config, destination, app_name_with_ext)
    print(f"Download 7 successful: {success7}")
    if success7:
        assert os.path.exists(os.path.join(destination, app_name_with_ext))


    print("\nAll local tests for downloader.py completed.")
    # Consider cleaning up 'test_downloads_output' directory if needed,
    # but for sandbox, it's fine to leave it.
    # import shutil
    # if os.path.exists(destination):
    #     shutil.rmtree(destination)
    #     print(f"Cleaned up {destination} directory.")
