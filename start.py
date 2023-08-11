#!/usr/bin/env python3
import os
import math
import random
import shutil
import tkinter as tk
from tkinter import messagebox
from tkinter import Listbox, Button
from tkinter import ttk
import configparser
import tkinter.filedialog
#source_folder_original = "~/Downloads/sssssssssssssss"
#target_folder_original = "~/Downloads/target"
# Load configuration from config.ini
print("Start")
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
        if os.path.exists(target_folder) and os.access(target_folder, os.W_OK):
            if os.path.exists(destination_path):
                if compare_folders(folder, destination_path):
                    for file in os.listdir(folder):
                        file_path = os.path.join(folder, file)
                        shutil.move(file_path, destination_path)
            else:
                shutil.move(folder, destination_path)
        else:
            print("Target folder does not exist or doesn't have write permissions.")

    app.refresh_folder_list()  # Call the refresh function after changing the source folder

#GUI

class ImageMoveGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config = configparser.ConfigParser()

        # Check if the config file exists
        if os.path.exists('./config.ini'):
            self.config.read('./config.ini')
        else:
            self._create_default_config()
        self.config.read('./config.ini')
        
        self.source_folder_movies = self.config['Paths']['movies_source_folder']
        self.target_folder_movies = self.config['Paths']['movies_target_folder']

        print("source_folder ", self.source_folder_movies)
        print("target_folder ", self.target_folder_movies)


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

        #self.source_folder_movies = source_folder  # Replace with your source folder for movies.
        self.source_folder_tv_series = "path_to_tv_series"  # Replace with your source folder for TV series.

        # Source folder section
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

        # Target folder section
        self.movies_target_label = tk.Label(self.movies_tab, text="Movies Target Folder:")
        self.movies_target_label.pack(pady=5)
        self.movies_target_var = tk.StringVar(value=self.target_folder_movies)
        self.movies_target_label = tk.Label(self.movies_tab, textvariable=self.movies_target_var)
        self.movies_target_label.pack()
        self.movies_change_target_button = tk.Button(self.movies_tab, text="Change Target Folder", command=self.change_movies_target)
        self.movies_change_target_button.pack(pady=5)


        # Listbox and move button
        self.subfolders_with_images = find_subfolders_with_images(self.source_folder_movies)

        self.listbox = tk.Listbox(self.movies_tab)
        self.refresh_folder_list()  # Call the function to populate the listbox


        self.move_button = tk.Button(self.movies_tab, text="Move Random Folders Now", command=self.move_folders)

        self.listbox.pack(padx=10, pady=10)
        self.move_button.pack(padx=10, pady=5)

    def refresh_folder_list(self):
        self.subfolders_with_images = find_subfolders_with_images(self.source_folder_movies)
        self.listbox.delete(0, tk.END)  # Clear the listbox

        for folder in self.subfolders_with_images:
            folder_name = os.path.basename(folder)
            self.listbox.insert(tk.END, folder_name)

    def change_movies_source(self):
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            self.source_folder_movies = new_source_folder
            self.config['Paths']['movies_source_folder'] = new_source_folder
            self.movies_source_var.set(new_source_folder)
            with open('./config.ini', 'w') as configfile:
                self.config.write(configfile)
            self.refresh_folder_list()  # Call the refresh function after changing the source folder
    def change_movies_target(self):
        new_target_folder = tk.filedialog.askdirectory()
        if new_target_folder:
            self.target_folder_movies = new_target_folder
            self.config['Paths']['movies_target_folder'] = new_target_folder
            self.movies_target_var.set(new_target_folder)
            with open('./config.ini', 'w') as configfile:
                self.config.write(configfile)

    def change_tv_series_source(self):
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            self.source_folder_tv_series = new_source_folder
            self.config['Paths']['tv_source_folder'] = new_source_folder    # Replace this part
            self.tv_series_source_var.set(new_source_folder)

    def move_folders(self):
        move_random_folders_to_target(self.source_folder_movies, self.target_folder_movies) 
        #messagebox.showinfo("Move Complete", "Random folders moved!")

    def _create_default_config(self):
        config = configparser.ConfigParser()
        config['Paths'] = {
            'movies_source_folder': '/path/to/source/folder',
            'movies_target_folder': '/path/to/target/folder'
        }
        with open('./config.ini', 'w') as configfile:
            config.write(configfile)
if __name__ == "__main__":
    app = ImageMoveGUI()
    app.mainloop()
    # Later in your code, you want to refresh the folder list:
    # def some_function():
    #     # Call the refresh_folder_list function from the ImageMoveGUI instance
    #     app.refresh_folder_list()
    # # Call the function to refresh the folder list
    # some_function()
