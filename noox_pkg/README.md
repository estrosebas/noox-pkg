# noox pkg

**noox pkg** is a command-line application designed to simplify the process of downloading multiple applications from a predefined list. You provide a JSON file containing application names and their download URLs, and noox pkg handles the rest.

## Features

*   **JSON Import:** Easily import a list of applications and their download URLs from a JSON file.
*   **Selective Download:** Choose to download specific applications from the imported list.
*   **Bulk Download:** Download all applications from the list with a single command.
*   **Custom Download Directory:** Specify where your downloaded files should be saved.
*   **Command-Line Interface:** All operations are performed through a straightforward CLI.

## Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://your-repository-url-here.git
    cd name-of-the-cloned-directory
    ```
    *(Replace `https://your-repository-url-here.git` and `name-of-the-cloned-directory` with actual values.)*

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

All commands are run through `main.py` within the `noox_pkg` module.

**General command structure:**
```bash
python -m noox_pkg.main [command] [options]
```

**Available Commands:**

*   **`import <filepath>`:**
    Imports application data from the specified JSON file.
    ```bash
    python -m noox_pkg.main import path/to/your/apps.json
    ```

*   **`list`:**
    Lists all applications currently loaded from the JSON file.
    ```bash
    python -m noox_pkg.main list
    ```

*   **`download [--all-apps | <app_name>]`:**
    Downloads applications.
    *   To download a specific application:
        ```bash
        python -m noox_pkg.main download "My Application Name"
        ```
    *   To download all loaded applications:
        ```bash
        python -m noox_pkg.main download --all-apps
        ```

*   **`set-dir <directory_path>`:**
    Sets the directory where downloaded files will be saved. The directory will be created if it doesn't exist.
    ```bash
    python -m noox_pkg.main set-dir path/to/your/downloads_folder
    ```

*   **`--help`:**
    Show help for commands.
    ```bash
    python -m noox_pkg.main --help
    python -m noox_pkg.main import --help
    # and so on for other commands
    ```

## JSON File Format

The JSON file you import should be an object where keys are application names (strings) and values are their corresponding download URLs (strings).

**Example (`apps.json`):**
```json
{
  "MyCoolApp": "http://example.com/downloads/mycoolapp.exe",
  "AnotherTool": "https://codeload.github.com/user/repo/zip/refs/heads/main",
  "UtilityScript": "http://server.com/scripts/utility.zip"
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
