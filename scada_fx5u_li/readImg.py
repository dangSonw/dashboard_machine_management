import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileExplorer(tk.Tk):
    def __init__(self, path):
        super().__init__()
        self.title("File Explorer")
        self.geometry("800x600")

        self.path = path

        self.tree = ttk.Treeview(self)
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.image_frame = tk.Frame(self)
        self.image_frame.pack(side="right", fill="both", expand=True)
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()

        self.refresh_tree()

        self.event_handler = ChangeHandler(self)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, self.path, recursive=True)
        self.observer.start()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        self.observer.stop()
        self.observer.join()
        self.destroy()

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        self.populate_tree("", self.path)

    def populate_tree(self, parent, path):
        if parent == "":
            parent_node = self.tree.insert(parent, "end", text=path, open=True)
        else:
            parent_node = parent

        try:
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    child_node = self.tree.insert(parent_node, "end", text=item, open=False)
                    self.populate_tree(child_node, item_path)
                else:
                    self.tree.insert(parent_node, "end", text=item, open=False)
        except Exception as e:
            self.tree.insert(parent_node, "end", text=f"Error: {e}")

    def on_tree_select(self, event):
        if not self.tree.selection():
            return
            
        selected_item = self.tree.selection()[0]
        
        path_parts = []
        current_item = selected_item
        while current_item:
            path_parts.insert(0, self.tree.item(current_item, "text"))
            parent = self.tree.parent(current_item)
            if parent == '':
                break
            current_item = parent

        full_path = os.path.join(self.path, *path_parts[1:])

        if os.path.isfile(full_path) and full_path.lower().endswith(".jpg"):
            self.show_image(full_path)
        elif os.path.isdir(full_path):
            self.tree.item(selected_item, open=not self.tree.item(selected_item, "open"))

    def show_image(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo)
            self.image_label.image = photo
        except Exception as e:
            print(f"Error opening image: {e}")
            self.image_label.config(image=None, text="Cannot display image")
            self.image_label.image = None

class ChangeHandler(FileSystemEventHandler):
    def __init__(self, app):
        self.app = app

    def on_any_event(self, event):
        self.app.after(100, self.app.refresh_tree)

if __name__ == "__main__":
    # NOTE: You might need to install Pillow and Watchdog:
    # pip install Pillow
    # pip install watchdog
    disk_path = r"C:\Users\Public\Documents\RAMDisk"
    if not os.path.exists(disk_path):
        os.makedirs(disk_path)
        with open(os.path.join(disk_path, "test.txt"), "w") as f:
            f.write("This is a test file.")
    
    app = FileExplorer(disk_path)
    app.mainloop()
