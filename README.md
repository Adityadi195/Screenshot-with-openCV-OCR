Screenshot Detection and Platform Identification Tool

Proyek ini adalah sebuah aplikasi berbasis Python yang mengautomasi proses pengambilan screenshot dan deteksi platform menggunakan OCR (Optical Character Recognition) serta algoritma pencocokan berbasis URL. Aplikasi ini memungkinkan pengguna untuk mengambil screenshot dari layar, menganalisis gambar yang diambil menggunakan OCR untuk mendeteksi platform sosial seperti Facebook, YouTube, LinkedIn, dan X, serta mengekstrak informasi teks dari gambar.

Fitur Utama:
Pengambilan Screenshot:
Pengguna dapat mengambil screenshot dengan mengklik tombol kiri mouse selama durasi tertentu.

Screenshot disimpan dalam folder tertentu dan diproses lebih lanjut untuk analisis.

Deteksi Platform (Logo/URL detection):
Gambar yang diambil akan diproses menggunakan OCR untuk mengidentifikasi platform yang tertera dalam gambar berdasarkan URL yang terdapat di dalamnya (misalnya, URL Facebook, YouTube, dll).
Jika URL ditemukan dalam teks hasil OCR, platform yang sesuai akan dikembalikan.
Jika tidak ada kecocokan langsung, sistem akan menggunakan fuzzy matching untuk mencocokkan teks OCR dengan daftar URL yang sudah dinormalisasi.

Preprocessing Gambar:
Gambar yang diambil diproses terlebih dahulu menggunakan grayscale conversion, histogram equalization, dan thresholding untuk mempermudah OCR dalam membaca teks dengan lebih akurat.

OCR (Optical Character Recognition):
Tesseract OCR digunakan untuk mengekstrak teks dari gambar. OCR ini berfungsi untuk mengenali karakter dalam gambar dan membantu dalam deteksi platform berbasis URL.

Pengolahan Multi-Threading:
Proses pengambilan screenshot dan deteksi platform dijalankan secara asynchronous menggunakan multi-threading dengan ThreadPoolExecutor, yang memungkinkan aplikasi untuk menangani beberapa screenshot secara bersamaan tanpa memperlambat proses utama.


Dependencies:
pytesseract: Untuk OCR (Optical Character Recognition).
opencv-python: Untuk pemrosesan gambar seperti konversi ke grayscale, equalization, dan thresholding.
numpy: Untuk manipulasi array dan pemrosesan gambar.
Pillow: Untuk memanipulasi gambar menggunakan Python Imaging Library (PIL).
rapidfuzz: Untuk pencocokan teks menggunakan algoritma fuzzy matching.
pynput: Untuk mendeteksi klik mouse dan menjalankan listener.
