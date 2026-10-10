"""Filtrlash paneli, kengaytiriluvchi quyuq kulrang audit kartochkalari va o'chirish logikasi."""
import tkinter as tk
from tkinter import ttk, messagebox
import config
from src.ui.styles import DarkButton
from src.core.visualizer_3d import Visualizer3D

class FilterBar(ttk.Frame):
    def __init__(self, parent, on_filter_selected):
        super().__init__(parent, style="Dark.TFrame")
        self.on_filter_selected = on_filter_selected

        filters = [
            ("Barchasi", config.COLOR_ALL),
            ("Qizil", config.COLOR_RED),
            ("Sariq", config.COLOR_YELLOW),
            ("Yashil", config.COLOR_GREEN)
        ]

        for label, color in reversed(filters):
            btn = DarkButton(
                self,
                text=label,
                bg="#2A2D33",
                fg="#FFFFFF",
                hover_bg=color,
                padx=12,
                pady=4,
                command=lambda lbl=label: self.on_filter_selected(lbl)
            )
            btn.pack(side=tk.RIGHT, padx=4, pady=6)


class ContentList(ttk.Frame):
    def __init__(self, parent, on_delete_record=None):
        super().__init__(parent, style="Dark.TFrame")
        self.visualizer_3d = Visualizer3D()
        self.on_delete_record = on_delete_record

        self.canvas = tk.Canvas(self, bg=config.COLOR_BG_PRIMARY, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas, style="Dark.TFrame")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas_window = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))

        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def render_items(self, items):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        if not items:
            lbl = tk.Label(
                self.scrollable_frame,
                text="Qurilish hisobotlari mavjud emas",
                font=("Helvetica", 12),
                fg=config.COLOR_TEXT_MUTED,
                bg=config.COLOR_BG_PRIMARY
            )
            lbl.pack(pady=40)
            return

        for item in items:
            self._render_card(item)

    def _render_card(self, item):
        card = tk.Frame(self.scrollable_frame, bg=config.COLOR_BG_SECONDARY, padx=14, pady=10)
        card.pack(fill=tk.X, padx=12, pady=6)

        badge_color = {
            "Qizil": config.COLOR_RED,
            "Sariq": config.COLOR_YELLOW,
            "Yashil": config.COLOR_GREEN
        }.get(item["status"], config.COLOR_ALL)

        # 1. Header (ID, Toifa, Holat)
        row1 = tk.Frame(card, bg=config.COLOR_BG_SECONDARY)
        row1.pack(fill=tk.X)
        tk.Label(row1, text=f"{item['id']} • {item['category']}", font=("Helvetica", 11, "bold"), fg="#64B5F6", bg=config.COLOR_BG_SECONDARY).pack(side=tk.LEFT)
        tk.Label(row1, text=f"● {item['status']}", font=("Helvetica", 11, "bold"), fg=badge_color, bg=config.COLOR_BG_SECONDARY).pack(side=tk.RIGHT)

        if item.get("sub_type"):
            tk.Label(card, text=f"Turi: {item['sub_type']}", font=("Helvetica", 10, "italic"), fg=config.COLOR_TEXT_PRIMARY, bg=config.COLOR_BG_SECONDARY, anchor="w").pack(fill=tk.X, pady=(2, 2))

        # 2. Qisqa ko'rinish
        q_txt = f"{item['quantity']:g} {item['unit']}".strip()
        p_txt = f"{item['unit_price']:,.0f}".replace(",", " ")
        c_txt = f"{item['total_cost']:,.0f}".replace(",", " ")

        summary_lbl = tk.Label(
            card,
            text=f"Hajm: {q_txt} @ {p_txt} UZS  |  Jami xarajat (C): {c_txt} UZS",
            font=("Helvetica", 10, "bold"),
            fg="#FFD60A",
            bg=config.COLOR_BG_SECONDARY,
            anchor="w"
        )
        summary_lbl.pack(fill=tk.X, pady=(4, 2))

        # 3. Kengaytiriluvchi panel
        expandable_frame = tk.Frame(card, bg="#181A20", padx=10, pady=8)

        m_cost = item["quantity"] * item["unit_price"]
        fin_details = (
            f"• Material sof bahosi (M = Q×P): {m_cost:,.0f} UZS\n"
            f"• Yetkazib berish (D): {item['delivery_cost']:,.0f} UZS\n"
            f"• Ish haqi va O'rnatish (L): {item['labor_cost']:,.0f} UZS\n"
            f"• Qo'shimcha sarf-xarajatlar (E): {item['extra_cost']:,.0f} UZS\n"
            f"• Ajratilgan byudjet: {item['allocated_budget']:,.0f} UZS  (Qoldiq: {item['remaining_budget']:,.0f} UZS)"
        ).replace(",", " ")

        tk.Label(expandable_frame, text="MABLAG'LARNING ANIQLANGAN TAQSIMOTI:", font=("Helvetica", 9, "bold"), fg="#64B5F6", bg="#181A20").pack(anchor="w")
        tk.Label(expandable_frame, text=fin_details, font=("Helvetica", 8), fg="#CFD8DC", bg="#181A20", justify="left", anchor="w").pack(fill=tk.X, pady=(2, 6))

        m_p = item.get("market_price", 0)
        damage = item.get("damage_amount", 0)
        notes = item.get("audit_notes", "")

        audit_box = tk.Frame(expandable_frame, bg="#23262C", padx=8, pady=6)
        audit_box.pack(fill=tk.X, pady=4)

        if m_p > 0:
            diff_pct = ((item["unit_price"] - m_p) / m_p) * 100.0
            color_diff = "#FF453A" if diff_pct > 20 else ("#FFD60A" if diff_pct > 5 else "#81C784")
            tk.Label(audit_box, text=f"Bozor etaloni: {m_p:,.0f} UZS  (Farq: {diff_pct:+.1f}%)", font=("Helvetica", 9, "bold"), fg=color_diff, bg="#23262C", anchor="w").pack(fill=tk.X)

        if damage > 0:
            tk.Label(audit_box, text=f"⚠️ ANIQLANGAN ZARAR: {damage:,.0f} UZS", font=("Helvetica", 10, "bold"), fg="#FF453A", bg="#23262C", anchor="w").pack(fill=tk.X, pady=(2, 2))

        if notes:
            tk.Label(audit_box, text=f"Auditor qaydi: {notes}", font=("Helvetica", 8), fg="#B0BEC5", bg="#23262C", justify="left", anchor="w", wraplength=500).pack(fill=tk.X)

        # 4. Pastki boshqaruv paneli (To'liq DarkButton)
        bottom_bar = tk.Frame(card, bg=config.COLOR_BG_SECONDARY)
        bottom_bar.pack(fill=tk.X, pady=(6, 0))

        is_expanded = {"val": False}

        def toggle_expand():
            if is_expanded["val"]:
                expandable_frame.pack_forget()
                btn_expand.set_text("▼ Batafsil Audit")
                is_expanded["val"] = False
            else:
                expandable_frame.pack(fill=tk.X, pady=(6, 4), before=bottom_bar)
                btn_expand.set_text("▲ Yopish")
                is_expanded["val"] = True

        btn_expand = DarkButton(
            bottom_bar,
            text="▼ Batafsil Audit",
            bg="#2E3238",
            fg="#FFFFFF",
            hover_bg="#3D424B",
            command=toggle_expand
        )
        btn_expand.pack(side=tk.LEFT)

        btn_3d = DarkButton(
            bottom_bar,
            text="🧊 3D",
            bg="#2E3238",
            fg="#64B5F6",
            hover_bg="#007AFF",
            command=lambda itm=item: self.visualizer_3d.show_item_3d(itm)
        )
        btn_3d.pack(side=tk.LEFT, padx=(6, 0))

        btn_del = DarkButton(
            bottom_bar,
            text="🗑 O'chirish",
            bg="#2E3238",
            fg="#FF453A",
            hover_bg="#C62828",
            command=lambda raw_id=item["raw_id"], name=item["id"]: self._confirm_delete(raw_id, name)
        )
        btn_del.pack(side=tk.LEFT, padx=(6, 0))

        tk.Label(bottom_bar, text=f"{item['created_at']}", font=("Helvetica", 8), fg=config.COLOR_TEXT_MUTED, bg=config.COLOR_BG_SECONDARY).pack(side=tk.RIGHT)

    def _confirm_delete(self, raw_id: int, item_id: str):
        if messagebox.askyesno("O'chirishni tasdiqlash", f"{item_id} raqamli smeta yozuvini bazadan butunlay o'chirmoqchimisiz?"):
            if self.on_delete_record:
                self.on_delete_record(raw_id)