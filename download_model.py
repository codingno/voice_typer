import os
import urllib.request
import zipfile
import shutil

url = "https://alphacephei.com/vosk/models/vosk-model-small-id-0.3.zip"
zip_path = "model.zip"
extract_dir = "temp_model"
final_dir = "model"

print("=========================================================")
# Mengunduh model Bahasa Indonesia
print("Mengunduh model Bahasa Indonesia (~45MB) secara langsung...")
print("Mohon tunggu sebentar, kecepatan tergantung internet Anda...")

try:
    # Hapus file/folder lama jika ada
    if os.path.exists(zip_path):
        os.remove(zip_path)
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    if os.path.exists(final_dir):
        shutil.rmtree(final_dir)
        
    # Unduh file ZIP
    urllib.request.urlretrieve(url, zip_path)
    print("[✓] Unduhan selesai. Menyarikan file (unzipping)...")
    
    # Ekstrak file ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_dir)
    print("[✓] Ekstraksi selesai.")
    
    # Pindahkan folder hasil ekstraksi ke tujuan akhir
    extracted_folder_name = "vosk-model-small-id-0.3"
    src_folder = os.path.join(extract_dir, extracted_folder_name)
    
    if os.path.exists(src_folder):
        shutil.move(src_folder, final_dir)
        print("[✓] Model berhasil dipindahkan ke folder 'model'.")
    else:
        print("[X] Kesalahan: Folder hasil ekstraksi tidak ditemukan.")
        
    # Bersihkan file sampah
    if os.path.exists(zip_path):
        os.remove(zip_path)
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
        
    print("[✓] Selesai! Model Bahasa Indonesia siap digunakan secara lokal.")
    print("=========================================================")

except Exception as e:
    print(f"\n[X] Terjadi kesalahan saat mengunduh: {e}")
