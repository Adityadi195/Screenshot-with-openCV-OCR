# ini file config.py

import os
import ctypes
import pyautogui
import win32api
import win32con
import sys

screenshot_folder = ""
left_click_duration = 0.5
image_counter = {p: 1 for p in ["Facebook", "YouTube", "LinkedIn", "X"]}
start_mouse_position = None
drag_threshold = 10

DEFAULT_SCREENSHOT_FOLDER = os.path.join(os.getcwd(), "screenshots")

FOLDER_IMAGE_DETECT = "templates"

DETECT_IMAGE_FILE = {
    "Facebook": ["facebook_fullpage.png","facebook_link_white.png","facebook_link.png","facebook_logo_kecil.png","facebook_logo.png", "facebook_logo_kecil_black.png"],
    "YouTube": ["youtube_fullpage_white.png","youtube_fullpage.png","youtube_link_white.png", "youtube_link_white_100.png", "youtube_link_white_125.png" ,"youtube_link.png","youtube_logo_white.png"],
    "LinkedIn": ["linkedin_fullpage_dark.png","linkedin_fullpage.png","linkedin_link.png","linkedin_logo_grey.png","linkedIn_logo_kecil.png","linkedin_logo.png","linkedin_text_icon.png"],
    "X": ["x_dark_fullpage.png","x_fullpage.png","x_link_white.png","x_link.png","x_logo_white.png","x_logo.png"],
}
DETECT_IMAGE = {k: [os.path.join(FOLDER_IMAGE_DETECT, f) for f in v] for k, v in DETECT_IMAGE_FILE.items()}

PLATFORM_URLS = {
    "Facebook": ["facebook.com", "facebook", "www-acebook.com"],
    "YouTube": ["youtube.com", "youtube"],
    "LinkedIn": ["linkedin.com", "linkedin", "inkedin"],
    "X": ["xcom", "x.com", "bi ccom", "busi"]
}

_cached_dpi = None

def get_dpi_scale():
    global _cached_dpi
    if _cached_dpi is not None:
        return _cached_dpi

    try:
        hdc = ctypes.windll.gdi32.GetDC(0)
        dpi = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)
        ctypes.windll.gdi32.ReleaseDC(0, hdc)
        
        _cached_dpi = dpi
        return dpi
    except Exception as e:
        print(f"Error: {e}")
        _cached_dpi = 96
        return _cached_dpi

def get_crop_values_based_on_dpi():
    dpi = get_dpi_scale()
    if dpi == 96:  # Skala 100%
        return 18, 20
    elif dpi == 120:  # Skala 125%
        return 26, 30
    elif dpi == 144:  # Skala 150%
        return 28, 34
    else:
        return 16, 20

def get_crop_values():
    crop_top, crop_bottom = get_crop_values_based_on_dpi()
    print(f"Skala DPI terdeteksi, CROP_TOP: {crop_top}, CROP_BOTTOM: {crop_bottom}")
    return crop_top, crop_bottom

if __name__ == "__main__":
    crop_top, crop_bottom = get_crop_values()
    print(f"Nilai crop yang dihasilkan: CROP_TOP = {crop_top}, CROP_BOTTOM = {crop_bottom}")
