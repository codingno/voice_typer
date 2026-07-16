import os
import sys
import time
import tempfile
import subprocess
import speech_recognition as sr

import platform

CURRENT_OS = platform.system()

# Import framework sesuai OS
if CURRENT_OS == 'Darwin':
    try:
        from Speech import SFSpeechRecognizer, NSLocale, SFSpeechURLRecognitionRequest
        from Foundation import NSURL, NSRunLoop, NSDefaultRunLoopMode, NSDate
        from CoreFoundation import CFRunLoopStop, CFRunLoopGetCurrent
    except ImportError:
        print("[X] Gagal mengimpor PyObjC Speech. Pastikan pyobjc-framework-Speech telah terinstal.")
        sys.exit(1)
else:
    try:
        from vosk import Model, KaldiRecognizer
        import json
        import wave
    except ImportError:
        pass
    
    # Impor controller pengetikan untuk Windows/Linux
    from pynput.keyboard import Controller as KController, Key
    keyboard_controller = KController()

# Global variables untuk menangani callback dari macOS Speech API
transcription_result = ""
is_task_final = False
current_speech_task = None
vosk_model = None

def resultHandler(result, error):
    global transcription_result, is_task_final
    if error:
        is_task_final = True
        try:
            CFRunLoopStop(CFRunLoopGetCurrent())
        except Exception:
            pass
    if result:
        transcription_result = result.bestTranscription().formattedString()
        if result.isFinal():
            is_task_final = True
            try:
                CFRunLoopStop(CFRunLoopGetCurrent())
            except Exception:
                pass

def transcribe_local_wav_cocoa(file_path, language_code="id-ID"):
    global transcription_result, is_task_final
    transcription_result = ""
    is_task_final = False
    
    locale = NSLocale.alloc().initWithLocaleIdentifier_(language_code)
    recognizer = SFSpeechRecognizer.alloc().initWithLocale_(locale)
    
    if not recognizer:
        locale = NSLocale.alloc().initWithLocaleIdentifier_("en-US")
        recognizer = SFSpeechRecognizer.alloc().initWithLocale_(locale)
        
    url = NSURL.fileURLWithPath_(str(file_path))
    request = SFSpeechURLRecognitionRequest.alloc().initWithURL_(url)
    
    global current_speech_task
    # Jalankan proses recognition
    current_speech_task = recognizer.recognitionTaskWithRequest_resultHandler_(request, resultHandler)
    
    # Jalankan Cocoa RunLoop sebentar agar callback handler berjalan secara sinkron
    start_time = time.time()
    while not is_task_final and (time.time() - start_time) < 8.0:
        # Spin runloop selama 0.05 detik
        date = NSDate.dateWithTimeIntervalSinceNow_(0.05)
        NSRunLoop.currentRunLoop().runMode_beforeDate_(NSDefaultRunLoopMode, date)
        
    if not is_task_final and current_speech_task:
        current_speech_task.cancel()
    current_speech_task = None
    
    return transcription_result

def transcribe_local_wav(file_path, language_code="id-ID"):
    if CURRENT_OS == 'Darwin':
        return transcribe_local_wav_cocoa(file_path, language_code)
    else:
        # Jalankan Vosk Offline di Windows / Linux
        global vosk_model
        model_path = "model"
        if not os.path.exists(model_path):
            print(f"\n[X] Folder '{model_path}' tidak ditemukan!")
            print("-> Harap unduh model Vosk Bahasa Indonesia dan taruh di folder 'model'.")
            return ""
            
        if vosk_model is None:
            print("\n[+] Memuat model Vosk Offline (hanya sekali saat pertama)...")
            try:
                vosk_model = Model(model_path)
            except Exception as e:
                print(f"[X] Gagal memuat model Vosk: {e}")
                return ""
                
        try:
            wf = wave.open(str(file_path), "rb")
            rec = KaldiRecognizer(vosk_model, wf.getframerate())
            rec.SetWords(False)
            
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                rec.AcceptWaveform(data)
                
            res = json.loads(rec.FinalResult())
            return res.get("text", "")
        except Exception as e:
            print(f"[X] Gagal transkripsi Vosk: {e}")
            return ""

