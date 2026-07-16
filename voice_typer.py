import os
import sys
import subprocess
import time
import speech_recognition as sr

def type_text_and_enter(text):
    """
    Menggunakan AppleScript untuk menyalin teks ke clipboard, melakukan paste (Cmd+V),
    dan menekan tombol Enter (Return). Ini lebih cepat dan mendukung karakter khusus.
    """
    escaped_text = text.replace('\\', '\\\\').replace('"', '\\"').replace('$', '\\$')
    applescript = f'''
    try
        set oldClipboard to the clipboard
    on error
        set oldClipboard to ""
    end try
    
    set the clipboard to "{escaped_text}"
    delay 0.1
    
    tell application "System Events"
        keystroke "v" using {{command down}}
        delay 0.1
        key code 36 -- Enter (Return)
    end tell
    
    delay 0.5
    try
        set the clipboard to oldClipboard
    end try
    '''
    subprocess.run(["osascript", "-e", applescript])

def listen_and_type():
    recognizer = sr.Recognizer()
    
    # Sensitivitas mikrofon (bisa disesuaikan)
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300
    
    with sr.Microphone() as source:
        print("Mengkalkulasi kebisingan sekitar (Ambient noise)... mohon tenang sejenak.")
        recognizer.adjust_for_ambient_noise(source, duration=1.5)
        print("Selesai! Mulai mendengarkan...")
        print("-> Silakan bicara. Setelah Anda selesai berbicara, teks akan langsung terketik dan menekan Enter.")
        print("-> Tekan Ctrl+C di terminal ini untuk berhenti.")
        
        while True:
            try:
                print("\nMendengarkan suara...")
                audio = recognizer.listen(source, phrase_time_limit=15)
                
                print("Mentranskripsikan suara menjadi teks...")
                # Menggunakan Google Speech Recognition (gratis & mendukung Bahasa Indonesia)
                text = recognizer.recognize_google(audio, language="id-ID")
                print(f"Hasil Suara: \"{text}\"")
                
                if text.strip():
                    print("Mengetik dan menekan enter...")
                    type_text_and_enter(text)
                    
            except sr.UnknownValueError:
                print("Tidak dapat mengenali suara atau sunyi...")
            except (sr.RequestError, ConnectionResetError, OSError) as e:
                print(f"\n[!] Terjadi kesalahan koneksi: {e}")
                print("    Penjelasan: Layanan transkripsi Google mengalami gangguan koneksi (Connection reset).")
                # Deteksi jika ada kendala jaringan atau VPN
                print("    Solusi:")
                print("    1. Pastikan koneksi internet Anda stabil dan tidak diblokir oleh VPN/Proxy.")
                print("    2. SANGAT DISARANKAN menggunakan 'Metode A (macOS Shortcut)' karena menggunakan")
                print("       mesin dikte bawaan Apple yang berjalan secara lokal di Mac Anda (tidak butuh API luar).")
                print("       Panduan lengkap ada di: solusi_voice_typing.md\n")
            except KeyboardInterrupt:
                print("\nMenonaktifkan voice typer...")
                break
            except Exception as e:
                print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    print("====================================================")
    print("  MacBook Voice Typer & Auto-Enter (Python Version) ")
    print("====================================================")
    print("Pastikan kursor Anda sudah aktif di kolom teks yang diinginkan.")
    print("Memulai dalam 3 detik...")
    time.sleep(3)
    try:
        listen_and_type()
    except KeyboardInterrupt:
        print("\nKeluar.")
