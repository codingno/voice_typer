import os
import sys
import time
import tempfile
import subprocess
import threading
import queue
import pyaudio
import wave
from pynput import keyboard

# Import PyObjC speech framework components
try:
    from Speech import SFSpeechRecognizer, NSLocale, SFSpeechURLRecognitionRequest
    from Foundation import NSURL, NSRunLoop, NSDefaultRunLoopMode, NSDate
    from CoreFoundation import CFRunLoopStop, CFRunLoopGetCurrent
except ImportError:
    print("[X] Gagal mengimpor PyObjC Speech.")
    sys.exit(1)

# Global variables
transcription_result = ""
is_task_final = False
audio_frames = []
p = pyaudio.PyAudio()
stream = None
lang_code = "id-ID"
current_speech_task = None

# Queue untuk mengirim event dari thread keyboard pynput ke main thread
event_queue = queue.Queue()

# Tombol pemicu: Right Control (ctrl_r)
PTT_KEY = keyboard.Key.ctrl_r
PTT_KEY_NAME = "Right Control (Ctrl Kanan)"

# Variabel pembantu untuk menghindari trigger duplikat saat key-repeat
key_is_held = False

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

def transcribe_local_wav(file_path, language_code="id-ID"):
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
    current_speech_task = recognizer.recognitionTaskWithRequest_resultHandler_(request, resultHandler)
    
    # Jalankan Cocoa RunLoop di Main Thread agar callback terpanggil
    start_time = time.time()
    while not is_task_final and (time.time() - start_time) < 8.0:
        date = NSDate.dateWithTimeIntervalSinceNow_(0.05)
        NSRunLoop.currentRunLoop().runMode_beforeDate_(NSDefaultRunLoopMode, date)
        
    if not is_task_final and current_speech_task:
        current_speech_task.cancel()
    current_speech_task = None
    
    return transcription_result

def type_text_and_enter(text):
    """
    Simulasikan keyboard mengetik teks dan menekan Enter menggunakan AppleScript
    """
    if not text.strip():
        return
        
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
        key code 36 -- Enter (Return)
    end tell
    
    delay 0.3
    try
        set the clipboard to oldClipboard
    end try
    '''
    subprocess.run(["osascript", "-e", applescript])

def save_wav_and_transcribe(frames):
    if not frames:
        return
        
    print("[+] Memproses suara lokal...")
    
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        temp_wav_path = f.name
        
    try:
        wf = wave.open(temp_wav_path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Transkripsi audio lokal
        text = transcribe_local_wav(temp_wav_path, lang_code)
        print(f"[✓] Hasil: \"{text}\"")
        
        if text.strip():
            type_text_and_enter(text)
    except Exception as e:
        print(f"[X] Gagal memproses audio: {e}")
    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

def on_press(key):
    global key_is_held
    if key == PTT_KEY:
        if not key_is_held:
            key_is_held = True
            event_queue.put("START")

def on_release(key):
    global key_is_held
    if key == PTT_KEY:
        if key_is_held:
            key_is_held = False
            event_queue.put("STOP")

def main():
    global lang_code
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
    print("  MacBook Voice Typer PUSH-TO-TALK (Tahan untuk Bicara)  ")
    print("=========================================================")
    print(f"Bahasa aktif / Language: {lang_code}")
    print(f"Tombol Pemicu: Tekan & Tahan tombol [{PTT_KEY_NAME}]")
    print("---------------------------------------------------------")
    print("Menghubungkan ke Apple Speech Recognition...")
    
    # Request authorization saat startup
    def auth_callback(status):
        pass
    SFSpeechRecognizer.requestAuthorization_(auth_callback)
    
    print("\n[✓] Siap! Program berjalan di background.")
    print("-> Posisikan kursor pada kolom teks tujuan Anda.")
    print(f"-> TEKAN & TAHAN tombol [{PTT_KEY_NAME}] untuk mulai berbicara.")
    print("-> LEPASKAN tombol setelah selesai berbicara untuk mengetik & Enter.")
    print("-> Tekan Ctrl+C di terminal ini untuk berhenti.")
    print("---------------------------------------------------------")
    print("\n[Menunggu tombol ditahan...]")
    
    # Jalankan listener keyboard di background thread
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    is_recording = False
    frames = []
    
    # Loop utama berjalan di MAIN THREAD
    try:
        while True:
            # Jika sedang merekam, kita baca data audio secara non-blocking
            if is_recording:
                try:
                    data = stream.read(1024, exception_on_overflow=False)
                    frames.append(data)
                except Exception:
                    pass
                    
            # Cek apakah ada event baru dari keyboard (non-blocking jika sedang merekam)
            try:
                # Jika sedang merekam, timeout dibuat sangat singkat agar input mic lancar
                timeout = 0.001 if is_recording else 0.1
                event = event_queue.get(timeout=timeout)
                
                if event == "START" and not is_recording:
                    print("\n[🎙️] MENDENGARKAN... (Bicaralah sambil MENAHAN tombol)")
                    frames = []
                    is_recording = True
                    try:
                        stream = p.open(
                            format=pyaudio.paInt16,
                            channels=1,
                            rate=16000,
                            input=True,
                            frames_per_buffer=1024
                        )
                        stream.start_stream()
                    except Exception as e:
                        print(f"[X] Gagal membuka mikrofon: {e}")
                        is_recording = False
                        
                elif event == "STOP" and is_recording:
                    print("[🛑] Tombol dilepas.")
                    is_recording = False
                    if stream:
                        try:
                            stream.stop_stream()
                            stream.close()
                        except Exception:
                            pass
                    # Jalankan transkripsi dan pengetikan di MAIN THREAD
                    save_wav_and_transcribe(frames)
                    print("\n[Menunggu tombol ditahan...]")
                    
            except queue.Empty:
                pass
                
    except KeyboardInterrupt:
        print("\nMenonaktifkan voice typer PTT. Sampai jumpa!")
    finally:
        if stream:
            try:
                stream.close()
            except Exception:
                pass
        p.terminate()
        listener.stop()

if __name__ == "__main__":
    main()
