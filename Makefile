# Makefile untuk mempermudah menjalankan Voice Typer dan Demo ML

LANG ?= id-ID

.PHONY: run setup clean model ptt

run:
	@echo "Memulai Voice Typer..."
	@. venv/bin/activate && python3 voice_typer_native.py --lang $(LANG)

model:
	@echo "Memulai Model Machine Learning..."
	@. venv/bin/activate && python3 simple_ml_model.py

ptt:
	@echo "Memulai Voice Typer PTT (Tahan Tombol)..."
	@. venv/bin/activate && python3 voice_typer_ptt.py --lang $(LANG)

setup:
	@chmod +x setup.sh
	@./setup.sh

clean:
	@echo "Membersihkan virtual environment..."
	@rm -rf venv
	@echo "Selesai."
