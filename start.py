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
from crontab import CronTab
import sys

print("Start")


# Determine the script's location
script_location = os.path.abspath(__file__)
script_folder = os.path.dirname(os.path.abspath(__file__))
print("Script location ", script_location)
id = 1  # Library number
arg1 = "moviemover"  # String to identify in the crontab table


def main():  # If the script started with argument, this function will run
    print("main")
    cron = CronTab(user=True)
    config = configparser.ConfigParser()

    # Check if the config file exists
    if os.path.exists(str(script_folder + "/config.ini")):
        config.read(str(script_folder + "/config.ini"))

        print("searcjhhh ", str("library " + str(id) + "source folder"))
        source_folder_movies = config["Paths"][
            str("library_" + str(id) + "_source_folder")
        ]
        target_folder_movies = config["Paths"][
            str("library_" + str(id) + "_target_folder")
        ]
        percentage = config["Settings"][str("library_" + str(id) + "_percentage")]

        print("source_folder ", source_folder_movies)
        print("target_folder ", target_folder_movies)
        print("percentage ", percentage)
        app.move_folders()
    else:
        print("Config file is not available at ./config.ini")


def write_to_document(custom_line):  # Logging
    with open(str(script_folder + "/Log.txt"), "a") as file:
        file.write(custom_line + "\n")
    limit_log_lines(str(script_folder + "/Log.txt"), max_lines=1000)


def limit_log_lines(log_file_path, max_lines):  # limit the size of the log file
    lines = []
    with open(log_file_path, "r") as file:
        lines = file.readlines()
    if len(lines) > max_lines:
        with open(log_file_path, "w") as file:
            file.writelines(lines[-max_lines:])


def is_script_already_added(cron, arg1):
    write_to_document("is_script_already_added")
    ide = str(id) + " " + arg1
    print("search for ", ide)
    for job in cron:
        print("Script keresese: ", job.comment)
        if ide in job.comment:
            print("Script megtalalva")
            return True
    return False


def create_crontab_entry(script_location, crontab_expression, cron, edit_mode=False):
    write_to_document("create_crontab_entry")
    print("create_crontab_entry()")
    print("script_location ", script_location)
    print("crontab_expression ", crontab_expression)
    print("id ", id)
    crontab_entry = f"{crontab_expression} /usr/bin/env python3 {script_location}"

    with os.popen("crontab -l") as crontab_file:
        existing_crontab = crontab_file.read()
    # Split the existing crontab into lines
    lines = existing_crontab.strip().split("\n")

    if edit_mode:
        # Remove the old crontab entry, if exists
        lines = [line for line in lines if arg1 not in line]

    # Append the new crontab entry
    lines.append(crontab_entry + " " + str(id) + " #" + str(id) + " " + arg1 + "\n")

    # Join the lines and write back to crontab
    new_crontab = "\n".join(lines)

    with os.popen("crontab", "w") as crontab_file:
        crontab_file.write(new_crontab)


def find_subfolders_with_images(folder_path, image_extensions=("jpg", "jpeg", "bmp")):
    write_to_document("find_subfolders_with_images")
    subfolders_with_images = []

    for root, dirs, files in os.walk(folder_path):
        # Calculate the depth of the current subfolder from the starting folder
        if root == folder_path:
            continue
        current_depth = root[len(folder_path) :].count(os.sep)

        # Check if the current depth is greater than 1 (deeper than one subfolder)
        if current_depth > 1:
            continue

        image_files = [
            file
            for file in files
            if os.path.splitext(file)[1].lower().lstrip(".") in image_extensions
        ]
        if image_files:
            subfolders_with_images.append(root)

    return subfolders_with_images


def compare_folders(source_folder, destination_folder):
    write_to_document("compare_folders")
    source_files = set(os.listdir(source_folder))
    destination_files = set(os.listdir(destination_folder))

    return not source_files.intersection(destination_files)


def move_folders_to_target(source_folder, target_folder, selected_folders):
    write_to_document("move_folders_to_target")

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


