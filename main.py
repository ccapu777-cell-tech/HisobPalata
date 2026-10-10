"""Dasturni ishga tushirish moduli."""
import os
import sys
import tkinter as tk

os.environ["TK_SILENCE_DEPRECATION"] = "1"
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if sys.platform.startswith("win"):
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

import config
from src.core.database import Database
from src.ui.monitor_window import MonitorWindow
from src.ui.form_window import FormWindow

def main():
    root = tk.Tk()
    db = Database()

    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()

    total_w = config.FORM_WIDTH + config.MONITOR_WIDTH + 24
    start_x = max(0, int((screen_w - total_w) / 2))
    start_y = max(10, int((screen_h - config.FORM_HEIGHT) / 2))

    form_x = start_x
    monitor_x = start_x + config.FORM_WIDTH + 24

    monitor_app = None

    def refresh_monitor():
        if monitor_app:
            monitor_app.refresh()

    form_ref = {"window": None}

    def open_form():
        if form_ref["window"] is None or not form_ref["window"].winfo_exists():
            form_ref["window"] = FormWindow(root, db, refresh_monitor, form_x, start_y)
        else:
            form_ref["window"].lift()

    monitor_app = MonitorWindow(root, db, open_form, monitor_x, start_y)
    open_form()

    root.mainloop()

if __name__ == "__main__":
    main()