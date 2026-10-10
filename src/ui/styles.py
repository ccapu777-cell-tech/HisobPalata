"""Dinamik Dark-Grey mavzu va platformaga bog'liq bo'lmagan DarkButton komponenti."""
import tkinter as tk
from tkinter import ttk
import config

class DarkButton(tk.Label):
    """macOS Aqua cheklovlarini aylanib o'tuvchi, toza kulrang fonli va oq yozuvli tugma."""
    def __init__(self, parent, text, command=None, bg=config.COLOR_BTN_GREY, fg=config.COLOR_TEXT_PRIMARY, hover_bg=config.COLOR_BTN_GREY_HOVER, padx=10, pady=5, font=("Helvetica", 9, "bold")):
        super().__init__(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            padx=padx,
            pady=pady,
            font=font,
            cursor="pointinghand",
            relief="flat",
            bd=0
        )
        self.command = command
        self.default_bg = bg
        self.hover_bg = hover_bg

        self.bind("<Enter>", lambda e: self.config(bg=self.hover_bg))
        self.bind("<Leave>", lambda e: self.config(bg=self.default_bg))
        self.bind("<Button-1>", lambda e: self._on_click())

    def _on_click(self):
        if self.command:
            self.command()

    def set_text(self, new_text):
        self.config(text=new_text)

    def set_bg(self, new_bg):
        self.default_bg = new_bg
        self.config(bg=new_bg)


def apply_styles(root):
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except Exception:
        pass

    # Ochiluvchi ro'yxat (Combobox) to'liq kulrang va oq matn
    style.configure(
        "TCombobox",
        fieldbackground="#2A2D33",
        background="#3A3D42",
        foreground="#FFFFFF",
        darkcolor="#2A2D33",
        lightcolor="#2A2D33",
        bordercolor="#44474E",
        arrowcolor="#FFFFFF",
        insertcolor="#FFFFFF",
        padding=4
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", "#2A2D33"), ("focus", "#33373E")],
        foreground=[("readonly", "#FFFFFF"), ("focus", "#FFFFFF")],
        background=[("readonly", "#3A3D42"), ("active", "#4A4D54")]
    )

    root.option_add("*TCombobox*Listbox.background", "#2A2D33")
    root.option_add("*TCombobox*Listbox.foreground", "#FFFFFF")
    root.option_add("*TCombobox*Listbox.selectBackground", "#007AFF")
    root.option_add("*TCombobox*Listbox.selectForeground", "#FFFFFF")

    style.configure("Dark.TFrame", background=config.COLOR_BG_PRIMARY)