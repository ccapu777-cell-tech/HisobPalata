# 🏛️ Automated Financial Pre-Audit & Benchmark Variance Platform — Qurilish Smetasi va Byudjet Nazorati Auditi Tizimi

**Automated Financial Pre-Audit & Benchmark Variance Platform** — O‘zbekiston Respublikasi qurilish me’yorlari (**ShNQ**) hamda tovar-xomashyo birjasi etalon narxlari (**O‘zRTXB / UzEx**) asosida davlat qurilish ob’ektlari smetalarini tekshiruvchi, moliyaviy qallobliklarni (narx va hajm ko‘pirtirilishi) avtomatik aniqlovchi ish stoli (desktop) tahlil platformasi.

Tizim interaktiv 4-bosqichli **3D BIM evolyutsion renderi** hamda **5.0 Trillion so‘mlik davlat byudjeti jamg‘armasi** uchun kinematik animatsion **Byudjet Daraxti (Tree Diagram)** bilan jihozlangan.

---

## 📌 Asosiy Imkoniyatlar

- **12 ta Qurilish Toifasi:**
  - Bino Parametrlari (Building), Qolip (Formwork), Sement (Cement), Shag‘al (Gravel), Qum (Sand), G‘isht (Brick), Shlakoblok (Cinder Block), Taxtalar (Wooden Boards), Armatura, Fasad Materiallari, Standart Deraza, Eshiklar.
- **Avtomatlashtirilgan Audit Dvijogi (Audit Engine):**
  - **Narx sun’iy oshirilishi (Price Gouging):** Bozor etalonidan $+5\%$ va $+20\%$ og‘ishlarni aniqlash.
  - **Hajm sun’iy ko‘paytirilishi (Volume Inflation):** ShNQ me’yoridan ortiqcha kiritilgan hajmlarni aniqlash va byudjetga yetkazilgan zararni hisoblash.
  - **Smeta ko‘rsatkichlari:** $M$ (Sof material bahosi), $D$ (Yetkazish), $L$ (Mehnat va montaj), $E$ (Qo‘shimcha sarf) va $C$ (Jami qiymat).
- **🏗️ 4-Bosqichli Real 3D Evolyutsiya:**
  - Barcha 12 toifa to‘ldirilgach, birgina darchada binoning 4 ta qurilish bosqichi yonma-yon render qilinadi:
    1. *Poydevor, qoliplar, armatura to‘ri va material uyumlari*
    2. *Temir-beton monolit karkas va orayopma plitalari*
    3. *G‘isht devorlar terimi*
    4. *Fasad, oyna romlari, kirish portali va tomi bilan to‘liq bitgan bino*
- **🌳 Kinematik "Tree Diagram" (Byudjet Daraxti):**
  - **5.0 Trillion UZS Davlat Jamg‘armasi** poydevori, 4 ta magistral shox ($M, D, L, E$) bo‘ylab uzluksiz oquvchi pul zarrachalari hamda 12 ta interaktiv smeta barglari orqali byudjetning qayerga, qanday va nima maqsadda sarflanganligini ko‘rsatuvchi 45-60 FPS jonli vizualizatsiya.
- **State-Isolated Xavfsiz Baza:**
  - Har bir toifa o‘zining mustaqil xotirasiga ega. Qayta saqlanganda dublikat yaratilmaydi (`SQLite UPSERT`).

---

## 💻 Tizim Talablari va Kross-Platforma

Dastur **macOS**, **Windows** va **Linux** operatsion tizimlarida bir xil barqarorlikda ishlaydi:

- **Python:** 3.10 – 3.12 *(tavsiya etiladi)*
- **Asosiy kutubxonalar:** `pyvista`, `numpy`
- **Ichki modullar:** `tkinter`, `sqlite3`, `json`, `math`, `subprocess`

---

## 🚀 O‘rnatish va Ishga Tushirish

### 1. Loyihani yuklab olish
```bash
git clone https://github.com/ccapu777-cell-tech/HisobPalata.git
cd HisobPalata
```

---

### 2. Ishga tushirish usullari

#### 🍎 macOS va 🐧 Linux uchun (One-Click)

1. Ishga tushirgichga ruxsat bering:
   ```bash
   chmod +x run.sh
   ```
2. Skriptni ishga tushiring:
   ```bash
   ./run.sh
   ```

> **Linux (Ubuntu/Debian) foydalanuvchilari uchun eslatma:**  
> Tkinter va OpenGL drayverlari o‘rnatilmagan bo‘lsa, quyidagi buyruqni bajaring:  
> `sudo apt update && sudo apt install python3-tk libgl1-mesa-glx`

---

#### 🪟 Windows uchun (One-Click)

Papka ichidagi **`run.bat`** fayli ustiga sichqoncha bilan ikki marta bosing.  
*(Skript virtual muhitni tekshiradi, kutubxonalarni o‘rnatadi va dasturni ochadi).*

---

#### ⚙️ Qo‘lda ishga tushirish (Universal)

Virtual muhit yaratish va kutubxonalarni o‘rnatish:
```bash
# Virtual muhit yaratish
python3 -m venv .venv

# Faollashtirish (macOS / Linux)
source .venv/bin/activate

# Faollashtirish (Windows Command Prompt)
# .venv\Scripts\activate.bat

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# Dasturni yurgizish
python3 main.py
```

---

## 📂 Loyiha Tuzilishi

```text
HisobPalata/
├── run.sh                  # macOS / Linux uchun avtomatlashtirilgan ishga tushirgich
├── run.bat                 # Windows uchun avtomatlashtirilgan ishga tushirgich
├── requirements.txt        # Tashqi kutubxonalar ro'yxati
├── config.py               # 5.0 Trln byudjet, toifalar va ranglar konfiguratsiyasi
├── main.py                 # Dastur kirish nuqtasi va oynalar koordinatsiyasi
├── .gitignore              # Keraksiz kesh va baza fayllari filtri
├── README.md               # Loyiha hujjatlari
└── src/
    ├── core/
    │   ├── audit_engine.py       # ShNQ va UzEx tekshiruv algoritmlari
    │   ├── database.py           # SQLite saqlash va boshqarish (UPSERT)
    │   ├── formulas.py           # M, C, R, Q_max matematik formulalari
    │   ├── market_benchmarks.py  # Rasmiy bozor etalon narxlari bazasi
    │   └── visualizer_3d.py      # PyVista 4-bosqichli va yakka tartibdagi 3D modeli
    └── ui/
        ├── components.py         # Kengaytiriluvchi quyuq kartochkalar va filtrlar
        ├── form_window.py        # 12 toifali mustaqil smeta kiritish oynasi
        ├── monitor_window.py     # Monitoring, checklist va asosiy boshqaruv oynasi
        ├── styles.py             # Dark-Grey dizayn va kross-platforma tugmalari
        └── tree_diagram_window.py# 5 Trln lik Byudjet Daraxti kinematik oynasi
```

---

## 📄 Litsenziya

Ushbu dasturiy ta’minot ta’lim va tahliliy tadqiqot maqsadlarida yaratilgan.
