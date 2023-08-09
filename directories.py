#!/usr/bin/env python3
import os
import math
import random
import shutil
import tkinter as tk
from tkinter import messagebox
from tkinter import Listbox, Button
from tkinter import ttk
import tkinter.filedialog
source_folder_original = "/home/miki/Downloads/sssssssssssssss"
target_folder_original = "/home/miki/Downloads/target"
def find_subfolders_with_images(folder_path, image_extensions=("jpg", "jpeg", "bmp")):
    subfolders_with_images = []

    for root, dirs, files in os.walk(folder_path):
        # Calculate the depth of the current subfolder from the starting folder
        if root == folder_path:
            continue
        current_depth = root[len(folder_path):].count(os.sep)

        # Check if the current depth is greater than 1 (deeper than one subfolder)
        if current_depth > 1:
            continue

        image_files = [file for file in files if os.path.splitext(file)[1].lower().lstrip('.') in image_extensions]
        if image_files:
            subfolders_with_images.append(root)

    return subfolders_with_images
def compare_folders(source_folder, destination_folder):
    source_files = set(os.listdir(source_folder))
    destination_files = set(os.listdir(destination_folder))

    return not source_files.intersection(destination_files)

def move_random_folders_to_target(source_folder, target_folder, percentage=30):
    subfolders_with_images = find_subfolders_with_images(source_folder)


    num_folders_to_move = math.ceil(len(subfolders_with_images) * percentage / 100)
    selected_folders = random.sample(subfolders_with_images, num_folders_to_move)

    for folder in selected_folders:
        subfolder_name = os.path.relpath(folder, source_folder)
        destination_path = os.path.join(target_folder, subfolder_name)

        # Check if the destination folder already exists
        if os.path.exists(destination_path):
            if compare_folders(folder, destination_path):
                for file in os.listdir(folder):
                    file_path = os.path.join(folder, file)
                    shutil.move(file_path, destination_path)
        else:
            shutil.move(folder, destination_path)

#GUI

class ImageMoveGUI(tk.Tk):
    def __init__(self):
        super().__init__()


        self.title("Image Move GUI")
        self.style = ttk.Style()
        self.style.configure("TNotebook", background="red")
        self.style.theme_use("clam")  # Use the system color scheme
        


        self.notebook = ttk.Notebook(self)
        self.movies_tab = ttk.Frame(self.notebook)
        self.tv_series_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.movies_tab, text="Movies")
        self.notebook.add(self.tv_series_tab, text="TV Series")
        self.notebook.pack(fill="both", expand=True)

        self.source_folder_movies = source_folder_original  # Replace with your source folder for movies.
        self.source_folder_tv_series = "path_to_tv_series"  # Replace with your source folder for TV series.

        self.movies_label = tk.Label(self.movies_tab, text="Movies Source Folder:")
        self.movies_label.pack(pady=5)
        self.movies_source_var = tk.StringVar(value=self.source_folder_movies)
        self.movies_source_label = tk.Label(self.movies_tab, textvariable=self.movies_source_var)
        self.movies_source_label.pack()
        self.movies_change_button = tk.Button(self.movies_tab, text="Change Source Folder", command=self.change_movies_source)
        self.movies_change_button.pack(pady=5)

        self.tv_series_label = tk.Label(self.tv_series_tab, text="TV Series Source Folder:")
        self.tv_series_label.pack(pady=5)
        self.tv_series_source_var = tk.StringVar(value=self.source_folder_tv_series)
        self.tv_series_source_label = tk.Label(self.tv_series_tab, textvariable=self.tv_series_source_var)
        self.tv_series_source_label.pack()
        self.tv_series_change_button = tk.Button(self.tv_series_tab, text="Change Source Folder", command=self.change_tv_series_source)
        self.tv_series_change_button.pack(pady=5)

        self.subfolders_with_images = find_subfolders_with_images(source_folder_original)

        self.listbox = tk.Listbox(self.movies_tab)
        for folder in self.subfolders_with_images:
            folder_name = os.path.basename(folder)  # Extract the folder name
            self.listbox.insert(tk.END, folder_name)  # Insert the folder name in the listbox


        self.move_button = tk.Button(self.movies_tab, text="Move Random Folders Now", command=self.move_folders)

        self.listbox.pack(padx=10, pady=10)
        self.move_button.pack(padx=10, pady=5)

    def change_movies_source(self):
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            self.source_folder_movies = new_source_folder
            self.movies_source_var.set(new_source_folder)

    def change_tv_series_source(self):
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            self.source_folder_tv_series = new_source_folder
            self.tv_series_source_var.set(new_source_folder)

    def move_folders(self):
        move_random_folders_to_target(self.source_folder_movies, "target")  # Replace "target" with your target folder.
        messagebox.showinfo("Move Complete", "Random folders moved!")


if __name__ == "__main__":
    app = ImageMoveGUI()
    app.mainloop()
