"""O'zbekiston bozori (UzEx / Qurilish vazirligi ShNQ) etalon narxlari va sarf me'yorlari."""

# 1. BOZOR NARXLARI BAZASI (UZS, 2026-yilgi O'zRTXB va monitoring o'rtacha ko'rsatkichlari)
MARKET_RATES = {
    "G'isht (Brick)": {
        "unit": "pcs",
        "market_price": 1350.0,      # 1 dona pishiq qizil g'isht
        "min_allowed": 1100.0,
        "max_allowed": 1550.0,
        "source": "UzEx (Birja kotirovkasi) / Toshkent bozori"
    },
    "Sement (Cement)": {
        "unit": "kg",
        "market_price": 1250.0,      # 1 kg M-400 sement (qopda ~62 500 so'm)
        "min_allowed": 1050.0,
        "max_allowed": 1400.0,
        "source": "O'zRTXB Sement auksioni"
    },
    "Armatura": {
        "unit": "kg",
        "market_price": 10500.0,     # 1 kg A500C metall prokat (~10.5 mln so'm/t)
        "min_allowed": 9200.0,
        "max_allowed": 11800.0,
        "source": "O'zmetkombinat birja narxlari"
    },
    "Qum (Sand)": {
        "unit": "cubic meter",
        "market_price": 85000.0,     # 1 m3 yuvilgan karyer qumi
        "min_allowed": 65000.0,
        "max_allowed": 110000.0,
        "source": "Hududiy karyerlar o'rtacha stavkasi"
    },
    "Shag'al (Gravel)": {
        "unit": "cubic meter",
        "market_price": 95000.0,     # 1 m3 shag'al (fraktsiya 5-20)
        "min_allowed": 75000.0,
        "max_allowed": 125000.0,
        "source": "Hududiy karerlar o'rtacha stavkasi"
    },
    "Shlakoblok (Cinder Block)": {
        "unit": "pcs",
        "market_price": 6200.0,      # 1 dona 20x20x40 blok
        "min_allowed": 5200.0,
        "max_allowed": 75000.0,
        "source": "Ishlab chiqaruvchilar narxi"
    },
    "Taxtalar (Wooden Boards)": {
        "unit": "cubic meter",
        "market_price": 3800000.0,   # 1 m3 qarag'ay yog'ochi
        "min_allowed": 3200000.0,
        "max_allowed": 4400000.0,
        "source": "Import yog'och materiallari birjasi"
    },
    "Standart Deraza": {
        "unit": "pcs",
        "market_price": 1450000.0,   # 1 dona 1.4x1.6m PVX rom
        "min_allowed": 1150000.0,
        "max_allowed": 1850000.0,
        "source": "Mahalliy PVX ishlab chiqaruvchilar katalogi"
    },
    "Eshiklar": {
        "unit": "pcs",
        "market_price": 1200000.0,   # 1 dona standart MDF/eko-shpon blok
        "min_allowed": 850000.0,
        "max_allowed": 1650000.0,
        "source": "O'rtacha bozor bahosi"
    },
    "Qolip (Formwork)": {
        "unit": "square meter",
        "market_price": 45000.0,     # 1 m2 qolip ijarasi/ishlatilishi
        "min_allowed": 35000.0,
        "max_allowed": 60000.0,
        "source": "Qurilish uskunalar ijarasi"
    },
    "Fasad Materiallari": {
        "unit": "square meter",
        "market_price": 180000.0,    # 1 m2 o'rtacha fasad qoplamasi
        "min_allowed": 130000.0,
        "max_allowed": 240000.0,
        "source": "Bozor tahlili"
    },
    "Bino Parametrlari (Building)": {
        "unit": "square meter",
        "market_price": 4200000.0,   # 1 m2 qurilish tannarxi (smeta)
        "min_allowed": 3400000.0,
        "max_allowed": 4900000.0,
        "source": "Qurilish vazirligi bazaviy smeta qiymati"
    }
}

# 2. ShNQ (Shaharsozlik normalari va qoidalari) BO'YICHA SARF ME'YORLARI
# 1 m2 bino umumiy maydoniga to'g'ri keluvchi o'rtacha muhandislik sarf ko'rsatkichlari:
ENGINEERING_NORMS = {
    "G'isht (Brick)": {
        "norm_per_building_sqm": 75.0,     # 1 m2 bino uchun o'rtacha 70-80 dona g'isht (devorlar uchun)
        "tolerance_pct": 20.0             # Konstruksiyaga qarab ruxsat etilgan tebranish
    },
    "Armatura": {
        "norm_per_building_sqm": 42.0,     # 1 m2 bino maydoniga o'rtacha 35-50 kg armatura
        "tolerance_pct": 25.0
    },
    "Sement (Cement)": {
        "norm_per_building_sqm": 160.0,    # 1 m2 ga poydevor + orayopma uchun sement (kg)
        "tolerance_pct": 25.0
    },
    "Qum (Sand)": {
        "norm_per_building_sqm": 0.35,     # 1 m2 ga qum (m3)
        "tolerance_pct": 30.0
    },
    "Shag'al (Gravel)": {
        "norm_per_building_sqm": 0.45,     # 1 m2 ga shag'al (m3)
        "tolerance_pct": 30.0
    }
}