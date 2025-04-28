# # ini file image_processing.py

# import cv2, numpy as np, tensorflow as tf
# from PIL import Image
# from ocr_utils import extract_text_platform
# from config import get_crop_values
# import os
# from concurrent.futures import ThreadPoolExecutor, as_completed

# TEMPLATE_DIR = "templates"
# CACHED_TEMPLATES = {}

# def load_templates():
#     for platform_name in os.listdir(TEMPLATE_DIR):
#         platform_path = os.path.join(TEMPLATE_DIR, platform_name)
#         if not os.path.isdir(platform_path):
#             continue
#         for file_name in os.listdir(platform_path):
#             if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
#                 full_path = os.path.join(platform_path, file_name)
#                 if full_path not in CACHED_TEMPLATES:
#                     template_img = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
#                     if template_img is not None:
#                         edges = cv2.Canny(template_img, 50, 150)
#                         CACHED_TEMPLATES[full_path] = (platform_name, template_img, edges, template_img.shape)
#                     else:
#                         print(f"[ERROR] Gagal memuat template: {full_path}")
#     print(f"[INFO] Template selesai dimuat dan diproses ({len(CACHED_TEMPLATES)} file).")
# load_templates()

# def crop_image_file_screenshot(path, top=0, bottom=0):
#     img = Image.open(path)
#     w, h = img.size
#     img.crop((0, top, w, h - bottom if bottom else h)).save(path)

# def resize_template_to_match(image_shape, template_img):
#     img_h, img_w = image_shape[:2]
#     t_h, t_w = template_img.shape[:2]
#     if t_h > img_h or t_w > img_w:
#         scale = min(img_h / t_h, img_w / t_w)
#         resized = cv2.resize(template_img, (int(t_w * scale), int(t_h * scale)))
#         return resized
#     return template_img

# def match_logo(screenshot_path, crop_top=None, crop_bottom=None, save_visual_result=True):
#     if crop_top is None or crop_bottom is None:
#         crop_top, crop_bottom = get_crop_values()
#     img = cv2.imread(screenshot_path)
#     if img is None:
#         print("[ERROR] Gagal membaca gambar:", screenshot_path)
#         return "Unknown"
#     h, w, _ = img.shape
#     gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     edge_img = cv2.Canny(gray_img, 50, 150).astype(np.float32)
#     best_match = None
#     best_score = 0.0
#     best_loc = None
#     best_template_shape = (0, 0)

#     def process_template(template_data):
#         label, template_img, template_edge, template_shape = template_data
#         resized_template_img = resize_template_to_match(edge_img.shape, template_img)
#         resized_template_edge = cv2.Canny(resized_template_img, 50, 150)
#         if edge_img.shape[0] < resized_template_edge.shape[0] or edge_img.shape[1] < resized_template_edge.shape[1]:
#             return None, None, None, None
#         res = cv2.matchTemplate(edge_img, resized_template_edge.astype(np.float32), cv2.TM_CCOEFF_NORMED)
#         _, max_val, _, max_loc = cv2.minMaxLoc(res)
#         return max_val, label, max_loc, resized_template_img.shape

#     with ThreadPoolExecutor() as executor:
#         results = executor.map(process_template, CACHED_TEMPLATES.values())

#     for max_val, label, max_loc, template_shape in results:
#         if max_val is None:
#             continue
#         if max_val > best_score:
#             best_score = max_val
#             best_match = label
#             best_loc = max_loc
#             best_template_shape = template_shape
#         if best_score >= 0.95:
#             break

#     if best_score < 0.80:
#         print(f"[LOGO MATCH] Confidence terlalu rendah ({best_score:.2f}) → Unknown")
#         return "Unknown"

#     print(f"[LOGO MATCH] Match dengan {best_match} (Score: {best_score:.2f})")

#     if save_visual_result and best_loc:
#         h_t, w_t = best_template_shape
#         top_left = best_loc
#         bottom_right = (top_left[0] + w_t, top_left[1] + h_t)
#         matched_img = img.copy()
#         cv2.rectangle(matched_img, top_left, bottom_right, (0, 255, 0), 2)
#         save_dir = "matched_logos"
#         os.makedirs(save_dir, exist_ok=True)
#         base_name = os.path.basename(screenshot_path)
#         name_no_ext = os.path.splitext(base_name)[0]
#         result_path = os.path.join(save_dir, f"{name_no_ext}_{best_match}_match.jpg")
#         cv2.imwrite(result_path, matched_img)
#         print(f"[SAVED] Hasil pencocokan disimpan: {result_path}")

#     return best_match

# def get_page_name_from_screenshot(path, crop_top=None, crop_bottom=None):
#     if crop_top is None or crop_bottom is None:
#         crop_top, crop_bottom = get_crop_values()
#     platform = match_logo(path, crop_top=crop_top, crop_bottom=crop_bottom)
#     if platform == "Unknown":
#         platform = extract_text_platform(path)
#     print(f"[PAGE INFO] Platform: {platform}")
#     return platform

# def crop_and_detect_ocr_and_logo(path, crop_top=None, crop_bottom=None):
#     if crop_top is None or crop_bottom is None:
#         crop_top, crop_bottom = get_crop_values()
#     crop_image_file_screenshot(path, crop_top, crop_bottom)
#     platform = get_page_name_from_screenshot(path, crop_top=crop_top, crop_bottom=crop_bottom)
#     print(f"[INFO] OCR dan Logo Deteksi selesai. Platform: {platform}")
#     return platform

