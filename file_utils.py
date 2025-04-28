# File: file_utils.py

import os
import tkinter as tk
import shutil
import time
import threading
import queue
from concurrent.futures import ThreadPoolExecutor
from config import image_counter, screenshot_folder, get_crop_values
import gui

ImageGrab = None
crop_image_file_screenshot = None
crop_and_detect_ocr_and_logo = None
match_logo = None
screenshot_folder = None
folder_selected = False
screenshot_queue = queue.Queue()
executor = ThreadPoolExecutor(max_workers=3)

def create_screenshot_folder(start_listener_callback=None):
    from tkinter import filedialog, simpledialog
    import os
    import threading
    global screenshot_folder, folder_selected
    from config import image_counter
    if not folder_selected or not screenshot_folder:
        folder_path = filedialog.askdirectory(title="Select Folder Location")
        if not folder_path:
            return
        folder_selected = True
    else:
        folder_path = os.path.dirname(screenshot_folder)
    folder_name = simpledialog.askstring("Folder Name", "Enter folder name:")
    if not folder_name:
        return
    screenshot_folder = os.path.join(folder_path, folder_name)
    os.makedirs(screenshot_folder, exist_ok=True)
    os.startfile(screenshot_folder)
    image_counter.clear()
    if start_listener_callback:
        start_listener_callback()
    threading.Thread(target=_screenshot_worker, daemon=True).start()

def _generate_unique_name(base, ext=".jpg"):
    i = 1
    path = os.path.join(screenshot_folder, f"{base}{ext}")
    while os.path.exists(path):
        path = os.path.join(screenshot_folder, f"{base}_{i}{ext}")
        i += 1
    return path

def take_screenshot(current_folder):
    if not screenshot_folder:
        gui.show_auto_close_message("Please create or select the folder first.")
        return
    screenshot_queue.put(current_folder)

def _screenshot_worker():
    while True:
        current_folder = screenshot_queue.get()
        executor.submit(_process_screenshot, current_folder)

def _save_temp_screenshot():
    temp_path = os.path.join(screenshot_folder, "temp_screenshot.jpg")
    img = ImageGrab.grab()
    img.save(temp_path, format="JPEG", quality=85)
    for _ in range(20):
        if os.path.exists(temp_path) and os.path.getsize(temp_path) > 8000:
            return temp_path
        time.sleep(0.025)
    raise RuntimeError("Screenshot tidak valid atau terlalu kecil")

def _process_screenshot(current_folder):
    global ImageGrab, crop_image_file_screenshot, crop_and_detect_ocr_and_logo, match_logo
    try:
        if ImageGrab is None:
            from PIL import ImageGrab as IG
            ImageGrab = IG
        if crop_image_file_screenshot is None or crop_and_detect_ocr_and_logo is None or match_logo is None:
            from image_processing import crop_image_file_screenshot as ci, crop_and_detect_ocr_and_logo as cad, match_logo as ml
            crop_image_file_screenshot, crop_and_detect_ocr_and_logo, match_logo = ci, cad, ml
        if not screenshot_folder:
            gui.show_auto_close_message("Please create or select the folder first.")
            return
        temp_path = _save_temp_screenshot()
        crop_top, crop_bottom = get_crop_values()
        crop_image_file_screenshot(temp_path, top=crop_top, bottom=crop_bottom)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as local_executor:
            future_ocr = local_executor.submit(crop_and_detect_ocr_and_logo, temp_path, crop_top, crop_bottom)
            future_logo = local_executor.submit(match_logo, temp_path, crop_top, crop_bottom)
            try:
                page = future_ocr.result()
                print(f"[PAGE DETECTED] {page}")
            except Exception as e:
                print(f"[ERROR] crop_and_detect_ocr_and_logo gagal: {e}")
                page = "unknown"
            try:
                matched_logo = future_logo.result()
                print(f"[HASIL] Logo paling mirip adalah: {matched_logo}")
            except Exception as e:
                print(f"[ERROR] match_logo gagal: {e}")
                matched_logo = "Unknown"
        from PIL import Image
        try:
            with Image.open(temp_path) as img:
                img.verify()
        except Exception:
            raise RuntimeError("Gambar screenshot rusak.")
        if matched_logo != "Unknown":
            base_name = matched_logo
        elif page != "unknown":
            base_name = page
        else:
            base_name = "unknown"

        index = image_counter.get(base_name, 1)
        filename = f"{base_name} - {index}"
        final_path = _generate_unique_name(filename)
        Image.open(temp_path).convert("RGB").save(final_path, "JPEG", quality=85)
        try:
            os.remove(temp_path)
        except:
            pass
        image_counter[base_name] = image_counter.get(base_name, 1) + 1
        msg = f"Screenshot berhasil"
        gui.show_auto_close_message(msg)
        gui.custom_messagebox(msg)

    except Exception as e:
        print(f"[FATAL ERROR] Gagal mengambil screenshot: {e}")