def type_text_and_enter(text):
    """
    Simulasikan keyboard mengetik teks dan menekan Enter menggunakan AppleScript
    """
    if not text.strip():
        return
        
    # Format teks (kapitalisasi huruf pertama)
    formatted_text = text.strip()
    formatted_text = formatted_text[0].upper() + formatted_text[1:]
    
    if CURRENT_OS == 'Darwin':
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
            key code 36 -- Enter (Return)
        end tell
        
        delay 0.3
        try
            set the clipboard to oldClipboard
        end try
        '''
        subprocess.run(["osascript", "-e", applescript])
    else:
        # Gunakan pynput di Windows / Linux
        keyboard_controller.type(formatted_text)
        time.sleep(0.05)
        keyboard_controller.press(Key.enter)
        keyboard_controller.release(Key.enter)

def handle_git_commands(text):
    text_lower = text.lower().strip()
    
    commit_prefix = ""
    if text_lower.startswith("git commit"):
        commit_prefix = "git commit"
    elif text_lower.startswith("commit"):
        commit_prefix = "commit"
        
    if commit_prefix:
        raw_message = text[len(commit_prefix):].strip()
        commit_message = raw_message if raw_message else "Update via Voice Typer"
        
        print(f"\n[🚀 Git Automation] Mendeteksi perintah commit & push!")
        print(f"    Pesan commit: \"{commit_message}\"")
        
        try:
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            print("    Mengunggah (push) ke GitHub...")
            subprocess.run(["git", "push"], check=True)
            print("[✓] Git add, commit, dan push berhasil!")
            
            # Tampilkan notifikasi macOS
            subprocess.run(["osascript", "-e", "display notification \"Git Commit & Push Berhasil!\" with title \"Voice Typer Git\""])
            return True
        except subprocess.CalledProcessError as e:
            print(f"[X] Gagal menjalankan perintah git: {e}")
            subprocess.run(["osascript", "-e", "display notification \"Git Commit & Push Gagal!\" with title \"Voice Typer Git\""])
            return True
            
    return False

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--lang", default="id-ID", help="Language code (e.g. id-ID or en-US)")
    args, unknown = parser.parse_known_args()
    
    lang_code = args.lang
    if lang_code == "id":
        lang_code = "id-ID"
    elif lang_code == "en":
        lang_code = "en-US"

    print("=========================================================")
    print("  MacBook Voice Typer NATIVE & LOKAL (Continuous Mode)   ")
    print("=========================================================")
    print(f"Bahasa aktif / Language: {lang_code}")
    print("Menghubungkan ke Apple Speech Recognition engine...")
    
    # Request authorization saat startup
    def auth_callback(status):
        pass
    SFSpeechRecognizer.requestAuthorization_(auth_callback)
    
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = True
    recognizer.energy_threshold = 300
    
    try:
        microphone = sr.Microphone()
    except Exception as e:
        print(f"[X] Gagal membuka mikrofon: {e}")
        print("Pastikan Terminal mendapat izin akses mikrofon di System Settings.")
        sys.exit(1)
        
    with microphone as source:
        print("Menghitung kebisingan ruangan...")
        recognizer.adjust_for_ambient_noise(source, duration=1.0)
        print("[✓] Siap! Program mendengarkan terus-menerus.")
        print("-> Letakkan kursor di aplikasi chat/kolom teks Anda.")
        print("-> Silakan langsung bicara secara alami dalam Bahasa Indonesia.")
        print("-> Program akan mengetik dan menekan ENTER otomatis saat Anda diam.")
        print("-> Tekan Ctrl+C untuk berhenti.")
        print("---------------------------------------------------------")
        
        while True:
            try:
                print("\nMendengarkan...")
                audio = recognizer.listen(source, phrase_time_limit=15)
                
                print("Memproses suara secara lokal...")
                # Simpan audio hasil rekaman ke file wav sementara
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    temp_wav_path = f.name
                    f.write(audio.get_wav_data())
                
                try:
                    # Transkripsikan menggunakan Apple Speech API lokal
                    text = transcribe_local_wav(temp_wav_path, lang_code)
                    print(f"Hasil: \"{text}\"")
                    
                    if text.strip():
                        if handle_git_commands(text):
                            continue
                        type_text_and_enter(text)
                finally:
                    # Hapus file sementara
                    if os.path.exists(temp_wav_path):
                        os.remove(temp_wav_path)
                        
            except KeyboardInterrupt:
                print("\nMenonaktifkan voice typer. Sampai jumpa!")
                break
            except Exception as e:
                print(f"Terjadi kesalahan: {e}")

if __name__ == "__main__":
    main()
