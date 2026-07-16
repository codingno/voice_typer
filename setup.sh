#!/bin/bash

# setup.sh - Menginstal dependensi untuk Voice Typer & Auto-Enter
echo "=============================================="
echo " Setup Voice Typer & Auto-Enter untuk macOS   "
echo "=============================================="
echo ""

# 1. Cek Homebrew
if ! command -v brew &> /dev/null; then
    echo "[X] Homebrew tidak terdeteksi. Silakan install Homebrew terlebih dahulu dari https://brew.sh/"
    exit 1
else
    echo "[✓] Homebrew terdeteksi."
fi

# 2. Install PortAudio jika belum ada
echo "Mengecek portaudio..."
if ! brew list portaudio &> /dev/null; then
    echo "Menginstal portaudio (dibutuhkan untuk audio input)..."
    brew install portaudio
else
    echo "[✓] PortAudio sudah terinstal."
fi

# 3. Buat virtual environment agar tidak mengganggu sistem Python
echo "Membuat virtual environment Python..."
python3 -m venv venv
source venv/bin/activate

# 4. Install library Python
echo "Menginstal library SpeechRecognition dan PyAudio..."
pip3 install --upgrade pip
pip3 install SpeechRecognition pyaudio

echo ""
echo "=============================================="
echo " Setup Selesai!"
echo "=============================================="
echo "Untuk menjalankan program, jalankan perintah:"
echo "  source venv/bin/activate"
echo "  python3 voice_typer.py"
echo ""
echo "Catatan Penting macOS:"
echo "1. Saat pertama kali dijalankan, macOS akan meminta izin Akses Mikrofon."
echo "2. Program ini menggunakan AppleScript untuk mensimulasikan keyboard (ketik & enter)."
echo "   Anda perlu memberikan izin Aksesibilitas (Accessibility) di:"
echo "   System Settings > Privacy & Security > Accessibility"
echo "   untuk aplikasi Terminal atau IDE (VS Code/Cursor) yang Anda gunakan."
echo "=============================================="
