
import tkinter as tk # Ensure tk is imported directly
from tkinter import ttk, filedialog, messagebox
# from ttkthemes import ThemedTk # Comment out for now
import os

# Assuming utils is in the same package directory
from .utils import json_parser, downloader

# Fallback for DOWNLOAD_DIR if cli module is not found
try:
    from .cli import DOWNLOAD_DIR as CLI_DOWNLOAD_DIR
except ImportError:
    CLI_DOWNLOAD_DIR = "downloads"


class AppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Noox App Downloader")

        # --- Theme and Style Setup ---
        # 1. Set root window background
        self.root.configure(bg='#1A1A1A')

        # 2. Initialize ttk.Style
        style = ttk.Style(self.root)

        # 3. Attempt to set 'clam' as the base theme
        available_themes = style.theme_names()
        print(f"Available themes: {available_themes}")
        if 'clam' in available_themes:
            try:
                style.theme_use('clam')
                print("Using 'clam' theme as base.")
            except tk.TclError as e:
                print(f"Failed to use 'clam' theme: {e}. Styling might not work as expected.")
        else:
            print("'clam' theme not available. Styling might not work as expected.")

        # --- Custom 'Gamer' Style Definitions ---
        # Main Frame Style
        style.configure('Main.TFrame', background='#1A1A1A')

        # LabelFrame Style (for "Applications" box)
        style.configure('Custom.TLabelframe', background='#1A1A1A', borderwidth=1, relief="solid", bordercolor="#00FF00") # Neon green border
        style.configure('Custom.TLabelframe.Label', foreground='#00FF00', background='#1A1A1A', font=('TkDefaultFont', 10, 'bold'))

        # General Label Style (example, can be applied if needed)
        style.configure('Custom.TLabel', foreground='#E0E0E0', background='#1A1A1A')

        # Button Style ('Neon.TButton')
        style.configure('Neon.TButton', foreground='#00FF00', background='#333333', font=('TkDefaultFont', 9, 'bold'), borderwidth=1, relief="solid", bordercolor="#00FF00")
        style.map('Neon.TButton',
                  background=[('active', '#444444'), ('pressed', '#222222')],
                  foreground=[('active', '#33FF33')],
                  relief=[('pressed', 'sunken'), ('!pressed', 'solid')])

        # Treeview Style
        style.configure('Custom.Treeview', background='#2B2B2B', fieldbackground='#2B2B2B', foreground='#E0E0E0',
                        borderwidth=1, relief='solid', bordercolor="#00FF00")
        style.map('Custom.Treeview',
                  background=[('selected', '#004C99')],
                  foreground=[('selected', '#FFFFFF')])
        style.configure('Custom.Treeview.Heading', background='#333333', foreground='#00FF00',
                        font=('TkDefaultFont', 9, 'bold'), relief='flat')
        style.map('Custom.Treeview.Heading', background=[('active', '#444444')])

        # Scrollbar Style
        style.configure('Custom.Vertical.TScrollbar', gripcount=0, background='#333333', troughcolor='#1A1A1A',
                        bordercolor='#333333', lightcolor='#333333', darkcolor='#333333', arrowcolor='#00FF00')
        style.map('Custom.Vertical.TScrollbar', background=[('active', '#444444')])
        style.configure('Custom.Horizontal.TScrollbar', gripcount=0, background='#333333', troughcolor='#1A1A1A',
                        bordercolor='#333333', lightcolor='#333333', darkcolor='#333333', arrowcolor='#00FF00')
        style.map('Custom.Horizontal.TScrollbar', background=[('active', '#444444')])

        # --- Initialize GUI Elements with Styles ---
        self.current_download_dir = CLI_DOWNLOAD_DIR
        self.loaded_apps = {}

        main_frame = ttk.Frame(self.root, padding="10", style='Main.TFrame')

        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        app_list_frame = ttk.LabelFrame(main_frame, text="Applications", padding="10", style='Custom.TLabelframe')
        app_list_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        app_list_frame.columnconfigure(0, weight=1)
        app_list_frame.rowconfigure(0, weight=1)

        self.app_tree = ttk.Treeview(app_list_frame, columns=("App Name", "URL"), show="headings", style='Custom.Treeview')
        self.app_tree.heading("App Name", text="App Name") # Headings styled by Custom.Treeview.Heading

        self.app_tree.heading("URL", text="URL")
        self.app_tree.column("App Name", width=200, stretch=tk.YES)
        self.app_tree.column("URL", width=400, stretch=tk.YES)

        tree_scrollbar_y = ttk.Scrollbar(app_list_frame, orient="vertical", command=self.app_tree.yview, style='Custom.Vertical.TScrollbar')
        tree_scrollbar_x = ttk.Scrollbar(app_list_frame, orient="horizontal", command=self.app_tree.xview, style='Custom.Horizontal.TScrollbar')

        self.app_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)

        self.app_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))

        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        self.import_button = ttk.Button(main_frame, text="Import JSON", command=self.import_json, style='Neon.TButton')
        self.import_button.grid(row=1, column=0, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.download_selected_button = ttk.Button(main_frame, text="Download Selected", command=self.download_selected, style='Neon.TButton')
        self.download_selected_button.grid(row=1, column=1, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.download_all_button = ttk.Button(main_frame, text="Download All", command=self.download_all, style='Neon.TButton')
        self.download_all_button.grid(row=1, column=2, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.set_dir_button = ttk.Button(main_frame, text="Set Download Directory", command=self.set_download_dir, style='Neon.TButton')
        self.set_dir_button.grid(row=1, column=3, padx=5, pady=10, sticky=(tk.W, tk.E))

        self.status_bar_text = tk.StringVar()
        self.update_status(f"Ready. Download directory: {self.current_download_dir}")
        # Configure status_bar directly as it's a simple ttk.Label
        status_bar = ttk.Label(main_frame, textvariable=self.status_bar_text, relief=tk.FLAT, anchor=tk.W)
        status_bar.configure(background='#1A1A1A', foreground='#00FF00', padding="5", font=('TkDefaultFont', 8))
        status_bar.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E))

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.columnconfigure(3, weight=1)

    def import_json(self):
        filepath = filedialog.askopenfilename(
            title="Select JSON file",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filepath:
            try:
                data = json_parser.load_apps_from_json(filepath)
                if data is not None:
                    self.loaded_apps = data
                    self.populate_app_list()
                    filename = os.path.basename(filepath)
                    self.update_status(f"Successfully imported {len(self.loaded_apps)} apps from {filename}.")
                    if not self.loaded_apps:
                         messagebox.showinfo("Import Info", f"The JSON file '{filename}' was valid but contained no applications.")
                else:
                    filename = os.path.basename(filepath)
                    self.update_status(f"Failed to import apps from {filename}. Check console for details.")
                    messagebox.showerror("Import Error", f"Could not load apps from {filename}. It might be corrupted or not a valid app list JSON.")
            except Exception as e:
                filename = os.path.basename(filepath) if filepath else "selected file"
                self.update_status(f"An unexpected error occurred importing {filename}: {e}")
                messagebox.showerror("Import Error", f"An unexpected error occurred while importing {filename}: {e}")
        else:
            self.update_status("Import cancelled.")

    def populate_app_list(self):
        for i in self.app_tree.get_children():
            self.app_tree.delete(i)
        for app_name, url in self.loaded_apps.items():
            self.app_tree.insert("", tk.END, values=(app_name, url))

    def download_selected(self):
        selected_items = self.app_tree.selection()
        if not selected_items:
            messagebox.showwarning("No Selection", "Please select an application to download.")
            self.update_status("No application selected for download.")
            return

        selected_item = selected_items[0]
        item_values = self.app_tree.item(selected_item, 'values')
        app_name = item_values[0]
        url = item_values[1]

        self.update_status(f"Downloading {app_name}...")
        self.root.update_idletasks()

        if not self.create_dir_if_not_exists(self.current_download_dir):
            messagebox.showerror("Download Error", f"Download directory {self.current_download_dir} does not exist and could not be created.")
            self.update_status(f"Download directory error for {app_name}.")
            return

        success = downloader.download_file(url, self.current_download_dir, app_name)

        if success:
            download_path = os.path.join(self.current_download_dir, app_name)
            self.update_status(f"{app_name} downloaded successfully.")
            messagebox.showinfo("Download Complete", f"{app_name} downloaded successfully to {download_path}")
        else:
            self.update_status(f"Failed to download {app_name}. Check console for details.")
            messagebox.showerror("Download Error", f"Failed to download {app_name}. See console for details.")

    def download_all(self):
        if not self.loaded_apps:
            messagebox.showwarning("No Apps", "No applications loaded to download. Please import a JSON file first.")
            self.update_status("No applications to download.")
            return

        if not self.create_dir_if_not_exists(self.current_download_dir):
            messagebox.showerror("Download Error", f"Download directory {self.current_download_dir} does not exist and could not be created. Cannot download all apps.")
            self.update_status(f"Download directory error. Cannot download all.")
            return

        success_count = 0
        fail_count = 0
        total_apps = len(self.loaded_apps)

        self.update_status(f"Starting download of all {total_apps} applications...")
        self.root.update_idletasks()

        for i, (app_name, url) in enumerate(self.loaded_apps.items()):
            self.update_status(f"Downloading {app_name} ({i + 1}/{total_apps})...")
            self.root.update_idletasks()

            download_success = downloader.download_file(url, self.current_download_dir, app_name)

            if download_success:
                success_count += 1
                print(f"Successfully downloaded {app_name}")
            else:
                fail_count += 1
                print(f"Failed to download {app_name}")

        summary_message = f"All downloads attempted. Successful: {success_count}, Failed: {fail_count}."
        self.update_status(summary_message)
        messagebox.showinfo("Download All Complete", summary_message)

    def set_download_dir(self):
        new_dir = filedialog.askdirectory(mustexist=False, title="Select Download Directory", initialdir=self.current_download_dir)
        if new_dir:
            abs_new_dir = os.path.abspath(new_dir)
            if self.create_dir_if_not_exists(abs_new_dir):
                 self.current_download_dir = abs_new_dir
                 self.update_status(f"Download directory set to: {self.current_download_dir}")
            else:
                 messagebox.showerror("Set Directory Error", f"Could not access or create directory '{abs_new_dir}'. Please check path and permissions.")
                 self.update_status(f"Failed to set download directory to {abs_new_dir}.")
        else:
            self.update_status("Set download directory cancelled.")

    def create_dir_if_not_exists(self, directory_path):
        try:
            if not os.path.isdir(directory_path):
                os.makedirs(directory_path, exist_ok=True)
                print(f"Created directory: {directory_path}")
            return True
        except OSError as e:
            self.update_status(f"Error creating directory {directory_path}: {e}")
            print(f"OSError creating directory {directory_path}: {e}")
            return False

    def update_status(self, message):
        self.status_bar_text.set(message)

def start_gui():
    root = tk.Tk()
    # Removed root.set_theme() calls from here
    app = AppGUI(root)
    root.mainloop()

if __name__ == '__main__':
    start_gui()
