"""Loyiha konfiguratsiyasi va 5 Trillionlik Davlat Byudjeti Jamg'armasi."""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "qurilish_audit.db")

FORM_WIDTH = 620
FORM_HEIGHT = 800
MONITOR_WIDTH = 620
MONITOR_HEIGHT = 800
WINDOW_GAP = 20

# 5 Trillion so'mlik Davlat Byudjeti Jamg'armasi (Pool)
TOTAL_BUDGET_POOL = 5_000_000_000_000.0

COLOR_BG_PRIMARY = "#121316"
COLOR_BG_SECONDARY = "#1E2024"
COLOR_INPUT_BG = "#2A2D33"
COLOR_BTN_GREY = "#3A3D42"
COLOR_BTN_GREY_HOVER = "#4A4D54"
COLOR_TEXT_PRIMARY = "#FFFFFF"
COLOR_TEXT_MUTED = "#9E9E9E"

COLOR_RED = "#FF453A"
COLOR_YELLOW = "#FFD60A"
COLOR_GREEN = "#30D158"
COLOR_ALL = "#0A84FF"

CATEGORIES = [
    "Bino Parametrlari (Building)",
    "Qolip (Formwork)",
    "Sement (Cement)",
    "Shag'al (Gravel)",
    "Qum (Sand)",
    "G'isht (Brick)",
    "Shlakoblok (Cinder Block)",
    "Taxtalar (Wooden Boards)",
    "Armatura",
    "Fasad Materiallari",
    "Standart Deraza",
    "Eshiklar"
]