class PopupWindow:
    def __init__(self, parent, title, percentage):
        write_to_document("__init__Popup")
        self.config = configparser.ConfigParser()

        # Check if the config file exists
        if os.path.exists(str(script_folder + "/config.ini")):
            self.config.read(str(script_folder + "/config.ini"))
        else:
            self._create_default_config()
        self.config.read(str(script_folder + "/config.ini"))

        self.percentage = percentage
        self.parent = parent
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        # self.popup.title("Popup Window")

    def crontab_popup(self):
        write_to_document("crontab_popup")
        # Add contents and layout for the popup window here
        self.crontab_value = tk.StringVar()

        self.label = tk.Label(self.popup, text="Custom crontab time code:")
        self.label.pack()

        self.crontab_entry = tk.Entry(self.popup, textvariable=self.crontab_value)
        self.crontab_entry.pack()

        example_label = tk.Label(self.popup, text="Example crontab codes:")
        example_label.pack()

        self.example1_label = tk.Label(
            self.popup, text="Every Friday at 20:00: 0 20 * * 5"
        )
        self.example1_label.pack()

        self.example2_label = tk.Label(
            self.popup, text="Every Wednesday and Saturday at 06:00: 0 6 * * 3,6"
        )
        self.example2_label.pack()

        self.information_label = tk.Label(
            self.popup,
            text="On linux you can see your crontab entries with: crontab -l",
        )
        self.information_label.pack()

        ok_button = tk.Button(
            self.popup, text="OK", command=self.validate_and_save_crontab
        )
        ok_button.pack()

    def percentage_popup(self):
        write_to_document("percentage_popup")
        self.percentage_value = tk.StringVar()
        self.example1_label = tk.Label(
            self.popup, text="Set the percentage of folders that will be moved"
        )
        self.example1_label.pack()
        self.perc_entry = tk.Entry(self.popup, textvariable=self.percentage_value)
        self.perc_entry.pack()
        ok_button = tk.Button(self.popup, text="OK", command=self.save_percentage)
        ok_button.pack()

    def save_percentage(self):
        write_to_document("save_percentage")
        new_percentage = self.percentage_value.get()
        if new_percentage.isdigit() and 1 <= int(new_percentage) <= 100:
            print("new percentage ", new_percentage)
            self.parent.percentage = (
                new_percentage  # Update the shared percentage value
            )
            self.parent.percentage_value = (
                new_percentage  # Update the shared percentage value
            )

            # percentage = new_percentage
            self.config["Settings"][
                str("library_" + str(id) + "_percentage")
            ] = new_percentage
            with open(str(script_folder + "/config.ini"), "w") as configfile:
                self.config.write(configfile)
            self.popup.destroy()
            app.refresh_perc()
        else:
            messagebox.showerror(
                "Validation Error", f"The value should be between 1 and 100"
            )

    def validate_and_save_crontab(self):
        write_to_document("validate_and_save_crontab")
        crontab_expression = self.crontab_value.get()
        print("Okés22")
        ## Using the current user
        try:
            print("try1")
            cron = CronTab(user=True)
            print("try2")
            if len(crontab_expression) == 0:
                print("len")
                messagebox.showerror("Validation Error", "Invalid crontab expression.")
            else:
                print("else")
                self.parent.crontab_value = crontab_expression
                self.popup.destroy()
                print("script_location ", script_location)
                print("crontab_expression ", crontab_expression)
                if is_script_already_added(cron, arg1):
                    create_crontab_entry(
                        script_location, crontab_expression, cron, True
                    )
                else:
                    create_crontab_entry(script_location, crontab_expression, cron)

        except Exception as e:
            print("Exception")
            messagebox.showerror("Validation Error", f"Error: {str(e)}")
        # 0 20 * * 5


