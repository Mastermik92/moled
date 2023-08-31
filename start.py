#!/usr/bin/env python3
import os
import math
import random
import shutil
from tkinter import simpledialog
import tkinter as tk
from tkinter import messagebox
from tkinter import Listbox, Button

from tkinter import ttk
import configparser
import tkinter.filedialog
from crontab import CronTab
import sys
import datetime

# Determine the script's location
script_location = os.path.abspath(__file__)
script_folder = os.path.dirname(os.path.abspath(__file__))
print("Script location ", script_location)
id = 1  # Library number
arg1 = "moviemover"  # String to identify in the crontab table
percentage = 30
source_folder = "path/to/source"
target_folder = "path/to/target"
num_folders_to_move = 0
library_name = "Library_1"
a = 1  # If the config is generated in this session, do not create a +1 tab, because with the generation a tab is already added.
deljob = 0  # This will contain the job chosen from the crontab entries, which will be deleted


def main():  # If the script started with argument, this function will run
    # Without GUI
    print("main")
    write_to_document("main")
    # cron = CronTab(user=True)
    config = configparser.ConfigParser()

    # Check if the config file exists
    if os.path.exists(str(script_folder + "/config.ini")):
        config.read(str(script_folder + "/config.ini"))
        global percentage, source_folder, target_folder, library_name

        print("searcjhhh ", str("library " + str(id) + "source folder"))
        source_folder = config["Paths"][str("source_folder_library_" + str(id))]
        target_folder = config["Paths"][str("target_folder_library_" + str(id))]
        percentage = config["Settings"][str("percentage_library_" + str(id))]
        #    self.parent.percentage = percentage
        print("source_folder ", source_folder)
        print("target_folder ", target_folder)
        print("percentage ", percentage)
        move_folders()
    else:
        write_to_document("Supposed to run, but did not find the config file")
        print("Config file is not available at ./config.ini")


def write_to_document(custom_line):  # Logging
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
    with open(str(script_folder + "/Log.txt"), "a") as file:
        file.write(
            str(
                "Library "
                + str(id)
                + " "
                + formatted_datetime
                + " "
                + custom_line
                + "\n"
            )
        )
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
            deljob = job
            print("deljob", deljob)
            return True
    return False


def create_crontab_entry(i, crontab_expression, cron, edit_mode=False):
    write_to_document("create_crontab_entry")
    print("create_crontab_entry()")
    print("script_location ", script_location)
    print("crontab_expression ", crontab_expression)
    print("id ", i)
    crontab_entry = f"{crontab_expression} /usr/bin/env python3 {script_location}"

    with os.popen("crontab -l") as crontab_file:
        existing_crontab = crontab_file.read()
    # Split the existing crontab into lines
    lines = existing_crontab.strip().split("\n")

    if edit_mode:
        # Remove the old crontab entry, if exists
        lines = [line for line in lines if arg1 not in line]

    # Append the new crontab entry
    lines.append(crontab_entry + " " + str(i) + " #" + str(i) + " " + arg1 + "\n")

    # Join the lines and write back to crontab
    new_crontab = "\n".join(lines)

    with os.popen("crontab", "w") as crontab_file:
        crontab_file.write(new_crontab)


def find_subfolders_with_images(folder_path, image_extensions=("jpg", "jpeg", "bmp")):
    print("find_subfolders_with_images ", folder_path)
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
    print("find_subfolders_with_images vege ", subfolders_with_images)
    return subfolders_with_images


def compare_folders(source_folder, destination_folder):
    write_to_document("compare_folders")
    source_files = set(os.listdir(source_folder))
    destination_files = set(os.listdir(destination_folder))

    return not source_files.intersection(destination_files)


