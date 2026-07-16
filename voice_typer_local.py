import os
import sys
import json
import subprocess
import time
import pyaudio
from vosk import Model, KaldiRecognizer, SetLogLevel

# Matikan log internal Vosk yang terlalu bising agar terminal tetap bersih
SetLogLevel(-1)

def type_text_and_enter(text):
    """
    Menggunakan AppleScript untuk menyalin teks ke clipboard, melakukan paste (Cmd+V),
    dan menekan tombol Enter (Return). Ini 100% handal dan mendukung semua karakter.
    """
    if not text.strip():
        return
        
    # Format tulisan: Kapitalisasi huruf pertama
    formatted_text = text.strip()
    formatted_text = formatted_text[0].upper() + formatted_text[1:]
    
    escaped_text = formatted_text.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
    applescript = f'''
    try
        set oldClipboard to the clipboard
    on error
        set oldClipboard to ""
    end try
    
    set the clipboard to "{escaped_text}"
    delay 0.05
    
    tell application "System Events"
        keystroke "v" using {{command down}}
        delay 0.05
        key code 36 -- Tombol Enter (Return)
    end tell
    
    delay 0.3
    try
        set the clipboard to oldClipboard
    end try
    '''
    subprocess.run(["osascript", "-e", applescript])

def main():
    print("=========================================================")
    print("  MacBook Voice Typer NATIVE & LOKAL (Continuous Mode)   ")
    print("=========================================================")
    print("Mempersiapkan Model Bahasa Indonesia secara lokal...")
    
    try:
        # Mengunduh/memuat model Bahasa Indonesia otomatis (~45MB)
        model = Model(lang="id")
    except Exception as e:
        print(f"\n[X] Gagal memuat model lokal Bahasa Indonesia: {e}")
        print("Pastikan Anda terhubung ke internet saat pertama kali menjalankan agar model dapat diunduh.")
        sys.exit(1)
        
    # Inisialisasi recognizer pada sample rate 16000Hz
    recognizer = KaldiRecognizer(model, 16000)
    
    # Inisialisasi PyAudio
    p = pyaudio.PyAudio()
    
    try:
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=4000
        )
    except Exception as e:
        print(f"\n[X] Gagal membuka Mikrofon: {e}")
        print("Harap pastikan izin mikrofon untuk Terminal telah aktif di System Settings.")
        sys.exit(1)
        
    stream.start_stream()
    
    print("\n[✓] Sistem Siap!")
    print("-> Tempelkan kursor Anda di mana saja (WhatsApp, Word, Browser, dll).")
    print("-> Silakan mulai berbicara dalam Bahasa Indonesia.")
    print("-> Program akan MENDENGAR secara terus menerus, mengetikkan, dan langsung menekan ENTER.")
    print("-> Tekan Ctrl+C untuk keluar dari program.")
    print("---------------------------------------------------------")
    
    print("\n[Mendengarkan suara Anda...]")
    
    try:
        while True:
            data = stream.read(2000, exception_on_overflow=False)
            if len(data) == 0:
                continue
                
            # Deteksi suara
            if recognizer.AcceptWaveform(data):
                # Hasil kalimat lengkap yang selesai diucapkan (deteksi hening/pause)
                result_json = json.loads(recognizer.Result())
                text = result_json.get("text", "")
                
                if text.strip():
                    print(f"👉 Terdeteksi: \"{text}\" -> Mengetik & Enter")
                    type_text_and_enter(text)
            else:
                # Transkripsi real-time/parsial (sedang berbicara)
                partial_json = json.loads(recognizer.PartialResult())
                partial_text = partial_json.get("partial", "")
                if partial_text:
                    # Cetak di konsol agar user tahu program sedang mendengarkan secara real-time
                    sys.stdout.write(f"\rMendengar: {partial_text}...")
                    sys.stdout.flush()
                    
    except KeyboardInterrupt:
        print("\n\nMenonaktifkan voice typer lokal. Sampai jumpa!")
    finally:
        # Bersihkan resource
        stream.stop_stream()
        stream.close()
        p.terminate()

if __name__ == "__main__":
    main()
