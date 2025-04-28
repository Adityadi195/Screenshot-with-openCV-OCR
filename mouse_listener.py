# ini file mouse_listener.py

from pynput import mouse
import time, threading
from concurrent.futures import ThreadPoolExecutor
from file_utils import take_screenshot
from ocr_utils import extract_text_platform
import keyboard
from config import DEFAULT_SCREENSHOT_FOLDER

CLICK_DURATION, DRAG_THRESHOLD, MIN_INTERVAL = 0.3, 10, 0.6
left_click_time = right_click_time = last_ss_time = 0
start_pos, screenshot_taken = None, False
executor = ThreadPoolExecutor(max_workers=4)

def async_screenshot_and_detect(folder_name):
    def task():
        print("[INFO] Mengambil screenshot...")
        path = take_screenshot(folder_name)
        print("[INFO] Screenshot disimpan. Mulai OCR...")
        platform = extract_text_platform(path)
        print(f"[INFO] Platform terdeteksi: {platform}")
    executor.submit(task)

def on_click(x, y, button, pressed):
    global left_click_time, right_click_time, start_pos, screenshot_taken, last_ss_time
    now = time.time()
    
    if button == mouse.Button.left:
        if pressed:
            start_pos, left_click_time, screenshot_taken = (x, y), now, False
        else:
            dur = now - left_click_time
            dist = ((x - start_pos[0])**2 + (y - start_pos[1])**2)**0.5 if start_pos else 0
            if dur >= CLICK_DURATION and dist < DRAG_THRESHOLD and not screenshot_taken and now - last_ss_time >= MIN_INTERVAL:
                screenshot_taken, last_ss_time = True, now
                async_screenshot_and_detect(DEFAULT_SCREENSHOT_FOLDER)
            start_pos = None

def start_mouse_listener():
    print("[INFO] Listener mouse aktif. Menunggu interaksi...")
    mouse.Listener(on_click=on_click).start()