# GUI
class ImageMoveGUI(tk.Tk):
    def __init__(self):
        write_to_document("__init__ IMAGEGUI")
        super().__init__()
        self.config = configparser.ConfigParser()

        # Check if the config file exists
        if os.path.exists(str(script_folder + "/config.ini")):
            self.config.read(str(script_folder + "/config.ini"))
        else:
            self._create_default_config()
        self.config.read(str(script_folder + "/config.ini"))

        self.source_folder_movies = self.config["Paths"][
            str("library_" + str(id) + "_source_folder")
        ]
        self.target_folder_movies = self.config["Paths"][
            str("library_" + str(id) + "_target_folder")
        ]
        self.percentage = self.config["Settings"][
            str("library_" + str(id) + "_percentage")
        ]

        print("source_folder ", self.source_folder_movies)
        print("target_folder ", self.target_folder_movies)
        print("percentage ", self.percentage)

        self.title("Image Move GUI")
        self.style = ttk.Style()
        self.style.configure("TNotebook", background="red")
        self.style.theme_use("clam")  # Use the system color scheme

        self.notebook = ttk.Notebook(self)
        self.movies_tab = ttk.Frame(self.notebook)
        self.tv_series_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.movies_tab, text="Library 1")
        self.notebook.add(self.tv_series_tab, text="Create New Library")
        self.notebook.pack(fill="both", expand=True)

        # self.source_folder_movies = source_folder  # Replace with your source folder for movies.
        self.source_folder_tv_series = (
            "path_to_tv_series"  # Replace with your source folder for TV series.
        )

        # Source folder section
        self.movies_label = tk.Label(self.movies_tab, text="Source Folder (copy from)")
        self.movies_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.movies_source_var = tk.StringVar(value=self.source_folder_movies)
        self.movies_change_button = tk.Button(
            self.movies_tab,
            text=self.source_folder_movies,
            command=self.change_movies_source,
        )
        self.movies_change_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Target folder section
        self.movies_target_label = tk.Label(
            self.movies_tab, text="Target Folder (copy to): "
        )
        self.movies_target_var = tk.StringVar(value=self.target_folder_movies)
        self.movies_target_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.movies_change_target_button = tk.Button(
            self.movies_tab,
            text=self.target_folder_movies,
            command=self.change_movies_target,
        )
        self.movies_change_target_button.grid(
            row=1, column=1, padx=10, pady=5, sticky="w"
        )

        self.tv_series_label = tk.Label(
            self.tv_series_tab, text="TV Series Source Folder:"
        )
        self.tv_series_label.pack(pady=5)

        self.tv_series_source_var = tk.StringVar(value=self.source_folder_tv_series)
        self.tv_series_source_label = tk.Label(
            self.tv_series_tab, textvariable=self.tv_series_source_var
        )
        self.tv_series_source_label.pack()

        self.tv_series_change_button = tk.Button(
            self.tv_series_tab,
            text="Change Source Folder",
            command=self.change_tv_series_source,
        )
        self.tv_series_change_button.pack(pady=5)

        # Listbox and move button
        self.subfolders_with_images = find_subfolders_with_images(
            self.source_folder_movies
        )

        self.listbox = tk.Listbox(self.movies_tab, selectmode=tk.MULTIPLE)
        self.refresh_folder_list()  # Call the function to populate the listbox
        self.listbox.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")

        self.refresh_button = tk.Button(
            self.movies_tab, text="Refresh", command=self.refresh_folder_list
        )
        self.refresh_button.grid(
            row=3, column=0, columnspan=3, padx=10, pady=5, sticky="w"
        )

        self.move_selected_button = tk.Button(
            self.movies_tab,
            text="Move Selected Folders",
            command=self.move_selected_folders,
        )
        self.move_selected_button.grid(
            row=4, column=0, columnspan=3, padx=10, pady=5, sticky="w"
        )

        self.move_button = tk.Button(
            self.movies_tab, text="Move Random Folders Now", command=self.move_folders
        )
        self.move_button.grid(
            row=5, column=0, columnspan=3, padx=10, pady=5, sticky="w"
        )

        self.percentage_button = tk.Button(
            self.movies_tab,
            text=str("Move " + self.percentage + "%"),
            command=self.open_percentage_popup,
        )
        self.percentage_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.ido_button = tk.Button(
            self.movies_tab, text="Crontab Schedule", command=self.open_crontab_popup
        )
        self.ido_button.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        self.crontab_value = None

    def move_selected_folders(self):
        selected_indices = self.listbox.curselection()  # Get indices of selected items
        selected_folders = [
            self.subfolders_with_images[idx] for idx in selected_indices
        ]
        move_folders_to_target(
            self.source_folder_movies, self.target_folder_movies, selected_folders
        )

        # for folder in selected_folders:
        #     print("Moving:", folder)

    def move_folders(self):
        write_to_document("move_folders")
        print("move_folders percentage ", self.percentage)

        subfolders_with_images = find_subfolders_with_images(self.source_folder_movies)
        num_folders_to_move = math.ceil(
            len(subfolders_with_images) * int(self.percentage) / 100
        )
        print("all folders: ", len(subfolders_with_images))
        print("percentage: ", int(self.percentage))
        selected_folders = random.sample(subfolders_with_images, num_folders_to_move)
        print("chosen folders: ", selected_folders)
        move_folders_to_target(
            self.source_folder_movies, self.target_folder_movies, selected_folders
        )

    def open_crontab_popup(self):
        write_to_document("open_crontab_popup")
        crontab_popup = PopupWindow(
            self, "Edit/Add crontab schedule", self.percentage
        )  # Create an instance of PopupWindow
        crontab_popup.crontab_popup()

    def open_percentage_popup(self):
        write_to_document("open_percentage_popup")
        percentage_popup = PopupWindow(
            self, "Modify the percentage", self.percentage
        )  # Create an instance of PopupWindow
        percentage_popup.percentage_popup()

    def refresh_folder_list(self):
        write_to_document("refresh_folder_list")
        self.subfolders_with_images = find_subfolders_with_images(
            self.source_folder_movies
        )
        self.listbox.delete(0, tk.END)  # Clear the listbox

        for folder in self.subfolders_with_images:
            folder_name = os.path.basename(folder)
            self.listbox.insert(tk.END, folder_name)

    def refresh_perc(self):
        write_to_document("refresh_perc")
        self.percentage_button.config(
            text=str("Move " + self.percentage + "%")
        )  # Update the percentage button text

    def change_movies_source(self):
        write_to_document("change_movies_source")
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            self.source_folder_movies = new_source_folder
            self.config["Paths"][
                str("library_" + str(id) + "_source_folder")
            ] = new_source_folder
            self.movies_source_var.set(new_source_folder)
            with open(str(script_folder + "/config.ini"), "w") as configfile:
                self.config.write(configfile)
            self.movies_change_button.config(text=new_source_folder)
            self.refresh_folder_list()  # Call the refresh function after changing the source folder

    def change_movies_target(self):
        write_to_document("change_movies_target")
        new_target_folder = tk.filedialog.askdirectory()
        if new_target_folder:
            self.target_folder_movies = new_target_folder
            self.config["Paths"][
                str("library_" + str(id) + "_target_folder")
            ] = new_target_folder
            self.movies_target_var.set(new_target_folder)
            with open(str(script_folder + "/config.ini"), "w") as configfile:
                self.config.write(configfile)
            self.movies_change_target_button.config(text=new_target_folder)

    def change_tv_series_source(self):
        write_to_document("change_tv_series_source")
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            self.source_folder_tv_series = new_source_folder
            self.config["Paths"][
                "tv_source_folder"
            ] = new_source_folder  # Replace this part
            self.tv_series_source_var.set(new_source_folder)

    def _create_default_config(self):
        write_to_document("_create_default_config")
        config = configparser.ConfigParser()
        config["Paths"] = {
            "library_1_source_folder": "/path/to/source/folder",
            "library_1_target_folder": "/path/to/target/folder",
        }
        config["Settings"] = {"library_1_percentage": 30}
        with open(str(script_folder + "/config.ini"), "w") as configfile:
            config.write(configfile)


def check_argument():
    write_to_document("check_argument")
    if len(sys.argv) > 1:
        argument = sys.argv[1]
        print(f"Script started with argument: {argument}")
        try:
            if int(argument) > 0:  # Check if the argument is valid
                print("Start moving the library", argument)
                id = argument
                main()
        except:  # is not valid
            print("Argument should be the ID number of the library")
    else:
        print(
            "Script started without any arguments. It should have started with: script librarynumber"
        )


if __name__ == "__main__":
    check_argument()
    app = ImageMoveGUI()
    app.mainloop()

    if app.crontab_value is not None:
        print("Valid crontab expression:", app.crontab_value)