def move_folders():
    write_to_document("move_folders")
    print("move_folders percentage ", percentage)

    subfolders_with_images = find_subfolders_with_images(source_folder)
    num_folders_to_move = math.ceil(len(subfolders_with_images) * int(percentage) / 100)
    print("all folders: ", len(subfolders_with_images))
    print("percentage: ", int(percentage))
    selected_folders = random.sample(subfolders_with_images, num_folders_to_move)
    print("chosen folders: ", selected_folders)
    move_folders_to_target(source_folder, target_folder, selected_folders)


def move_folders_to_target(source_folder, target_folder, selected_folders):
    write_to_document("move_folders_to_target")
    write_to_document(str("Source: " + source_folder))
    write_to_document(str("Target: " + target_folder))
    write_to_document(str("Chosen folders: " + str(selected_folders)))

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
                write_to_document("Folders Moved")
        else:
            print("Target folder does not exist or doesn't have write permissions.")
            write_to_document(
                "Target folder does not exist or doesn't have write permissions."
            )
    app.refresh_folder_list()  # Call the refresh function after changing the source folder
    app.update_percentage(percentage)


class PopupWindow:
    def __init__(self, parent, title, percentage_n):
        write_to_document("__init__Popup")
        self.config = configparser.ConfigParser()
        global percentage
        self.config.read(str(script_folder + "/config.ini"))

        self.percentage = percentage = percentage_n
        self.parent = parent
        self.popup = tk.Toplevel(parent)
        self.popup.title(title)
        # self.popup.title("Popup Window")

    def crontab_popup(self):
        write_to_document("crontab_popup")
        # Add contents and layout for the popup window here
        self.crontab_value = tk.StringVar()
        self.config = configparser.ConfigParser()
        self.config.read(str(script_folder + "/config.ini"))

        self.label = tk.Label(self.popup, text="Custom crontab time code:")
        self.label.pack()

        # Check if the key exists in the config file and set the value
        if str("schedule_library_" + str(id)) in self.config["Settings"]:
            self.crontab_value.set(
                self.config["Settings"][str("schedule_library_" + str(id))]
            )
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

        del_button = tk.Button(
            self.popup, text="Delete saved entry", command=self.delete_saved_crontab
        )
        del_button.pack(side=tk.LEFT, padx=10, pady=5)

        ok_button = tk.Button(
            self.popup, text="Save", command=self.validate_and_save_crontab
        )
        ok_button.pack(side=tk.RIGHT, padx=10, pady=5)

    def delete_saved_crontab(self):
        print("Delete crontab entry")
        # Check if the key exists in the config file and remove it if it does
        if str("schedule_library_" + str(id)) in self.config["Settings"]:
            del self.config["Settings"][str("schedule_library_" + str(id))]
            with open(str(script_folder + "/config.ini"), "w") as configfile:
                self.config.write(configfile)
        # If it is in the crontab, then delete it from there
        cron = CronTab(user=True)
        if is_script_already_added(cron, arg1):
            ide = str(id) + " " + arg1
            cron.remove(cron.find_comment(ide))
            cron.write()  # Save changes to the crontab

        self.crontab_value.set("")  # Clear the crontab_entry textbox

    def validate_and_save_crontab(self):
        write_to_document("validate_and_save_crontab")
        crontab_expression = self.crontab_value.get()
        self.config = configparser.ConfigParser()
        print("validate_and_save_crontab")
        ## Using the current user
        try:
            cron = CronTab(user=True)
            if len(crontab_expression) == 0:
                print("len")
                messagebox.showerror(
                    "Validation Error", "Crontab entry did not get updated"
                )
            else:
                print("else")
                self.parent.crontab_value = crontab_expression
                self.popup.destroy()
                print("script_location ", script_location)
                print("crontab_expression ", crontab_expression)
                if is_script_already_added(cron, arg1):
                    create_crontab_entry(id, crontab_expression, cron, True)
                    print("create_crontab_entry, script_already_added")
                else:
                    create_crontab_entry(id, crontab_expression, cron)
                    print("create_crontab_entry")
                # Save to the config
                if os.path.exists(str(script_folder + "/config.ini")):
                    self.config.read(str(script_folder + "/config.ini"))
                self.config["Settings"][
                    str("schedule_library_" + str(id))
                ] = crontab_expression
                with open(str(script_folder + "/config.ini"), "w") as configfile:
                    self.config.write(configfile)

        except Exception as e:
            print("Exception")
            messagebox.showerror("Validation Error", f"Error: {str(e)}")


