import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
# import queue # Not using queue for this approach

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
        self.is_downloading_all = False
        self.apps_to_download_queue = []

        # --- Color Scheme Definitions ---
        self.color_schemes = {
            "Neon Verde": {
                "accent": "#00FF00", "accent_hover": "#33FF33",
                "text_selection_fg": "#FFFFFF", "text_selection_bg": "#004C99"
            },
            "Neon Azul": {
                "accent": "#00FFFF", "accent_hover": "#33FFFF",
                "text_selection_fg": "#000000", "text_selection_bg": "#00B8B8"
            },
            "Neon Magenta": {
                "accent": "#FF00FF", "accent_hover": "#FF33FF",
                "text_selection_fg": "#FFFFFF", "text_selection_bg": "#8B008B"
            },
            "Cyber Rojo": {
                "accent": "#FF0000", "accent_hover": "#FF3333",
                "text_selection_fg": "#FFFFFF", "text_selection_bg": "#8B0000"
            }
        }
        self.current_scheme_name = "Neon Verde"
        self.current_accent_color = self.color_schemes[self.current_scheme_name]["accent"]
        self.current_accent_hover_color = self.color_schemes[self.current_scheme_name]["accent_hover"]
        self.current_text_selection_fg = self.color_schemes[self.current_scheme_name]["text_selection_fg"]
        self.current_text_selection_bg = self.color_schemes[self.current_scheme_name]["text_selection_bg"]

        # --- Theme and Style Setup ---
        self.root.configure(bg='#1A1A1A')
        style = ttk.Style(self.root)
        available_themes = style.theme_names()
        print(f"Available themes: {available_themes}")
        if 'clam' in available_themes:
            try: style.theme_use('clam'); print("Using 'clam' theme as base.")
            except tk.TclError as e: print(f"Failed to use 'clam' theme: {e}.")
        else: print("'clam' theme not available.")

        style.configure('Main.TFrame', background='#1A1A1A')
        style.configure('Custom.TLabelframe', background='#1A1A1A', borderwidth=1, relief="solid", bordercolor=self.current_accent_color)
        style.configure('Custom.TLabelframe.Label', foreground=self.current_accent_color, background='#1A1A1A', font=('TkDefaultFont', 10, 'bold'))
        style.configure('Custom.TLabel', foreground='#E0E0E0', background='#1A1A1A')
        style.configure('Neon.TButton', foreground=self.current_accent_color, background='#333333', font=('TkDefaultFont', 9, 'bold'), borderwidth=1, relief="solid", bordercolor=self.current_accent_color)
        style.map('Neon.TButton', background=[('active', '#444444'), ('pressed', '#222222')], foreground=[('active', self.current_accent_hover_color)], relief=[('pressed', 'sunken'), ('!pressed', 'solid')])
        style.configure('Custom.Treeview', background='#2B2B2B', fieldbackground='#2B2B2B', foreground='#E0E0E0', borderwidth=1, relief='solid', bordercolor=self.current_accent_color)
        style.map('Custom.Treeview', background=[('selected', self.current_text_selection_bg)], foreground=[('selected', self.current_text_selection_fg)])
        style.configure('Custom.Treeview.Heading', background='#333333', foreground=self.current_accent_color, font=('TkDefaultFont', 9, 'bold'), relief='flat')
        style.map('Custom.Treeview.Heading', background=[('active', '#444444')])
        for orient, SbarStyle in [("vertical", "Custom.Vertical.TScrollbar"), ("horizontal", "Custom.Horizontal.TScrollbar")]:
            style.configure(SbarStyle, gripcount=0, background='#333333', troughcolor='#1A1A1A', bordercolor='#333333', lightcolor='#333333', darkcolor='#333333', arrowcolor=self.current_accent_color)
            style.map(SbarStyle, background=[('active', '#444444')])
        style.configure('Accent.Horizontal.TProgressbar', background=self.current_accent_color, troughcolor='#333333', bordercolor=self.current_accent_color, lightcolor=self.current_accent_color, darkcolor=self.current_accent_color)

        self.current_download_dir = CLI_DOWNLOAD_DIR
        self.loaded_apps = {}
        main_frame = ttk.Frame(self.root, padding="10", style='Main.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1); self.root.rowconfigure(0, weight=1)
        app_list_frame = ttk.LabelFrame(main_frame, text="Applications", padding="10", style='Custom.TLabelframe')
        app_list_frame.grid(row=0, column=0, columnspan=4, padx=5, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        app_list_frame.columnconfigure(0, weight=1); app_list_frame.rowconfigure(0, weight=1)
        self.app_tree = ttk.Treeview(app_list_frame, columns=("App Name", "URL"), show="headings", style='Custom.Treeview')
        self.app_tree.heading("App Name", text="App Name"); self.app_tree.heading("URL", text="URL")
        self.app_tree.column("App Name", width=200, stretch=tk.YES); self.app_tree.column("URL", width=400, stretch=tk.YES)
        tree_scrollbar_y = ttk.Scrollbar(app_list_frame, orient="vertical", command=self.app_tree.yview, style='Custom.Vertical.TScrollbar')
        tree_scrollbar_x = ttk.Scrollbar(app_list_frame, orient="horizontal", command=self.app_tree.xview, style='Custom.Horizontal.TScrollbar')
        self.app_tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        self.app_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S)); tree_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S)); tree_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        for i in range(4): main_frame.columnconfigure(i, weight=1)
        self.import_button = ttk.Button(main_frame, text="Import JSON", command=self.import_json, style='Neon.TButton')
        self.import_button.grid(row=1, column=0, padx=5, pady=10, sticky=(tk.W, tk.E))
        self.download_selected_button = ttk.Button(main_frame, text="Download Selected", command=self.download_selected, style='Neon.TButton')
        self.download_selected_button.grid(row=1, column=1, padx=5, pady=10, sticky=(tk.W, tk.E))
        self.download_all_button = ttk.Button(main_frame, text="Download All", command=self.download_all, style='Neon.TButton')
        self.download_all_button.grid(row=1, column=2, padx=5, pady=10, sticky=(tk.W, tk.E))
        self.set_dir_button = ttk.Button(main_frame, text="Set Download Directory", command=self.set_download_dir, style='Neon.TButton')
        self.set_dir_button.grid(row=1, column=3, padx=5, pady=10, sticky=(tk.W, tk.E))
        scheme_label = ttk.Label(main_frame, text="Color Scheme:"); scheme_label.configure(background='#1A1A1A', foreground='#E0E0E0')
        scheme_label.grid(row=2, column=0, padx=(5,0), pady=5, sticky=tk.W)
        self.scheme_combobox = ttk.Combobox(main_frame, values=list(self.color_schemes.keys()), state="readonly", width=15)
        self.scheme_combobox.set(self.current_scheme_name); self.scheme_combobox.grid(row=2, column=1, padx=(0,5), pady=5, sticky=tk.W)
        self.scheme_combobox.bind("<<ComboboxSelected>>", self.on_scheme_selected)
        self.progress_bar = ttk.Progressbar(main_frame, orient='horizontal', mode='determinate', length=200, style='Accent.Horizontal.TProgressbar')
        self.progress_bar.grid(row=3, column=0, columnspan=4, padx=5, pady=(5,0), sticky=(tk.W, tk.E)); self.progress_bar['value'] = 0
        self.status_bar_text = tk.StringVar(); self.update_status(f"Ready. Download directory: {self.current_download_dir}")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_bar_text, relief=tk.FLAT, anchor=tk.W)
        self.status_bar.configure(background='#1A1A1A', foreground=self.current_accent_color, padding="5", font=('TkDefaultFont', 8))
        self.status_bar.grid(row=4, column=0, columnspan=4, sticky=(tk.W, tk.E))

    def _update_gui_progress(self, percentage, current_bytes_str):
        if percentage is not None:
            if self.progress_bar['mode'] == 'indeterminate': self.progress_bar.stop(); self.progress_bar.configure(mode='determinate')
            self.progress_bar['value'] = percentage
            self.update_status(f"Downloading... {percentage:.1f}% ({current_bytes_str})")
        else:
            if self.progress_bar['value'] == 0 and self.progress_bar['mode'] == 'determinate': self.progress_bar.configure(mode='indeterminate'); self.progress_bar.start(10)
            self.update_status(f"Downloading... {current_bytes_str} (total size unknown)")

    def prepare_for_download(self):
        self.progress_bar['value'] = 0
        if self.progress_bar['mode'] == 'indeterminate': self.progress_bar.stop()
        self.progress_bar.configure(mode='determinate')
        self.download_selected_button.config(state=tk.DISABLED); self.download_all_button.config(state=tk.DISABLED)

    def cleanup_after_download(self):
        self.progress_bar['value'] = 0
        if self.progress_bar['mode'] == 'indeterminate': self.progress_bar.stop(); self.progress_bar.configure(mode='determinate')
        self.download_selected_button.config(state=tk.NORMAL); self.download_all_button.config(state=tk.NORMAL)

    def _download_thread_target(self, url, app_name, dest_folder):
        try:
            def progress_callback_wrapper(bytes_downloaded, total_size, percentage):
                current_size_str = f"{bytes_downloaded // 1024}KB"
                if total_size: current_size_str = f"{bytes_downloaded // 1024}KB / {total_size // 1024}KB"
                self.root.after_idle(self._update_gui_progress, percentage, current_size_str)

            success = downloader.download_file(url, dest_folder, app_name, progress_callback=progress_callback_wrapper)
            final_message = ""
            if success:
                final_message = f"{app_name} downloaded successfully to {os.path.join(dest_folder, app_name)}"
                self.root.after_idle(messagebox.showinfo, "Download Complete", final_message)
            else:
                final_message = f"Failed to download {app_name}. Check console for details."
                self.root.after_idle(messagebox.showerror, "Download Error", final_message)
            self.root.after_idle(self.update_status, final_message)
        except Exception as e:
            error_msg = f"Unexpected error downloading {app_name}: {e}"; print(error_msg)
            self.root.after_idle(self.update_status, error_msg)
            self.root.after_idle(messagebox.showerror, "Download Error", error_msg)
        finally:
            if not self.is_downloading_all: self.root.after_idle(self.cleanup_after_download)

    def download_selected(self):
        selected_items = self.app_tree.selection()
        if not selected_items: messagebox.showwarning("No Selection", "Please select an application to download."); self.update_status("No application selected."); return
        item_values = self.app_tree.item(selected_items[0], 'values'); app_name, url = item_values[0], item_values[1]
        if not self.create_dir_if_not_exists(self.current_download_dir):
            messagebox.showerror("Download Error", f"Directory {self.current_download_dir} error."); self.update_status("Dir error."); return
        self.prepare_for_download(); self.update_status(f"Starting download for {app_name}...")
        self.is_downloading_all = False
        thread = threading.Thread(target=self._download_thread_target, args=(url, app_name, self.current_download_dir)); thread.daemon = True; thread.start()

    def _start_next_download_in_queue(self):
        if not self.apps_to_download_queue:
            self.is_downloading_all = False; self.root.after_idle(self.cleanup_after_download)
            self.root.after_idle(self.update_status, "All application downloads attempted.")
            self.root.after_idle(messagebox.showinfo, "Download All Complete", "All downloads attempted. Check console/status.")
            return
        app_name, url = self.apps_to_download_queue.pop(0)
        self.root.after_idle(self._update_gui_progress, 0, "0KB / ---") # Reset progress for next item
        self.root.after_idle(self.update_status, f"Queue: Downloading {app_name}...")
        thread = threading.Thread(target=self._download_all_thread_target_wrapper, args=(url, app_name, self.current_download_dir)); thread.daemon = True; thread.start()

    def _download_all_thread_target_wrapper(self, url, app_name, dest_folder):
        try: self._download_thread_target(url, app_name, dest_folder)
        except Exception as e: print(f"Wrapper error for {app_name}: {e}"); self.root.after_idle(self.update_status, f"Critical error with {app_name}.")
        finally:
            if self.is_downloading_all: self.root.after_idle(self._start_next_download_in_queue)

    def download_all(self):
        if not self.loaded_apps: messagebox.showwarning("No Apps", "No applications loaded."); self.update_status("No apps to download."); return
        if not self.create_dir_if_not_exists(self.current_download_dir): messagebox.showerror("Download Error", f"Directory {self.current_download_dir} error."); self.update_status("Dir error."); return
        self.apps_to_download_queue = list(self.loaded_apps.items())
        if not self.apps_to_download_queue: messagebox.showinfo("Download All", "No apps in queue."); return
        self.is_downloading_all = True; self.prepare_for_download(); self.update_status(f"Queueing all {len(self.apps_to_download_queue)} apps...")
        self._start_next_download_in_queue()

    def on_scheme_selected(self, event): # Other methods like on_scheme_selected, apply_color_scheme, etc. are here
        selected_scheme_name = self.scheme_combobox.get()
        if selected_scheme_name: self.apply_color_scheme(selected_scheme_name)

    def apply_color_scheme(self, scheme_name):
        if scheme_name not in self.color_schemes: print(f"Error: Scheme '{scheme_name}' not found."); self.update_status(f"Scheme Error."); return
        self.current_scheme_name = scheme_name; new_scheme = self.color_schemes[scheme_name]
        self.current_accent_color = new_scheme["accent"]; self.current_accent_hover_color = new_scheme["accent_hover"]
        self.current_text_selection_fg = new_scheme["text_selection_fg"]; self.current_text_selection_bg = new_scheme["text_selection_bg"]
        style = ttk.Style(self.root)
        style.configure('Custom.TLabelframe', bordercolor=self.current_accent_color)
        style.configure('Custom.TLabelframe.Label', foreground=self.current_accent_color)
        style.configure('Neon.TButton', foreground=self.current_accent_color, bordercolor=self.current_accent_color)
        style.map('Neon.TButton', foreground=[('active', self.current_accent_hover_color)])
        style.configure('Custom.Treeview', bordercolor=self.current_accent_color)
        style.map('Custom.Treeview', background=[('selected', self.current_text_selection_bg)], foreground=[('selected', self.current_text_selection_fg)])
        style.configure('Custom.Treeview.Heading', foreground=self.current_accent_color)
        for orient in ["Vertical", "Horizontal"]: style.configure(f'Custom.{orient}.TScrollbar', arrowcolor=self.current_accent_color)
        style.configure('Accent.Horizontal.TProgressbar', background=self.current_accent_color, bordercolor=self.current_accent_color, lightcolor=self.current_accent_color, darkcolor=self.current_accent_color)
        self.status_bar.configure(foreground=self.current_accent_color)
        self.update_status(f"Color scheme '{scheme_name}' applied."); print(f"Applied scheme: {scheme_name}")

    def import_json(self):
        filepath = filedialog.askopenfilename(title="Select JSON file", filetypes=(("JSON files", "*.json"), ("All files", "*.*")))
        if filepath:
            try:
                data = json_parser.load_apps_from_json(filepath)
                if data is not None:
                    self.loaded_apps = data; self.populate_app_list(); filename = os.path.basename(filepath)
                    self.update_status(f"Imported {len(self.loaded_apps)} apps from {filename}.")
                    if not self.loaded_apps: messagebox.showinfo("Import Info", f"JSON '{filename}' valid but no apps.")
                else: filename = os.path.basename(filepath); self.update_status(f"Failed import from {filename}."); messagebox.showerror("Import Error", f"Could not load from {filename}.")
            except Exception as e: filename = os.path.basename(filepath) if filepath else "file"; self.update_status(f"Error importing {filename}: {e}"); messagebox.showerror("Import Error", f"Error importing {filename}: {e}")
        else: self.update_status("Import cancelled.")

    def populate_app_list(self):
        for i in self.app_tree.get_children(): self.app_tree.delete(i)
        for app_name, url in self.loaded_apps.items(): self.app_tree.insert("", tk.END, values=(app_name, url))


    def set_download_dir(self):
        new_dir = filedialog.askdirectory(mustexist=False, title="Select Download Directory", initialdir=self.current_download_dir)
        if new_dir:
            abs_new_dir = os.path.abspath(new_dir)
            if self.create_dir_if_not_exists(abs_new_dir): self.current_download_dir = abs_new_dir; self.update_status(f"Download dir: {self.current_download_dir}")
            else: messagebox.showerror("Set Dir Error", f"Could not use dir '{abs_new_dir}'."); self.update_status(f"Failed set dir to {abs_new_dir}.")
        else: self.update_status("Set download directory cancelled.")

    def create_dir_if_not_exists(self, directory_path):
        try:
            if not os.path.isdir(directory_path): os.makedirs(directory_path, exist_ok=True); print(f"Created directory: {directory_path}")
            return True
        except OSError as e: self.update_status(f"Error creating dir {directory_path}: {e}"); print(f"OSError creating dir {directory_path}: {e}"); return False

    def update_status(self, message): self.status_bar_text.set(message)

def start_gui():
    root = tk.Tk(); app = AppGUI(root); root.mainloop()

if __name__ == '__main__': start_gui()

