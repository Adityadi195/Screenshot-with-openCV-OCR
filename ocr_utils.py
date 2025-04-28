# # # ini file ocr_utils.py

# import re, cv2, pytesseract, numpy as np
# from PIL import Image, ImageEnhance
# from config import PLATFORM_URLS
# from rapidfuzz import process

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\tesseract.exe"

# def normalize_text(text):
#     return re.sub(r'[^a-z0-9:/._-]', '', text.lower())

# def preprocess_image(path):
#     img = cv2.imread(path)
#     if img is None:
#         print("[OCR WARNING] Gagal memuat gambar.")
#         return path
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     enhanced = cv2.equalizeHist(gray)
#     _, thresh = cv2.threshold(enhanced, 130, 255, cv2.THRESH_BINARY)
#     return thresh
# NORMALIZED_URLS = {
#     normalize_text(url): platform
#     for platform, urls in PLATFORM_URLS.items()
#     for url in urls
# }
# NORMALIZED_KEYS = list(NORMALIZED_URLS.keys())

# def extract_text_platform(path):
#     img = preprocess_image(path)
#     pil_img = Image.fromarray(img) if isinstance(img, np.ndarray) else Image.open(img)
#     custom_config = r'--oem 3 --psm 6'
#     raw = pytesseract.image_to_string(pil_img, config=custom_config).lower()
#     text = normalize_text(raw)
#     print(f"[OCR DEBUG] Extracted (normalized) text:\n{text}")
#     for norm_url, platform in NORMALIZED_URLS.items():
#         if norm_url in text:
#             print(f"[OCR MATCH] URL cocok dengan {platform}")
#             return platform
#     match, score, _ = process.extractOne(text, NORMALIZED_KEYS)
#     if score >= 65:
#         platform = NORMALIZED_URLS[match]
#         print(f"[OCR APPROX MATCH] URL mirip dengan {platform} (Similarity: {score:.2f})")
#         return platform
#     print("[OCR MATCH] Tidak ada link yang ditemukan dalam hasil OCR.")
#     return "Unknown"


import re, cv2, pytesseract, numpy as np
from PIL import Image, ImageEnhance
from config import PLATFORM_URLS
from rapidfuzz import process
import logging

# === SETUP LOGGING ===
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        # logging.FileHandler("ocr_utils.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# === KONFIGURASI TESSERACT ===
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\tesseract.exe"

def normalize_text(text):
    return re.sub(r'[^a-z0-9:/._-]', '', text.lower())

def preprocess_image(path):
    img = cv2.imread(path)
    if img is None:
        logger.warning("Gagal memuat gambar untuk OCR.")
        return path
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    enhanced = cv2.equalizeHist(gray)
    _, thresh = cv2.threshold(enhanced, 130, 255, cv2.THRESH_BINARY)
    logger.info(f"Preprocessing selesai untuk gambar: {path}")
    return thresh

# Buat URL yang sudah dinormalisasi
NORMALIZED_URLS = {
    normalize_text(url): platform
    for platform, urls in PLATFORM_URLS.items()
    for url in urls
}
NORMALIZED_KEYS = list(NORMALIZED_URLS.keys())

def extract_text_platform(path):
    logger.info(f"Memulai proses OCR untuk: {path}")
    img = preprocess_image(path)
    pil_img = Image.fromarray(img) if isinstance(img, np.ndarray) else Image.open(img)

    custom_config = r'--oem 3 --psm 6'
    raw = pytesseract.image_to_string(pil_img, config=custom_config).lower()
    text = normalize_text(raw)

    logger.debug(f"Raw OCR text:\n{raw}")
    logger.info(f"Text hasil OCR setelah normalisasi:\n{text}")

    for norm_url, platform in NORMALIZED_URLS.items():
        if norm_url in text:
            logger.info(f"URL cocok dengan {platform}")
            return platform

    match, score, _ = process.extractOne(text, NORMALIZED_KEYS)
    if score >= 65:
        platform = NORMALIZED_URLS[match]
        logger.info(f"URL mirip dengan {platform} (Similarity: {score:.2f})")
        return platform

    logger.warning("Tidak ada link yang ditemukan dalam hasil OCR.")
    return "Unknown"
