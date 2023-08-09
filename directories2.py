import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

class PopupWindow:
    def __init__(self, parent):
        self.popup = tk.Toplevel(parent)
        self.popup.title("Popup Window")
        
        self.text_boxes = []
        for i in range(5):
            label = tk.Label(self.popup, text=f"Textbox {i+1}:")
            label.pack()
            text_box = tk.Entry(self.popup)
            text_box.pack()
            self.text_boxes.append(text_box)
        
        ok_button = tk.Button(self.popup, text="OK", command=self.close_popup)
        ok_button.pack()

    def close_popup(self):
        # Here, you can process the data from text boxes if needed
        self.popup.destroy()

class MainApplication:
    def __init__(self, root):
        self.root = root
        self.root.title("Clam Theme GUI")

        self.button = tk.Button(self.root, text="Open Popup", command=self.open_popup)
        self.button.pack(pady=20)

    def open_popup(self):
        popup = PopupWindow(self.root)

def main():
    root = tk.Tk()
    
    # Clam theme customization (you can adjust colors and styles)
    clam_theme = {
        "TButton": {"configure": {"background": "#ececec"}},
        "TLabel": {"configure": {"background": "#ececec"}},
        "TEntry": {"configure": {"background": "#ffffff"}},
        "TFrame": {"configure": {"background": "#ececec"}},
    }
    
    style = tk.ttk.Style(root)
    style.theme_create("clam_custom", parent="clam", settings=clam_theme)
    style.theme_use("clam_custom")

    app = MainApplication(root)
    root.mainloop()

if __name__ == "__main__":
    main()