# GUI
class ImageMoveGUI(tk.Tk):
    def __init__(self):
        write_to_document("__init__ IMAGEGUI")
        super().__init__()
        print("__init__ IMAGEGUI")

        self.config = configparser.ConfigParser()
        # self.tab = "Library 1"
        global percentage, source_folder, target_folder, id

        self.title("Image Move GUI")
        self.style = ttk.Style()
        self.style.configure("TNotebook", background="red")
        self.style.theme_use("clam")  # Use the system color scheme
        self.notebook = ttk.Notebook(self)
        self.new_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.new_tab, text="Create New Library")
        self.notebook.pack(fill="both", expand=True)

        # Check if the config file exists
        if os.path.exists(str(script_folder + "/config.ini")):
            self.config.read(str(script_folder + "/config.ini"))
        else:
            self.create_config()
        self.tab = str("library" + str(id) + "_tab")
        self.tab_name = self.config["Settings"][str("name_library_" + str(id))]

        # Create new library button
        self.new_tab_button = ttk.Button(
            self.new_tab,
            text="Create new library with default settings",
            command=self.create_config,
            # Logic to get the next available id number, create entries in the config, then create library
        )
        self.new_tab_button.pack()

        self.library_count()

        # Dictionary to store buttons with library names as keys
        self.library_buttons = {}

        # Create library tabs based on the count
        for i in range(1, library_count + a):
            self.create_library_tab(i)

        # Bind the tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.update_id)
        # update_id
        self.tab = str("library" + str(id) + "_tab")
        print("3self.tab ", self.tab)

        self.load_library_settings(id)
        new_tab_index = id - 1  # Change this index to the desired tab
        self.notebook.select(new_tab_index)  # Active tab
        self.refresh_folder_list()
        print("init vege")

    def library_count(self):
        # Count the number of library sections
        global library_count
        library_size = 0
        for key in self.config["Settings"]:
            if key.startswith("percentage"):
                library_size += 1
        library_count = library_size
        print("Library count", library_size)
        print("self.config.sections()", self.config.sections())

    def load_library_settings(self, i):
        print("load_library_settings", i)
        self.library_count()
        if library_count + 1 == i:
            print("We are on the Create new library tab")
        else:
            self.config = configparser.ConfigParser()
            if os.path.exists(str(script_folder + "/config.ini")):
                self.config.read(str(script_folder + "/config.ini"))
            global percentage, source_folder, target_folder

            self.source_folder = source_folder = self.config["Paths"][
                str("source_folder_library_" + str(i))
            ]
            self.target_folder = target_folder = self.config["Paths"][
                str("target_folder_library_" + str(i))
            ]
            self.percentage = percentage = self.config["Settings"][
                str("percentage_library_" + str(i))
            ]
            self.tab_name = self.config["Settings"][str("name_library_" + str(i))]

        print("tab ", i, "source_folder ", self.source_folder)
        print("tab ", i, "target_folder ", self.target_folder)
        print("tab ", i, "percentage ", self.percentage)
        # print("tab ", i, "name ", self.tab)
        print("Load library settings vege")
        # self.refresh_folder_list()  # Call the refresh function after changing the source folder
        self.refresh_folder_list()

    def create_library_tab(self, i):
        print("create_library_tab ", i)
        print("library_count ", self.library_count)
        # print("create_library_tab ", i)
        self.config = configparser.ConfigParser()
        library_section = f"library_{i}"
        self.config.read(str(script_folder + "/config.ini"))
        self.tab = str("library" + str(i) + "_tab")
        self.load_library_settings(i)
        library_name = self.config["Settings"][str("name_library_" + str(i))]
        # Create a new tab for the library
        library_tab = ttk.Frame(self.notebook)
        self.notebook.insert(
            len(self.notebook.tabs()) - 1,
            library_tab,
            text=library_name,  # text=f"Library {i}"
        )

        # Source folder section
        source_frame = ttk.Frame(library_tab)
        source_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.movies_label = tk.Label(source_frame, text="Source Folder (copy from):")
        self.movies_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.movies_source_var = tk.StringVar(value=source_folder)
        self.movies_change_button = tk.Button(
            source_frame,
            text=source_folder,
            command=self.change_movies_source,
        )
        self.movies_change_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        source_frame.config(borderwidth=2, relief="solid")
        # Target folder section
        target_frame = ttk.Frame(library_tab)
        target_frame.grid(row=0, column=1, columnspan=2, padx=10, pady=10, sticky="w")
        self.movies_target_label = tk.Label(
            target_frame, text="Target Folder (copy to): "
        )
        self.movies_target_var = tk.StringVar(value=target_folder)
        self.movies_target_label.grid(
            row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w"
        )
        self.movies_change_target_button = tk.Button(
            target_frame,
            text=target_folder,
            command=self.change_movies_target,
        )
        self.movies_change_target_button.grid(
            row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w"
        )
        target_frame.config(borderwidth=2, relief="solid")
        # List
        listbox_frame = ttk.Frame(library_tab)
        listbox_frame.grid(
            row=1, column=0, columnspan=3, rowspan=6, padx=10, pady=10, sticky="w"
        )
        # Listbox and move button
        self.subfolders_with_images = find_subfolders_with_images(source_folder)

        self.listbox = tk.Listbox(listbox_frame, selectmode=tk.MULTIPLE)
        self.listbox.grid(
            row=1, column=0, columnspan=3, rowspan=4, padx=10, pady=10, sticky="w"
        )

        self.refresh_button = tk.Button(
            listbox_frame, text="Refresh", command=self.refresh_folder_list
        )
        self.refresh_button.grid(
            row=5, column=0, columnspan=3, padx=10, pady=5, sticky="w"
        )
        listbox_frame.config(borderwidth=2, relief="solid")

        self.move_selected_button = tk.Button(
            library_tab,
            text="Move Selected Folders",
            command=self.move_selected_folders,
        )
        self.move_selected_button.grid(
            row=7, column=0, columnspan=3, padx=10, pady=5, sticky="w"
        )

        # Create a frame to hold the percentage elements
        percentage_frame = ttk.Frame(library_tab)
        percentage_frame.grid(
            row=1, column=1, columnspan=2, padx=10, pady=5, sticky="w"
        )

        self.percentage_label = tk.Label(
            percentage_frame,
            text=str(str(percentage) + "%" + " of the found folders will be moved:"),
        )
        self.percentage_label.grid(
            row=0, column=0, columnspan=2, padx=10, pady=5, sticky="w"
        )
        # Create a slider for percentage
        self.percentage_slider = tk.Scale(
            percentage_frame,
            from_=1,
            to=100,
            orient="horizontal",
            showvalue=True,
            command=self.update_percentage,
        )
        self.percentage_slider.set(percentage)  # Set initial value
        self.percentage_slider.grid(
            row=1, column=0, columnspan=2, padx=10, pady=5, sticky="w"
        )
        percentage_frame.config(borderwidth=2, relief="solid")

        self.ido_button = tk.Button(
            library_tab, text="Crontab Schedule", command=self.open_crontab_popup
        )
        self.ido_button.grid(row=2, column=2, padx=10, pady=5, sticky="e")

        self.crontab_value = None

        self.log_button = tk.Button(
            library_tab, text="View Log Entries", command=self.open_log_popup
        )
        self.log_button.grid(row=3, column=2, padx=10, pady=5, sticky="e")

        self.rename_library_button = tk.Button(
            library_tab,
            text="Rename Library",
            command=self.rename_library,
        )
        self.rename_library_button.grid(row=5, column=1, padx=10, pady=5, sticky="e")

        self.delete_library_button = tk.Button(
            library_tab,
            text="Delete Libray",
            command=self.delete_library,
        )
        self.delete_library_button.grid(row=5, column=2, padx=10, pady=5, sticky="e")

        self.move_button = tk.Button(
            library_tab,
            text=str("Move Random (" + str(num_folders_to_move) + ") Folders Now"),
            command=move_folders,
        )
        self.move_button.grid(
            row=7, column=1, columnspan=2, padx=10, pady=5, sticky="e"
        )
        # self.library_buttons = {}
        self.library_buttons[self.tab] = {
            "movies_change_source_button": self.movies_change_button,
            "movies_change_target_button": self.movies_change_target_button,
            "log_button": self.log_button,
            "move_button": self.move_button,
            "percentage_label": self.percentage_label,
            "listbox": self.listbox,
            # "name": self.listbox,
        }
        print("self.tab ", self.tab)
        print("self.library_buttons ", self.library_buttons)

        print("Create library tab vege")
        self.refresh_folder_list()

    def rename_library(self):
        print("rename_library")
        # Get the current library id
        new_name = simpledialog.askstring("Rename Library", "Enter new library name:")
        if new_name:
            # Assuming you have the 'id' value defined
            key = f"name_library_{id}"
            self.config["Settings"][key] = new_name
            with open("config.ini", "w") as configfile:
                self.config.write(configfile)
            print(f"Renamed library {id} to {new_name}")

        self.notebook.tab(id - 1, text=new_name)

    def delete_library(self):
        print("delete library")
        self.library_count()
        cron = CronTab(user=True)
        # Get the current library id
        current_id = self.id

        # Iterate through keys and overwrite them
        for i in range(0, library_count - current_id + 1):
            print("iteration ", i)
            print("max ", library_count)
            new_id = current_id + i
            new_id_plus = new_id + 1
            print("new_id ", new_id)
            for key in self.config["Settings"]:
                if key.endswith(str("_" + str(new_id))):
                    if new_id < library_count:  # There are higher indexed keys
                        new_key_name = key.rsplit("_", 1)[0]
                        new_key = new_key_name + "_" + str(new_id_plus)
                        print(new_key)
                        print(new_key_name)
                        self.config["Settings"][key] = self.config["Settings"][new_key]
                    else:  # These the keys with highest index
                        # Remove the settings of the last library
                        self.config["Settings"].pop(key, None)
            for key2 in self.config["Paths"]:
                if key2.endswith(str("_" + str(new_id))):
                    if new_id < library_count:  # There are higher indexed keys
                        new_key_name = key2.rsplit("_", 1)[0]
                        new_key = new_key_name + "_" + str(new_id_plus)
                        print(new_key)
                        print(new_key_name)
                        self.config["Paths"][key2] = self.config["Paths"][new_key]
                    else:  # These the keys with highest index
                        # Remove the Path of the last library
                        self.config["Paths"].pop(key2, None)
            ide = str(new_id) + " " + arg1
            # ide_plus = str(new_id_plus) + " " + arg1
            if new_id < library_count:  # There are higher indexed keys
                for job in cron:
                    print("Script keresese: ", job.comment)
                    if ide in job.comment:  # There is schedule set for this library
                        crontab_expression = self.config["Settings"][
                            str("schedule_library_" + str(new_id_plus))
                        ]  # We get the schedule setting from the next library
                        create_crontab_entry(new_id, crontab_expression, cron, True)
            else:
                cron.remove(cron.find_comment(ide))
                cron.write()  # Save changes to the crontab

        # Update the config file
        with open(str(script_folder + "/config.ini"), "w") as configfile:
            self.config.write(configfile)

        # Close the current tab
        self.notebook.forget(self.notebook.select())
        self.id = current_id - 1
        self.notebook.select(self.id)  # Switch back to the first tab

        # Update GUI elements
        app.mainloop()
        self.library_count()

    def update_percentage(self, value):
        global percentage, num_folders_to_move
        write_to_document("update_percentage")
        new_percentage = value
        if new_percentage.isdigit() and 1 <= int(new_percentage) <= 100:
            if new_percentage != percentage:  # Changed
                print("new percentage ", new_percentage)
                self.percentage = (
                    percentage
                ) = new_percentage  # Update the shared percentage value
                # self.percentage_value = new_percentage  # Update the shared percentage value
                # percentage = new_percentage
                # percentage = new_percentage
                self.config["Settings"][
                    str("percentage_library_" + str(id))
                ] = new_percentage
                with open(str(script_folder + "/config.ini"), "w") as configfile:
                    self.config.write(configfile)
            # These will be updated even if just a tab changed, not the actual percentage:
            # Refresh Move button's label
            find_subfolders_with_images(source_folder)
            num_folders_to_move = math.ceil(
                len(self.subfolders_with_images) * int(percentage) / 100
            )
            print("num_folders_to_move ", num_folders_to_move)
            if self.tab in self.library_buttons:
                self.library_buttons[self.tab]["move_button"].config(
                    text=str(
                        "Move Random (" + str(num_folders_to_move) + ") Folders Now"
                    )
                )
            # Update percentage's label
            if self.tab in self.library_buttons:
                self.library_buttons[self.tab]["percentage_label"].config(
                    text=str(
                        str(percentage) + "%" + " of the found folders will be moved:"
                    )
                )
                print("Megtalalva")
            else:
                print("Nincs talalat")
                print("self.tab ", self.tab)
                print("self.library_buttons ", self.library_buttons)

        else:
            messagebox.showerror(
                "Validation Error", f"The value should be between 1 and 100"
            )

    def update_percentage_label(self, value):
        self.percentage_label.config(text=f"{value}%")

    def open_crontab_popup(self):
        write_to_document("open_crontab_popup")
        crontab_popup = PopupWindow(
            self, "Edit/Add crontab schedule", percentage
        )  # Create an instance of PopupWindow
        crontab_popup.crontab_popup()

    def refresh_folder_list(self):
        write_to_document("refresh_folder_list")
        print("refresh_folder_list")
        self.subfolders_with_images = find_subfolders_with_images(source_folder)
        # self.listbox.delete(0, tk.END)  # Clear the listbox
        # print("self.library_buttons ", self.library_buttons)
        print("self.tab ", self.tab)
        if self.tab in self.library_buttons:  # If this is that tab
            print("this is that tab")
            self.library_buttons[self.tab]["listbox"].delete(0, tk.END)
            for folder in self.subfolders_with_images:
                folder_name = os.path.basename(folder)
                # self.listbox.insert(tk.END, folder_name)
                self.library_buttons[self.tab]["listbox"].insert(tk.END, folder_name)
        print("refresh vege")
        self.update_percentage(percentage)

    def change_movies_source(self):
        write_to_document("change_movies_source")
        print("change_movies_source")
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            global source_folder
            self.source_folder = new_source_folder
            print("library ", id, "folder: ", new_source_folder)
            self.config["Paths"][
                str("source_folder_library_" + str(id))
            ] = new_source_folder
            self.movies_source_var.set(new_source_folder)
            source_folder = new_source_folder
            with open(str(script_folder + "/config.ini"), "w") as configfile:
                self.config.write(configfile)
            # self.movies_change_button.config(text=new_source_folder)
            if self.tab in self.library_buttons:
                self.library_buttons[self.tab]["movies_change_source_button"].config(
                    text=new_source_folder
                )
            self.refresh_folder_list()  # Call the refresh function after changing the source folder

    def change_movies_target(self):
        write_to_document("change_movies_target")
        print("change_movies_target")
        new_target_folder = tk.filedialog.askdirectory()
        print("new_target_folder ", new_target_folder)
        if new_target_folder:
            global target_folder
            self.target_folder = new_target_folder
            self.config["Paths"][
                str("target_folder_library_" + str(id))
            ] = new_target_folder
            self.movies_target_var.set(new_target_folder)
            target_folder = new_target_folder
            with open(str(script_folder + "/config.ini"), "w") as configfile:
                self.config.write(configfile)
            if self.tab in self.library_buttons:
                self.library_buttons[self.tab]["movies_change_target_button"].config(
                    text=new_target_folder
                )

    def create_config(self):
        write_to_document("create_config")
        print("Create config")
        config = configparser.ConfigParser()
        config.read(str(script_folder + "/config.ini"))
        newconfig = 0
        if "Settings" not in config:
            config["Settings"] = {}
            config["Paths"] = {}
            newconfig = 1
        config["Settings"][str("percentage_library_" + str(id))] = "30"
        config["Settings"][str("name_library_" + str(id))] = str("Library " + str(id))
        config["Settings"][str("schedule_library_" + str(id))] = str("No schedule")
        config["Paths"][
            str("source_folder_library_" + str(id))
        ] = "/path/to/source/folder"
        config["Paths"][
            str("target_folder_library_" + str(id))
        ] = "/path/to/target/folder"
        with open(str(script_folder + "/config.ini"), "w") as configfile:
            config.write(configfile)
        if newconfig == 0:
            self.library_count()
        else:
            global library_count, a
            library_size = 1
            a = 0
        new_tab_index = id - 1  # Change this index to the desired tab
        self.create_library_tab(id)
        self.notebook.select(new_tab_index)  # Active tab

        print("Create config vege")

    def move_selected_folders(self):
        selected_indices = self.library_buttons[self.tab][
            "listbox"
        ].curselection()  # Get indices of selected items
        selected_folders = [
            self.subfolders_with_images[idx] for idx in selected_indices
        ]
        move_folders_to_target(source_folder, target_folder, selected_folders)
        self.update_percentage(percentage)
        # for folder in selected_folders:
        #     print("Moving:", folder)

    def open_log_popup(self):
        log_entries = self.read_log_entries()

        popup = LogPopup(self, log_entries)
        popup.title("Log Entries")
        popup.geometry("400x300")
        popup.mainloop()

    def read_log_entries(self):
        log_entries = []
        search_for = str("Library " + str(id))
        with open("Log.txt", "r") as log_file:
            for line in log_file:
                if search_for in line:
                    cleaned_line = line.replace(search_for, "").strip()
                    log_entries.append(cleaned_line)
        return log_entries

    def update_id(self, event):
        # Get the selected tab index (0-based)
        global id
        selected_index = self.notebook.index(self.notebook.select())
        print("update_id")
        print(event)
        print(id)
        print("selected_index ", selected_index)
        # Update id based on the selected tab (adding 1 since id is 1-based)
        self.id = id = selected_index + 1
        self.tab = str("library" + str(id) + "_tab")
        print("1self.tab ", self.tab)
        self.load_library_settings(id)
        self.refresh_folder_list()
        print("update_id vege")
        print("id", id)


class LogPopup(tk.Toplevel):
    def __init__(self, parent, log_entries):
        super().__init__(parent)

        self.log_entries = log_entries
        self.listbox = tk.Listbox(self)

        self.scrollbar = tk.Scrollbar(self, orient="vertical")
        self.scrollbar.pack(side="right", fill="y")
        self.listbox.pack(fill="both", expand=True)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.listbox.yview)

        self.populate_listbox()

    def populate_listbox(self):
        self.listbox.delete(0, tk.END)
        for entry in self.log_entries:
            self.listbox.insert(tk.END, entry)


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
        print("Script started without any arguments.")


if __name__ == "__main__":
    check_argument()
    app = ImageMoveGUI()
    app.mainloop()

    if app.crontab_value is not None:
        print("Valid crontab expression:", app.crontab_value)
