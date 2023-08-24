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
import datetime

# This is where the magic happens
# sv_ttk.set_theme("dark")

# Determine the script's location
script_location = os.path.abspath(__file__)
script_folder = os.path.dirname(os.path.abspath(__file__))
print("Script location ", script_location)
id = 1  # Library number
arg1 = "moviemover"  # String to identify in the crontab table
percentage = 30
source_folder = "path/to/source"
target_folder = "path/to/target"


def main():  # If the script started with argument, this function will run
    print("main")
    write_to_document("main")
    # cron = CronTab(user=True)
    config = configparser.ConfigParser()

    # Check if the config file exists
    if os.path.exists(str(script_folder + "/config.ini")):
        config.read(str(script_folder + "/config.ini"))
        global percentage, source_folder, target_folder

        print("searcjhhh ", str("library " + str(id) + "source folder"))
        source_folder = config["Paths"][str("library_" + str(id) + "_source_folder")]
        target_folder = config["Paths"][str("library_" + str(id) + "_target_folder")]
        percentage = config["Settings"][str("library_" + str(id) + "_percentage")]
        #    self.parent.percentage = percentage
        print("source_folder ", source_folder)
        print("target_folder ", target_folder)
        print("percentage ", percentage)
        move_folders()
    else:
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
    def __init__(self, parent, title, percentage_n):
        write_to_document("__init__Popup")
        self.config = configparser.ConfigParser()
        global percentage
        # Check if the config file exists
        if os.path.exists(str(script_folder + "/config.ini")):
            self.config.read(str(script_folder + "/config.ini"))
        else:
            app.create_default_config()
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
        print("__init__ IMAGEGUI")

        self.config = configparser.ConfigParser()
        # self.tab = "Library 1"
        global percentage, source_folder, target_folder, id

        # Check if the config file exists
        if os.path.exists(str(script_folder + "/config.ini")):
            self.config.read(str(script_folder + "/config.ini"))
        else:
            self.create_default_config()

        self.tab = str("library" + str(id) + "_tab")
        self.tab_name = self.config["Settings"][str("library_" + str(id) + "_name")]
        self.title("Image Move GUI")
        self.style = ttk.Style()
        self.style.configure("TNotebook", background="red")
        self.style.theme_use("clam")  # Use the system color scheme

        self.notebook = ttk.Notebook(self)
        self.new_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.new_tab, text="Create New Library")
        self.notebook.pack(fill="both", expand=True)
        # Create new library button
        self.new_tab_button = ttk.Button(
            self.new_tab,
            text="Create new library with default settings",
            command=self.create_default_config,
            # Logic to get the next available id number, create entries in the config, then create library
        )
        self.new_tab_button.pack()

        self.library_count()

        # Dictionary to store buttons with library names as keys
        self.library_buttons = {}

        # Create library tabs based on the count
        for i in range(1, library_count + 1):
            self.create_library_tab(i)

        # Bind the tab change event
        self.notebook.bind("<<NotebookTabChanged>>", self.update_id)
        # update_id
        self.tab = str("library" + str(id) + "_tab")
        print("3self.tab ", self.tab)

        self.load_library_settings(id)
        new_tab_index = id - 1  # Change this index to the desired tab
        self.notebook.select(new_tab_index)  # Active tab

    def library_count(self):
        # Count the number of library sections
        global library_count
        library_size = 0
        for key in self.config["Settings"]:
            if key.endswith("percentage"):
                library_size += 1
        library_count = library_size
        print("Library count", library_size)
        print("self.config.sections()", self.config.sections())

    def load_library_settings(self, i):
        print("load_library_settings", i)
        self.library_count()
        if library_count + 1 == i:
            print("Create new library tab")
        else:
            self.config = configparser.ConfigParser()
            if os.path.exists(str(script_folder + "/config.ini")):
                self.config.read(str(script_folder + "/config.ini"))
            global percentage, source_folder, target_folder

            self.source_folder = source_folder = self.config["Paths"][
                str("library_" + str(i) + "_source_folder")
            ]
            self.target_folder = target_folder = self.config["Paths"][
                str("library_" + str(i) + "_target_folder")
            ]
            self.percentage = percentage = self.config["Settings"][
                str("library_" + str(i) + "_percentage")
            ]
            self.tab_name = self.config["Settings"][str("library_" + str(i) + "_name")]

            print("tab ", i, "source_folder ", self.source_folder)
            print("tab ", i, "target_folder ", self.target_folder)
            print("tab ", i, "percentage ", self.percentage)
            # print("tab ", i, "name ", self.tab)

        self.refresh_folder_list()  # Call the refresh function after changing the source folder

    def create_library_tab(self, i):
        print("create_library_tab ", i)
        self.config = configparser.ConfigParser()
        library_section = f"library_{i}"
        self.config.read(str(script_folder + "/config.ini"))
        tab = str("library" + str(i) + "_tab")
        self.load_library_settings(i)

        # Create a new tab for the library
        library_tab = ttk.Frame(self.notebook)
        self.notebook.insert(
            len(self.notebook.tabs()) - 1, library_tab, text=f"Library {i}"
        )

        # Source folder section
        self.movies_label = tk.Label(library_tab, text="Source Folder (copy from)")
        self.movies_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.movies_source_var = tk.StringVar(value=source_folder)
        self.movies_change_button = tk.Button(
            library_tab,
            text=source_folder,
            command=self.change_movies_source,
        )
        self.movies_change_button.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        # Target folder section
        self.movies_target_label = tk.Label(
            library_tab, text="Target Folder (copy to): "
        )
        self.movies_target_var = tk.StringVar(value=target_folder)
        self.movies_target_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.movies_change_target_button = tk.Button(
            library_tab,
            text=target_folder,
            command=self.change_movies_target,
        )
        self.movies_change_target_button.grid(
            row=1, column=1, padx=10, pady=5, sticky="w"
        )

        # Listbox and move button
        self.subfolders_with_images = find_subfolders_with_images(source_folder)

        self.listbox = tk.Listbox(library_tab, selectmode=tk.MULTIPLE)
        # self.refresh_folder_list()  # Call the function to populate the listbox
        self.listbox.grid(
            row=2, column=0, columnspan=3, rowspan=4, padx=10, pady=10, sticky="w"
        )

        self.refresh_button = tk.Button(
            library_tab, text="Refresh", command=self.refresh_folder_list
        )
        self.refresh_button.grid(
            row=6, column=0, columnspan=3, padx=10, pady=5, sticky="w"
        )

        self.move_selected_button = tk.Button(
            library_tab,
            text="Move Selected Folders",
            command=self.move_selected_folders,
        )
        self.move_selected_button.grid(
            row=7, column=0, columnspan=3, padx=10, pady=5, sticky="w"
        )

        # self.percentage_button = tk.Button(
        #     library_tab,
        #     text=str("Move " + str(percentage) + "%"),
        #     command=self.open_percentage_popup,
        # )
        # self.percentage_button.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        self.percentage_label = tk.Label(
            library_tab,
            text="Percentage of the found folders will be moved, rounded up:",
        )
        self.percentage_label.grid(row=2, column=1, padx=10, pady=5, sticky="w")
        # Create a slider for percentage
        self.percentage_slider = tk.Scale(
            library_tab,
            from_=1,
            to=100,
            orient="horizontal",
            showvalue=True,
            command=self.update_percentage,
        )
        self.percentage_slider.set(percentage)  # Set initial value
        self.percentage_slider.grid(row=3, column=1, padx=10, pady=5, sticky="w")

        # Label to show the current percentage
        # self.percentage_label = tk.Label(
        #     library_tab, text=str("Move " + str(percentage) + "%")
        # )
        # self.percentage_label.grid(row=2, column=2, padx=10, pady=5, sticky="w")

        self.ido_button = tk.Button(
            library_tab, text="Crontab Schedule", command=self.open_crontab_popup
        )
        self.ido_button.grid(row=4, column=1, padx=10, pady=5, sticky="w")

        self.crontab_value = None

        self.move_button = tk.Button(
            library_tab, text="Move Random Folders Now", command=move_folders
        )
        self.move_button.grid(row=5, column=1, padx=10, pady=5, sticky="w")

        self.log_button = tk.Button(
            library_tab, text="View Log Entries", command=self.open_log_popup
        )
        self.log_button.grid(row=7, column=1, columnspan=3, padx=10, pady=5, sticky="w")

        # Store the button in the dictionary with library name as key
        # self.library_buttons[tab] = self.movies_change_button
        # self.library_buttons[tab] = self.movies_change_target_button
        # self.library_buttons[tab] = self.percentage_button

        # Store library properties in the dictionary
        self.library_buttons[tab] = {
            "movies_change_source_button": self.movies_change_button,
            "movies_change_target_button": self.movies_change_target_button,
            "log_button": self.log_button,
            "listbox": self.listbox,
            # "percentage_button": self.percentage_button,
        }
        # print(self.library_buttons[tab])
        self.refresh_folder_list()

    def update_percentage(self, value):
        global percentage
        write_to_document("update_percentage")
        new_percentage = value
        if new_percentage.isdigit() and 1 <= int(new_percentage) <= 100:
            print("new percentage ", new_percentage)
            self.percentage = new_percentage  # Update the shared percentage value
            self.percentage_value = new_percentage  # Update the shared percentage value
            percentage = new_percentage
            # percentage = new_percentage
            self.config["Settings"][
                str("library_" + str(id) + "_percentage")
            ] = new_percentage
            with open(str(script_folder + "/config.ini"), "w") as configfile:
                self.config.write(configfile)
            # app.refresh_perc()
        else:
            messagebox.showerror(
                "Validation Error", f"The value should be between 1 and 100"
            )
        # percentage = self.percentage = int(value)
        # self.percentage_label.config(text=str("Move " + str(self.percentage) + "%"))

    def open_crontab_popup(self):
        write_to_document("open_crontab_popup")
        crontab_popup = PopupWindow(
            self, "Edit/Add crontab schedule", percentage
        )  # Create an instance of PopupWindow
        crontab_popup.crontab_popup()

    # def open_percentage_popup(self):
    #     write_to_document("open_percentage_popup")
    #     percentage_popup = PopupWindow(
    #         self, "Modify the percentage", percentage
    #     )  # Create an instance of PopupWindow
    # percentage_popup.percentage_popup()

    def refresh_folder_list(self):
        write_to_document("refresh_folder_list")
        print("refresh_folder_list")
        self.subfolders_with_images = find_subfolders_with_images(source_folder)
        # self.listbox.delete(0, tk.END)  # Clear the listbox
        print("self.tab ", self.tab)
        # print("self.library_buttons ", self.library_buttons)
        if self.tab in self.library_buttons:  # If this is that tab
            print("this is that tab")
            self.library_buttons[self.tab]["listbox"].delete(0, tk.END)
            for folder in self.subfolders_with_images:
                folder_name = os.path.basename(folder)
                # self.listbox.insert(tk.END, folder_name)
                self.library_buttons[self.tab]["listbox"].insert(tk.END, folder_name)

    # def refresh_perc(self):
    #     write_to_document("refresh_perc")
    #     if self.tab in self.library_buttons:
    #         self.library_buttons[self.tab]["percentage_button"].config(
    #             text=str("Move " + str(percentage) + "%")
    #         )

    def change_movies_source(self):
        write_to_document("change_movies_source")
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            global source_folder
            self.source_folder = new_source_folder
            print("library ", id, "folder: ", new_source_folder)
            self.config["Paths"][
                str("library_" + str(id) + "_source_folder")
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
        new_target_folder = tk.filedialog.askdirectory()
        if new_target_folder:
            global target_folder
            self.target_folder = new_target_folder
            self.config["Paths"][
                str("library_" + str(id) + "_target_folder")
            ] = new_target_folder
            self.movies_target_var.set(new_target_folder)
            target_folder = new_target_folder
            with open(str(script_folder + "/config.ini"), "w") as configfile:
                self.config.write(configfile)
            if self.tab in self.library_buttons:
                self.library_buttons[self.tab]["movies_change_target_button"].config(
                    text=new_target_folder
                )
            # self.movies_change_target_button.config(text=new_target_folder)

    def change_tv_series_source(self):
        write_to_document("change_tv_series_source")
        new_source_folder = tk.filedialog.askdirectory()
        if new_source_folder:
            self.source_folder_tv_series = new_source_folder
            self.config["Paths"][
                "tv_source_folder"
            ] = new_source_folder  # Replace this part
            self.tv_series_source_var.set(new_source_folder)

    def create_default_config(self):
        write_to_document("create_default_config")
        config = configparser.ConfigParser()
        config.read(str(script_folder + "/config.ini"))
        id = self.id
        # config["Paths"] = {
        #     str("library_" + str(id) + "_source_folder"): "/path/to/source/folder",
        #     str("library_" + str(id) + "_target_folder"): "/path/to/target/folder",
        # }
        # Add or update entries in the Settings section
        config["Settings"][str("library_" + str(id) + "_percentage")] = "30"
        config["Settings"][str("library_" + str(id) + "_name")] = str(
            "Library " + str(id)
        )
        config["Paths"][
            str("library_" + str(id) + "_source_folder")
        ] = "/path/to/source/folder"
        config["Paths"][
            str("library_" + str(id) + "_target_folder")
        ] = "/path/to/target/folder"
        # config["Settings"] = {
        #     str("library_" + str(id) + "_percentage"): 30,
        #     str("library_" + str(id) + "_name"): str("Library " + str(id)),
        # }
        with open(str(script_folder + "/config.ini"), "w") as configfile:
            config.write(configfile)

        app.create_library_tab(id)
        self.library_count()
        new_tab_index = id - 1  # Change this index to the desired tab
        self.notebook.select(new_tab_index)  # Active tab

    def move_selected_folders(self):
        selected_indices = self.library_buttons[self.tab][
            "listbox"
        ].curselection()  # Get indices of selected items
        selected_folders = [
            self.subfolders_with_images[idx] for idx in selected_indices
        ]
        move_folders_to_target(source_folder, target_folder, selected_folders)

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
        # Update id based on the selected tab (adding 1 since id is 1-based)
        self.id = id = selected_index + 1
        self.tab = str("library" + str(id) + "_tab")
        print("1self.tab ", self.tab)
        self.load_library_settings(id)
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
        print(
            "Script started without any arguments. It should have started with: script librarynumber"
        )


if __name__ == "__main__":
    check_argument()
    # capp = customtkinter.CTk()  # create CTk window like you do with the Tk window

    # def button_function():
    #     print("button pressed")

    # # Use CTkButton instead of tkinter Button
    # button = customtkinter.CTkButton(
    #     master=capp, text="CTkButton", command=button_function
    # )
    # # button.place(relx=0.5, rely=0.5, anchor=customtkinter.CENTER)

    # capp.mainloop()
    app = ImageMoveGUI()
    app.mainloop()

    if app.crontab_value is not None:
        print("Valid crontab expression:", app.crontab_value)
