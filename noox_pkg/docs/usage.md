# noox pkg - Usage Guide

This guide provides a more detailed walkthrough of using `noox pkg` for managing your application downloads.

## Core Workflow

The typical workflow for using `noox pkg` involves these steps:

1.  **Prepare your JSON file:** Create a JSON file that lists the applications you want to manage. The keys should be human-readable application names, and the values should be their direct download URLs.
2.  **Set Download Directory (Optional but Recommended):** Specify where you want your files to be downloaded. If not set, files will be downloaded into a `downloads` folder in the directory where you run the command.
3.  **Import Applications:** Load the application list from your JSON file into `noox pkg`.
4.  **List Applications (Optional):** Verify that your applications have been imported correctly.
5.  **Download Applications:** Download either all applications or specific ones from the loaded list.

## Command Details

All commands are executed using `python -m noox_pkg.main <command> [options]`.

### 1. `set-dir <directory_path>`

*   **Purpose:** Specifies the target folder for all subsequent downloads.
*   **Action:** If the directory doesn't exist, `noox pkg` will attempt to create it.
*   **Example:**
    ```bash
    python -m noox_pkg.main set-dir /path/to/my/software_collection
    ```
    On Windows:
    ```bash
    python -m noox_pkg.main set-dir C:\Users\YourUser\Downloads\MyApps
    ```
*   **Note:** This setting is currently not persisted between different executions of the program. You'll need to set it each time you start a new session if you want a custom directory.

### 2. `import <filepath>`

*   **Purpose:** Loads application names and URLs from a JSON file into the application's current session.
*   **Action:** Reads the specified JSON file, parses it, and validates the structure. If successful, the app list is stored in memory for the current session.
*   **Example:**
    ```bash
    python -m noox_pkg.main import ./my_apps.json
    ```
*   **Error Handling:** If the file is not found, is not valid JSON, or doesn't match the expected structure (object with string keys and string values), an error message will be displayed, and no apps will be imported.

### 3. `list`

*   **Purpose:** Displays all applications currently loaded into the session from an imported JSON file.
*   **Action:** Prints a list of application names and their associated URLs.
*   **Example:**
    ```bash
    python -m noox_pkg.main list
    ```
*   **Output:**
    ```
    CLI: Listing applications...
    - MyCoolApp: http://example.com/downloads/mycoolapp.exe
    - AnotherTool: https://codeload.github.com/user/repo/zip/refs/heads/main
    ```
    If no apps are loaded, it will indicate so.

### 4. `download [--all-apps | <app_name>]`

*   **Purpose:** Downloads applications to the specified (or default) download directory.
*   **Action:**
    *   If `<app_name>` is provided, `noox pkg` will search for it in the loaded list and download it.
    *   If `--all-apps` is specified, `noox pkg` will attempt to download every application in the loaded list.
    *   Progress (percentage or size) will be displayed during the download.
*   **Examples:**
    *   Download a single, specific application:
        ```bash
        python -m noox_pkg.main download "MyCoolApp"
        ```
    *   Download all applications in the list:
        ```bash
        python -m noox_pkg.main download --all-apps
        ```
*   **Important:** You must import a JSON file using the `import` command before you can download applications. The download directory should also be considered (use `set-dir` or be aware of the default `downloads/` folder).

## JSON File Structure - A Closer Look

The JSON file is the heart of `noox pkg`. It must be an object (dictionary) where:
*   Each **key** is a `string` representing the application's name. This name will be used for display and for specifying individual downloads.
*   Each **value** is a `string` representing the direct URL to the application's downloadable file.

**Example (`apps.json`):**
```json
{
  "Text Editor Pro": "http://example.com/texteditor_pro_setup.exe",
  "Image Viewer Lite": "http://download.example.org/ivlite.zip",
  "System Utility Pack": "https://somecdn.com/utils/syspack.msi"
}
```
**Tips for URLs:**
*   Ensure URLs are direct download links. Links to HTML pages that then link to the file will not work.
*   URLs starting with `http://` or `https://` are expected.

This should cover the primary usage scenarios for `noox pkg`. For any command, you can also use `--help` (e.g., `python -m noox_pkg.main download --help`) to see specific options.
