@echo off
cd /d "%~dp0"

IF NOT EXIST ".venv" (
    echo ⚡ Loyiha birinchi marta ishga tushirilmoqda. Virtual muhit yaratilmoqda...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    echo 📦 Kutubxonalar yuklanmoqda...
    pip install --upgrade pip
    pip install -r requirements.txt
) ELSE (
    call .venv\Scripts\activate.bat
)

echo 🚀 Hisob Palatasi tizimi ishga tushmoqda...
python main.py
pause