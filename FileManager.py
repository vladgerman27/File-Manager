import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import datetime
import shutil

class FileManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Manager")
        
        self.current_directory = tk.StringVar()
        self.current_directory.set(os.getcwd())  # Set the current directory to the initial
        
        self.history_stack = []  # Stack to store visited directories
        self.clipboard = {'action': None, 'path': None}  # Clipboard
        
        self.create_widgets()
        self.populate_file_list()

    def edit_path(self):
        self.entry_path.config(state="normal")  # Enable editing
        self.entry_path.focus_set()  # Set focus
        self.entry_path.select_range(0, tk.END)  # Select all text

    def save_path(self, event=None):
        new_path = self.entry_path.get()
        if os.path.exists(new_path):
            self.current_directory.set(new_path)
            self.history_stack.append(new_path)  # Add new directory to history stack
            self.populate_file_list()
        else:
            messagebox.showerror("Error", "Path does not exist.")
        self.entry_path.config(state="readonly")  # Disable editing

    def create_widgets(self):
        frame_path = tk.Frame(self.root)
        frame_path.pack(fill=tk.X, pady=5)

        # Input path to directory
        self.entry_path = ttk.Entry(frame_path, textvariable=self.current_directory, font=('Roboto', 12), state="readonly")
        self.entry_path.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.entry_path.bind("<Double-1>", lambda event: self.edit_path())  # Edit on double click
        self.entry_path.bind("<Return>", self.save_path)  # Save on Enter

        # Select directory button
        btn_select_dir = ttk.Button(frame_path, text="Select Folder", command=self.select_directory)
        btn_select_dir.pack(side=tk.RIGHT, padx=5)
        
        # Search input and search button
        frame_search = tk.Frame(self.root)
        frame_search.pack(fill=tk.X, padx=5, pady=5)
        
        self.entry_search = ttk.Entry(frame_search, width=50, font=('Roboto', 10))
        self.entry_search.grid(row=0, column=0)
        
        btn_search = ttk.Button(frame_search, text="Search", command=self.search_files)
        btn_search.grid(row=0, column=1, padx=5)
        
        # Load icon for refresh button
        self.refresh_icon = tk.PhotoImage(file="img\\refresh.png")

        # Refresh button
        btn_refresh = ttk.Button(frame_search, image=self.refresh_icon, command=self.populate_file_list)
        btn_refresh.grid(row=0, column=2, padx=5)

        # Navigation buttons
        btn_up = ttk.Button(frame_search, text="<", command=self.go_up_directory)
        btn_up.grid(row=0, column=3)

        btn_forward = ttk.Button(frame_search, text=">", command=self.go_forward_directory)
        btn_forward.grid(row=0, column=4)
        
        # Treeview to display files and folders with icons
        self.treeview_files = ttk.Treeview(self.root, columns=("date_modified"), selectmode="extended")
        self.treeview_files.heading("#0", text="Name")
        self.treeview_files.heading("date_modified", text="Date Modified")
        self.treeview_files.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Scrollbar for treeview
        scrollbar_treeview = ttk.Scrollbar(self.root, orient="vertical", command=self.treeview_files.yview)
        scrollbar_treeview.pack(side=tk.RIGHT, fill="y")
        self.treeview_files.configure(yscrollcommand=scrollbar_treeview.set)
        
        # Load folder and file icons
        self.folder_icon = tk.PhotoImage(file="img\\folder.png")
        self.file_icon = tk.PhotoImage(file="img\\file.png")
        
        # Bind double click event to open file or directory
        self.treeview_files.bind("<Double-1>", self.open_file_or_directory)
        
        # Create context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Open", command=self.open_file_or_directory)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Create File", command=self.create_file)
        self.context_menu.add_command(label="Create Directory", command=self.create_directory)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename", command=self.rename_file)
        self.context_menu.add_command(label="Delete", command=self.delete_file)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy", command=self.copy_file)
        self.context_menu.add_command(label="Paste", command=self.paste_file)
        self.context_menu.add_command(label="Cut", command=self.cut_file)
        self.treeview_files.bind("<Control-c>", self.copy_file)
        self.treeview_files.bind("<Control-v>", self.paste_file)
        self.treeview_files.bind("<Control-x>", self.cut_file)
        
        # Bind context menu to treeview
        self.treeview_files.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def select_directory(self):
        selected_directory = filedialog.askdirectory()
        if selected_directory:
            self.current_directory.set(selected_directory)
            self.history_stack.append(selected_directory)  # Add new directory to history stack
            self.populate_file_list()
    
    def populate_file_list(self):
        self.treeview_files.delete(*self.treeview_files.get_children())  # Clear existing items
        parent_node = self.treeview_files.insert("", "end", text="..", image=self.folder_icon, open=True)  # Add ".." to go up
        for file in os.listdir(self.current_directory.get()):
            file_path = os.path.join(self.current_directory.get(), file)
            if os.path.isdir(file_path):
                self.treeview_files.insert(parent_node, "end", text=file, image=self.folder_icon, open=True)
            else:
                timestamp = os.path.getmtime(file_path)
                date_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                file_icon = self.get_file_icon(file)
                self.treeview_files.insert(parent_node, "end", text=file, image=file_icon, values=(date_modified,))
    
    def open_file_or_directory(self, event):
        selected_item = self.treeview_files.selection()
        if selected_item:
            selected_item = self.treeview_files.item(selected_item)
            file_name = selected_item["text"]
            if file_name == "..":
                self.go_up_directory()
            else:
                path_to_item = os.path.join(self.current_directory.get(), file_name)
                if os.path.isdir(path_to_item):
                    self.current_directory.set(path_to_item)
                    self.history_stack.append(path_to_item)  # Add new directory to history stack
                    self.populate_file_list()
                else:
                    os.system(f'start "" "{path_to_item}"')  # Open file with default application
    
    def create_file(self):
        new_file_name = simpledialog.askstring("Create File", "Enter file name and type")
        if new_file_name:
            new_file_path = os.path.join(self.current_directory.get(), new_file_name)
            try:
                with open(new_file_path, 'w') as new_file:
                    pass  # Create empty file
                self.populate_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error creating file: {e}")
    
    def create_directory(self):
        new_directory_name = simpledialog.askstring("Create Directory", "Enter directory name:")
        if new_directory_name:
            new_directory_path = os.path.join(self.current_directory.get(), new_directory_name)
            try:
                os.makedirs(new_directory_path)
                self.populate_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error creating directory: {e}")
    
    def delete_file(self):
        selected_item = self.treeview_files.selection()
        if selected_item:
            selected_item = self.treeview_files.item(selected_item)
            file_name = selected_item["text"]
            path_to_item = os.path.join(self.current_directory.get(), file_name)
            try:
                if os.path.isdir(path_to_item):
                    os.rmdir(path_to_item)
                else:
                    os.remove(path_to_item)
                self.populate_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting {file_name}: {e}")
    
    def rename_file(self):
        selected_item = self.treeview_files.selection()
        if selected_item:
            selected_item = self.treeview_files.item(selected_item)
            file_name = selected_item["text"]
            new_name = simpledialog.askstring("Rename File", f"Enter new name for file {file_name}:")
            if new_name:
                old_path = os.path.join(self.current_directory.get(), file_name)
                new_path = os.path.join(self.current_directory.get(), new_name)
                try:
                    os.rename(old_path, new_path)
                    self.populate_file_list()
                except Exception as e:
                    messagebox.showerror("Error", f"Error renaming {file_name}: {e}")
    
    def go_up_directory(self):
        current_dir = self.current_directory.get()
        parent_dir = os.path.dirname(current_dir)
        if parent_dir:
            self.current_directory.set(parent_dir)
            self.history_stack.append(current_dir)  # Add current directory to history stack
            self.populate_file_list()

    def go_forward_directory(self):
        if self.history_stack:
            forward_directory = self.history_stack.pop()
            self.current_directory.set(forward_directory)
            self.populate_file_list()
    
    def search_files(self):
        search_term = self.entry_search.get()
        if search_term:
            found_files = [file for file in os.listdir(self.current_directory.get()) if search_term.lower() in file.lower()]
            self.treeview_files.delete(*self.treeview_files.get_children())
            parent_node = self.treeview_files.insert("", "end", text="..", image=self.folder_icon)  # Add ".." to go up
            for file in found_files:
                file_path = os.path.join(self.current_directory.get(), file)
                if os.path.isdir(file_path):
                    self.treeview_files.insert(parent_node, "end", text=file, image=self.folder_icon)
                else:
                    timestamp = os.path.getmtime(file_path)
                    date_modified = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
                    file_icon = self.get_file_icon(file)
                    self.treeview_files.insert(parent_node, "end", text=file, image=file_icon, values=(date_modified,))
    
    def get_file_icon(self, file_name):
        file_ext = file_name.split(".")[-1].lower()
        if file_ext in ["jpg", "png", "jpeg", "gif"]:
            return self.image_photo_icon
        elif file_ext in ["html", "webp", "webm"]:
            return self.image_browser_icon
        elif file_ext in ["mp3", "wav", "ape"]:
            return self.image_music_icon
        elif file_ext in ["mp4", "avi", "mov"]:
            return self.image_video_icon
        else:
            return self.file_icon
    
    def copy_file(self, event=None):
        selected_items = self.treeview_files.selection()
        if selected_items:
            selected_files = [self.treeview_files.item(item)["text"] for item in selected_items]
            self.clipboard['action'] = 'copy'
            self.clipboard['path'] = [os.path.join(self.current_directory.get(), file) for file in selected_files]
    
    def paste_file(self, event=None):
        if self.clipboard['action'] == 'copy':
            for file_path in self.clipboard['path']:
                try:
                    if os.path.isdir(file_path):
                        shutil.copytree(file_path, os.path.join(self.current_directory.get(), os.path.basename(file_path)))
                    else:
                        shutil.copy2(file_path, self.current_directory.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Error copying file: {e}")
            self.populate_file_list()
        elif self.clipboard['action'] == 'cut':
            for file_path in self.clipboard['path']:
                try:
                    if os.path.isdir(file_path):
                        shutil.move(file_path, os.path.join(self.current_directory.get(), os.path.basename(file_path)))
                    else:
                        shutil.move(file_path, self.current_directory.get())
                except Exception as e:
                    messagebox.showerror("Error", f"Error cutting file: {e}")
            self.populate_file_list()

    
    def cut_file(self, event=None):
        selected_items = self.treeview_files.selection()
        if selected_items:
            selected_files = [self.treeview_files.item(item)["text"] for item in selected_items]
            self.clipboard['action'] = 'cut'
            self.clipboard['path'] = [os.path.join(self.current_directory.get(), file) for file in selected_files]

if __name__ == "__main__":
    root = tk.Tk()
    app = FileManagerApp(root)
    
    # Load icons for different file types
    app.image_photo_icon = tk.PhotoImage(file="img\\img.png")
    app.image_browser_icon = tk.PhotoImage(file="img\\web.png")
    app.image_music_icon = tk.PhotoImage(file="img\\song.png")
    app.image_video_icon = tk.PhotoImage(file="img\\video.png")
    
    root.mainloop()
