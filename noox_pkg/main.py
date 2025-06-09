import argparse
import os # Added for DOWNLOAD_DIR creation
import sys

# Adjust sys.path to correctly import from .cli
# This assumes main.py is in 'noox_pkg/' and cli.py is also in 'noox_pkg/'
# If running 'python noox_pkg/main.py', the current working directory is the parent of 'noox_pkg'
# So 'noox_pkg' is a package that can be imported from.
# If running 'python main.py' from within 'noox_pkg', then '.' is 'noox_pkg'
# The from .cli import ... should work if the parent directory of noox_pkg is in sys.path
# Or if we are running the script with python -m noox_pkg.main

# Ensure the parent directory of 'noox_pkg' is in sys.path
# so that 'from noox_pkg.cli import ...' works, or alternatively use 'from .cli import ...'
# when 'noox_pkg' itself is treated as a package.

# If this script is run as `python noox_pkg/main.py`, the CWD is the parent of `noox_pkg`.
# Python automatically adds the script's directory (`noox_pkg/`) to `sys.path` (when run as script)
# or the parent directory (when run as module using -m).
# For `from .cli` to work reliably, this file should be treated as part of a package.
# This is achieved by running `python -m noox_pkg.main`.

# Ensure cli module can be found using relative import.
from .cli import handle_import, handle_list_apps, handle_download, handle_set_download_dir, DOWNLOAD_DIR

def main():
    parser = argparse.ArgumentParser(description="noox pkg - A CLI application downloader.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands", required=True)

    # Import command
    import_parser = subparsers.add_parser("import", help="Import applications from a JSON file.")
    import_parser.add_argument("filepath", type=str, help="Path to the JSON file.")

    # List command
    list_parser = subparsers.add_parser("list", help="List loaded applications.")

    # Download command
    download_parser = subparsers.add_parser("download", help="Download an application. Specify an app name or use --all-apps.")
    # Make app_name optional by using nargs='?' and providing a default of None.
    download_parser.add_argument("app_name", type=str, nargs='?', default=None, help="Name of the specific app to download.")
    download_parser.add_argument("--all-apps", action="store_true", help="Download all applications from the loaded list.")

    # Set download directory command
    set_dir_parser = subparsers.add_parser("set-dir", help="Set the download directory for files.")
    set_dir_parser.add_argument("directory", type=str, help="Path to the download directory.")

    args = parser.parse_args()

    # Create default download directory if it doesn't exist, relevant for download commands
    if args.command == "download" or args.command == "set-dir":
        # Access DOWNLOAD_DIR from cli module, it might have been updated by set-dir
        # For simplicity, we'll use the one imported at the start, or re-fetch if necessary.
        # A better state management would be good here.
        current_download_dir = DOWNLOAD_DIR
        if hasattr(args, 'directory') and args.command == "set-dir": # If set-dir is called
             current_download_dir = args.directory # This will be the new directory

        if not os.path.exists(current_download_dir):
            try:
                os.makedirs(current_download_dir)
                print(f"Created download directory: {current_download_dir}")
            except OSError as e:
                print(f"Error creating download directory {current_download_dir}: {e}")
                # Decide if we should exit or let the command proceed and potentially fail later
                # For now, let it proceed

    if args.command == "import":
        handle_import(args.filepath)
    elif args.command == "list":
        handle_list_apps()
    elif args.command == "download":
        handle_download(args.app_name)
    elif args.command == "set-dir":
        # The DOWNLOAD_DIR in cli.py is updated by this handler
        handle_set_download_dir(args.directory)


if __name__ == "__main__":
    main()
