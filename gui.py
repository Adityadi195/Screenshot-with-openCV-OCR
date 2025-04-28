# ini file gui.py

import tkinter as tk
from tkinter import simpledialog
import threading
from mouse_listener import start_mouse_listener
from file_utils import create_screenshot_folder

_root = _label_info = None

def set_gui_context(root, label_info):
    global _root, _label_info
    _root, _label_info = root, label_info

def show_auto_close_message(message):
    if _label_info:
        _label_info.config(
            text=message,
            font=("Segoe UI", 12),
            width=500
        )
        _root.after(2500, lambda: _label_info.config(text=""))


def custom_messagebox(message):
    if _root:
        msg = tk.Toplevel(_root)
        msg.title("Screenshot Saved")
        msg.geometry("1000x500")
        msg.attributes('-topmost', True)
        _root.update_idletasks()
        root_x = _root.winfo_x()
        root_y = _root.winfo_y()
        root_width = _root.winfo_width()
        root_height = _root.winfo_height()
        msg_width = 200
        msg_height = 100
        pos_x = root_x + (root_width - msg_width) // 2
        pos_y = root_y + (root_height - msg_height) // 2
        msg.geometry(f"{msg_width}x{msg_height}+{pos_x}+{pos_y}")
        msg.lift()
        msg.focus_force()
        tk.Label(msg, text=message, font=("Helvetica", 10), padx=10, pady=10).pack()
        msg.after(1000, msg.destroy)

def lazy_tf_log_disable():
    import tensorflow as tf
    tf.get_logger().setLevel('ERROR')
    print("[INIT] TensorFlow log disabled")

threading.Thread(target=lazy_tf_log_disable, daemon=True).start()

root = tk.Tk()
root.title("Screenshot Utility")
root.geometry("250x50")
label_info = tk.Label(root, text="", fg="green", font=("Helvetica", 12), anchor="w", padx=50)
label_info.pack(side="top", fill="x", pady=20)
set_gui_context(root, label_info)

def center_root():
    root.update_idletasks()
    width, height = 350, 250
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

def run_gui():
    def create_folder_callback():
        create_screenshot_folder(start_mouse_listener)
    tk.Button(root, text="Create Folder to test case",
              width=20, height=2, fg="white", bg="black",
              command=lambda: root.after(0, create_folder_callback)).pack(pady=2)
    tk.Button(root, text="Exit", 
              width=20, height=2, command=root.quit, fg="white", bg="red").pack(pady=2)
    center_root()
    root.mainloop()


