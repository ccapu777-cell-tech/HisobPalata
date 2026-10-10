#!/bin/bash
cd "$(dirname "$0")"

# Virtual muhit mavjud bo'lmasa yaratish
if [ ! -d ".venv" ]; then
    echo "⚡ Loyiha birinchi marta ishga tushirilmoqda. Virtual muhit (.venv) yaratilmoqda..."
    python3 -m venv .venv
    source .venv/bin/activate
    echo "📦 Kerakli kutubxonalar o'rnatilmoqda..."
    pip install --upgrade pip
    pip install -r requirements.txt
else
    source .venv/bin/activate
fi

# Dasturni ishga tushirish
echo "🚀 Hisob Palatasi monitoring tizimi ishga tushirilmoqda..."
python3 main.py