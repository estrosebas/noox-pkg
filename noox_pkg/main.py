import argparse
import os
import sys

# Adjust imports to include start_gui
from .cli import handle_import, handle_list_apps, handle_download, handle_set_download_dir, DOWNLOAD_DIR
from .gui import start_gui # New import for GUI

def main():
    parser = argparse.ArgumentParser(description="noox pkg - A CLI application downloader with GUI support.")
    # Removed required=True from subparsers to allow defaulting to GUI
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import applications from a JSON file.")
    import_parser.add_argument("filepath", type=str, help="Path to the JSON file.")

    # List command
    list_parser = subparsers.add_parser("list", help="List loaded applications.")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download an application. Specify an app name or use --all-apps.")
    download_parser.add_argument("app_name", type=str, nargs='?', default=None, help="Name of the specific app to download.")
    download_parser.add_argument("--all-apps", action="store_true", help="Download all applications from the loaded list.")

    # Set download directory command
    set_dir_parser = subparsers.add_parser("set-dir", help="Set the download directory for files.")
    set_dir_parser.add_argument("directory", type=str, help="Path to the download directory.")

    # GUI command - New
    gui_parser = subparsers.add_parser("gui", help="Launch the Graphical User Interface.")

    args = parser.parse_args()

    # If no command is given or 'gui' command is explicitly used, launch GUI.
    if args.command is None or args.command == "gui":
        if args.command is None:
            print("No command specified, launching GUI...")
        start_gui()
    elif args.command == "import":
        # Ensure DOWNLOAD_DIR exists for commands that might need it.
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            print(f"Created download directory at: {DOWNLOAD_DIR}")
        handle_import(args.filepath)
    elif args.command == "list":
        handle_list_apps()
    elif args.command == "download":
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            print(f"Created download directory at: {DOWNLOAD_DIR}")

        if args.all_apps:
            if args.app_name:
                download_parser.error("Cannot specify an app_name when --all-apps is used.")
            handle_download("--all")
        elif args.app_name:
            handle_download(args.app_name)
        else:
            # No app_name and no --all-apps, show help for download command
            download_parser.print_help()
            sys.exit(1) # Exit with error as no valid download instruction was given

    elif args.command == "set-dir":
        # handle_set_download_dir will manage directory creation
        handle_set_download_dir(args.directory)
    # No other commands expected at this point based on parser setup

if __name__ == "__main__":
    main()