import cv2, numpy as np, tensorflow as tf
from PIL import Image
from ocr_utils import extract_text_platform
from config import get_crop_values
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

# === SETUP LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        # logging.FileHandler("image_processing.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

TEMPLATE_DIR = "templates"
CACHED_TEMPLATES = {}

def load_templates():
    for platform_name in os.listdir(TEMPLATE_DIR):
        platform_path = os.path.join(TEMPLATE_DIR, platform_name)
        if not os.path.isdir(platform_path):
            continue
        for file_name in os.listdir(platform_path):
            if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                full_path = os.path.join(platform_path, file_name)
                if full_path not in CACHED_TEMPLATES:
                    template_img = cv2.imread(full_path, cv2.IMREAD_GRAYSCALE)
                    if template_img is not None:
                        edges = cv2.Canny(template_img, 50, 150)
                        CACHED_TEMPLATES[full_path] = (platform_name, template_img, edges, template_img.shape)
                    else:
                        logger.error(f"Gagal memuat template: {full_path}")
    logger.info(f"Template selesai dimuat dan diproses ({len(CACHED_TEMPLATES)} file).")

load_templates()

def crop_image_file_screenshot(path, top=0, bottom=0):
    logger.info(f"Melakukan crop gambar: {path}")
    img = Image.open(path)
    w, h = img.size
    img.crop((0, top, w, h - bottom if bottom else h)).save(path)

def resize_template_to_match(image_shape, template_img):
    img_h, img_w = image_shape[:2]
    t_h, t_w = template_img.shape[:2]
    if t_h > img_h or t_w > img_w:
        scale = min(img_h / t_h, img_w / t_w)
        resized = cv2.resize(template_img, (int(t_w * scale), int(t_h * scale)))
        return resized
    return template_img

def match_logo(screenshot_path, crop_top=None, crop_bottom=None, save_visual_result=True):
    if crop_top is None or crop_bottom is None:
        crop_top, crop_bottom = get_crop_values()

    logger.info(f"Membaca screenshot: {screenshot_path}")
    img = cv2.imread(screenshot_path)
    if img is None:
        logger.error(f"Gagal membaca gambar: {screenshot_path}")
        return "Unknown"

    h, w, _ = img.shape
    gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edge_img = cv2.Canny(gray_img, 50, 150).astype(np.float32)

    best_match = None
    best_score = 0.0
    best_loc = None
    best_template_shape = (0, 0)

    def process_template(template_data):
        label, template_img, template_edge, template_shape = template_data
        resized_template_img = resize_template_to_match(edge_img.shape, template_img)
        resized_template_edge = cv2.Canny(resized_template_img, 50, 150)
        if edge_img.shape[0] < resized_template_edge.shape[0] or edge_img.shape[1] < resized_template_edge.shape[1]:
            return None, None, None, None
        res = cv2.matchTemplate(edge_img, resized_template_edge.astype(np.float32), cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(res)
        return max_val, label, max_loc, resized_template_img.shape

    logger.info("Memulai proses pencocokan logo...")
    with ThreadPoolExecutor() as executor:
        results = executor.map(process_template, CACHED_TEMPLATES.values())

    for max_val, label, max_loc, template_shape in results:
        if max_val is None:
            continue
        if max_val > best_score:
            best_score = max_val
            best_match = label
            best_loc = max_loc
            best_template_shape = template_shape
        if best_score >= 0.95:
            break

    if best_score < 0.80:
        logger.warning(f"Confidence terlalu rendah ({best_score:.2f}) → Unknown")
        return "Unknown"

    logger.info(f"Match dengan {best_match} (Score: {best_score:.2f})")

    if save_visual_result and best_loc:
        h_t, w_t = best_template_shape
        top_left = best_loc
        bottom_right = (top_left[0] + w_t, top_left[1] + h_t)
        matched_img = img.copy()
        cv2.rectangle(matched_img, top_left, bottom_right, (0, 255, 0), 2)
        save_dir = "matched_logos"
        os.makedirs(save_dir, exist_ok=True)
        base_name = os.path.basename(screenshot_path)
        name_no_ext = os.path.splitext(base_name)[0]
        result_path = os.path.join(save_dir, f"{name_no_ext}_{best_match}_match.jpg")
        cv2.imwrite(result_path, matched_img)
        logger.info(f"Hasil pencocokan disimpan: {result_path}")

    return best_match

def get_page_name_from_screenshot(path, crop_top=None, crop_bottom=None):
    if crop_top is None or crop_bottom is None:
        crop_top, crop_bottom = get_crop_values()
    logger.info(f"Mendeteksi platform dari screenshot: {path}")
    platform = match_logo(path, crop_top=crop_top, crop_bottom=crop_bottom)
    if platform == "Unknown":
        platform = extract_text_platform(path)
    logger.info(f"Platform terdeteksi: {platform}")
    return platform

def crop_and_detect_ocr_and_logo(path, crop_top=None, crop_bottom=None):
    logger.info(f"Proses OCR dan deteksi logo dimulai untuk: {path}")
    if crop_top is None or crop_bottom is None:
        crop_top, crop_bottom = get_crop_values()
    crop_image_file_screenshot(path, crop_top, crop_bottom)
    platform = get_page_name_from_screenshot(path, crop_top=crop_top, crop_bottom=crop_bottom)
    logger.info(f"OCR dan Deteksi Logo selesai. Platform: {platform}")
    return platform


