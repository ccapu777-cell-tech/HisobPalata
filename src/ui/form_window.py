"""1-OYNA: Mustaqil xotirali (State-Isolated), xavfsiz almashinuvchi Qurilish Smeta Formasi."""
import tkinter as tk
from tkinter import ttk, messagebox
import config
from src.core.formulas import (
    calc_material_cost,
    calc_total_cost,
    calc_budget_remaining,
    calc_affordable_quantity
)
from src.core.audit_engine import AuditEngine
from src.core.market_benchmarks import MARKET_RATES

class FormWindow(tk.Toplevel):
    def __init__(self, parent, db, on_save_callback, x_pos, y_pos):
        super().__init__(parent)
        self.db = db
        self.on_save_callback = on_save_callback

        self.title("Qurilish Smetasini Kiritish va Nazorat Auditi")
        self.geometry(f"{config.FORM_WIDTH}x{config.FORM_HEIGHT}+{x_pos}+{y_pos}")
        self.configure(bg=config.COLOR_BG_PRIMARY)
        self.resizable(False, False)

        self.current_category = config.CATEGORIES[0]
        self.is_dirty = False  # Saqlanmagan o'zgarishlar bormi?
        self.dynamic_inputs = {}
        self.latest_audit = {}

        self._build_ui()
        self._load_category_view(self.current_category)

    def _build_ui(self):
        canvas = tk.Canvas(self, bg=config.COLOR_BG_PRIMARY, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable = ttk.Frame(canvas, style="Dark.TFrame")

        self.scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable, anchor="nw", width=config.FORM_WIDTH - 20)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Sarlavha va holat indikatori
        header_frame = tk.Frame(self.scrollable, bg=config.COLOR_BG_PRIMARY)
        header_frame.pack(fill=tk.X, padx=16, pady=(12, 6))

        tk.Label(
            header_frame,
            text="ARXITEKTURA VA QURILISH SMETASI",
            font=("Helvetica", 13, "bold"),
            fg=config.COLOR_TEXT_PRIMARY,
            bg=config.COLOR_BG_PRIMARY
        ).pack(side=tk.LEFT)

        self.lbl_save_status = tk.Label(
            header_frame,
            text="● Yangi forma",
            font=("Helvetica", 9, "bold"),
            fg="#FFD60A",
            bg=config.COLOR_BG_PRIMARY
        )
        self.lbl_save_status.pack(side=tk.RIGHT)

        # Toifa tanlash paneli
        cat_box = tk.Frame(self.scrollable, bg=config.COLOR_BG_PRIMARY, padx=16)
        cat_box.pack(fill=tk.X)

        tk.Label(cat_box, text="Material / Konstruksiya toifasi:", font=("Helvetica", 10, "bold"), fg=config.COLOR_TEXT_PRIMARY, bg=config.COLOR_BG_PRIMARY).pack(anchor="w")
        
        self.cmb_category = ttk.Combobox(cat_box, values=config.CATEGORIES, state="readonly", font=("Helvetica", 10))
        self.cmb_category.set(self.current_category)
        self.cmb_category.pack(fill=tk.X, pady=(3, 8))
        self.cmb_category.bind("<<ComboboxSelected>>", self._on_category_select_requested)

        # Dinamik toifa maydonlari
        self.fields_container = tk.Frame(self.scrollable, bg=config.COLOR_BG_SECONDARY, padx=14, pady=10)
        self.fields_container.pack(fill=tk.X, padx=16, pady=4)

        # Universal Moliyaviy Maydonlar
        self._build_financial_block()

        # Audit xulosasi paneli
        self._build_audit_display_block()

        # Saqlash tugmasi
        self.btn_save = tk.Button(
            self.scrollable,
            text=f"💾 {self.current_category.upper()} FORMASINI SAQLASH",
            font=("Helvetica", 11, "bold"),
            fg=config.COLOR_TEXT_PRIMARY,
            bg="#2E7D32",
            activebackground="#1B5E20",
            activeforeground="white",
            relief="flat",
            cursor="pointinghand",
            pady=10,
            command=self._save_record
        )
        self.btn_save.pack(fill=tk.X, padx=16, pady=(12, 20))

    def _build_financial_block(self):
        fin_frame = tk.Frame(self.scrollable, bg=config.COLOR_BG_SECONDARY, padx=14, pady=10)
        fin_frame.pack(fill=tk.X, padx=16, pady=8)

        tk.Label(fin_frame, text="UNIVERSAL MOLIYAVIY KO'RSATKICHLAR", font=("Helvetica", 10, "bold"), fg="#64B5F6", bg=config.COLOR_BG_SECONDARY).pack(anchor="w", pady=(0, 6))

        grid = tk.Frame(fin_frame, bg=config.COLOR_BG_SECONDARY)
        grid.pack(fill=tk.X)

        self.ent_q = self._grid_input(grid, "Miqdor / Hajm (Q):", 0, 0)
        self.ent_p = self._grid_input(grid, "Birlik Narxi (P, UZS):", 0, 1)
        self.ent_d = self._grid_input(grid, "Yetkazish xarajati (D, UZS):", 1, 0)
        self.ent_l = self._grid_input(grid, "Ish haqi/O'rnatish (L, UZS):", 1, 1)
        self.ent_e = self._grid_input(grid, "Qo'shimcha sarf (E, UZS):", 2, 0)
        self.ent_b = self._grid_input(grid, "Ajratilgan byudjet (B, UZS):", 2, 1)

        for ent in [self.ent_q, self.ent_p, self.ent_d, self.ent_l, self.ent_e, self.ent_b]:
            ent.bind("<KeyRelease>", self._on_field_changed)

        status_bar = tk.Frame(fin_frame, bg=config.COLOR_BG_SECONDARY)
        status_bar.pack(fill=tk.X, pady=(8, 4))
        tk.Label(status_bar, text="Auditorlik holati (Avtomatik):", font=("Helvetica", 9, "bold"), fg=config.COLOR_TEXT_PRIMARY, bg=config.COLOR_BG_SECONDARY).pack(side=tk.LEFT)

        self.status_var = tk.StringVar(value="Yashil")
        for val, col in [("Qizil", config.COLOR_RED), ("Sariq", config.COLOR_YELLOW), ("Yashil", config.COLOR_GREEN)]:
            tk.Radiobutton(
                status_bar,
                text=val,
                value=val,
                variable=self.status_var,
                fg=col,
                bg=config.COLOR_BG_SECONDARY,
                selectcolor=config.COLOR_BG_PRIMARY,
                activebackground=config.COLOR_BG_SECONDARY,
                activeforeground=col,
                font=("Helvetica", 9, "bold")
            ).pack(side=tk.LEFT, padx=8)

        self.lbl_calc_results = tk.Label(
            fin_frame,
            text="Material: 0 | Jami (C): 0 | Qoldiq (R): 0 UZS\nSotib olsa bo'ladi (Q max): 0",
            font=("Helvetica", 10, "bold"),
            fg="#81C784",
            bg="#212121",
            justify="left",
            padx=10,
            pady=8
        )
        self.lbl_calc_results.pack(fill=tk.X, pady=(8, 0))

    def _build_audit_display_block(self):
        self.audit_frame = tk.Frame(self.scrollable, bg="#1A1C1E", padx=14, pady=10, highlightbackground="#3A3D40", highlightthickness=1)
        self.audit_frame.pack(fill=tk.X, padx=16, pady=4)

        tk.Label(self.audit_frame, text="🔍 HISOB PALATASI: AVTOMATIK AUDIT TAHLILI", font=("Helvetica", 10, "bold"), fg="#FFD60A", bg="#1A1C1E").pack(anchor="w")

        self.lbl_audit_market_info = tk.Label(self.audit_frame, text="Bozor etalon narxi: ...", font=("Helvetica", 9), fg="#90CAF9", bg="#1A1C1E", anchor="w")
        self.lbl_audit_market_info.pack(fill=tk.X, pady=(4, 2))

        self.lbl_audit_summary = tk.Label(self.audit_frame, text="Tekshiruv kutilmoqda...", font=("Helvetica", 9), fg="#E0E0E0", bg="#1A1C1E", justify="left", wraplength=580, anchor="w")
        self.lbl_audit_summary.pack(fill=tk.X, pady=2)

        self.lbl_audit_damage = tk.Label(self.audit_frame, text="Taxminiy byudjet zarari: 0 UZS", font=("Helvetica", 10, "bold"), fg="#81C784", bg="#1A1C1E", anchor="w")
        self.lbl_audit_damage.pack(fill=tk.X, pady=(4, 0))

    def _grid_input(self, parent, label, r, c):
        f = tk.Frame(parent, bg=config.COLOR_BG_SECONDARY)
        f.grid(row=r, column=c, padx=6, pady=4, sticky="nsew")
        parent.columnconfigure(c, weight=1)

        tk.Label(f, text=label, font=("Helvetica", 8, "bold"), fg=config.COLOR_TEXT_PRIMARY, bg=config.COLOR_BG_SECONDARY).pack(anchor="w")
        ent = tk.Entry(f, font=("Helvetica", 10), bg=config.COLOR_INPUT_BG, fg="white", insertbackground="white", relief="flat")
        ent.pack(fill=tk.X, ipady=3)
        return ent

    # ---------------- XAVFSIZ ALMASHISH VA STATE BOSHQARUVI ----------------
    def _on_field_changed(self, event=None):
        self.is_dirty = True
        self.lbl_save_status.config(text="● Saqlanmagan o'zgarishlar", fg="#FF453A")
        self._recalc_all()

    def _on_category_select_requested(self, event=None):
        new_category = self.cmb_category.get()
        if new_category == self.current_category:
            return

        # Agar joriy formada saqlanmagan o'zgarishlar bo'lsa, ogohlantiramiz!
        if self.is_dirty:
            resp = messagebox.askyesnocancel(
                "Saqlanmagan o'zgarish!",
                f"'{self.current_category}' formasi hali saqlanmadi!\n\n"
                f"Yangi toifaga o'tishdan oldin hozirgi formani saqlashni xohlaysizmi?\n"
                f"• Ha: Saqlab keyin o'tish\n"
                f"• Yo'q: O'zgarishlarni bekor qilib o'tish\n"
                f"• Bekor qilish: Shu formada qolish"
            )
            if resp is True:
                saved = self._save_record(silence=True)
                if not saved:
                    self.cmb_category.set(self.current_category)
                    return
            elif resp is False:
                # O'zgarishlarni tashlab yangi toifaga o'tish
                pass
            else:
                # Bekor qilish (Cancel)
                self.cmb_category.set(self.current_category)
                return

        self.current_category = new_category
        self._load_category_view(new_category)

    def _load_category_view(self, cat: str):
        """Oldingi formani tozalab, yangi toifani toza xotira bilan yuklash."""
        # 1. Maydonlarni tozalash
        for w in self.fields_container.winfo_children():
            w.destroy()
        self.dynamic_inputs.clear()

        for ent in [self.ent_q, self.ent_p, self.ent_d, self.ent_l, self.ent_e, self.ent_b]:
            ent.delete(0, tk.END)

        self.btn_save.config(text=f"💾 {cat.upper()} FORMASINI SAQLASH")

        # 2. Yangi toifaga xos maydonlarni qurish
        self._build_specific_fields(cat)

        # 3. Bozor narxi ma'lumotlarini yuklash
        bench = MARKET_RATES.get(cat, {})
        m_p = bench.get("market_price", 0)
        unit_str = bench.get("unit", "")
        src_str = bench.get("source", "")
        self.lbl_audit_market_info.config(text=f"Bozor etaloni: {m_p:,.0f} UZS / {unit_str} ({src_str})")

        # 4. Bazada avval saqlangan ma'lumot bo'lsa, uni tiklash!
        existing = self.db.get_record_by_category(cat)
        if existing:
            self._fill_existing_data(existing)
            self.lbl_save_status.config(text="✓ Bazada saqlangan", fg="#81C784")
            self.is_dirty = False
        else:
            # Yangi toifa uchun etalon narxni taklif qilish
            self.ent_p.insert(0, f"{int(m_p)}")
            self.lbl_save_status.config(text="● Yangi forma", fg="#FFD60A")
            self.is_dirty = False

        self._recalc_all()

    def _fill_existing_data(self, record: dict):
        self.ent_q.delete(0, tk.END); self.ent_q.insert(0, f"{record['quantity']:g}")
        self.ent_p.delete(0, tk.END); self.ent_p.insert(0, f"{record['unit_price']:,.0f}".replace(",", ""))
        self.ent_d.delete(0, tk.END); self.ent_d.insert(0, f"{record['delivery_cost']:,.0f}".replace(",", ""))
        self.ent_l.delete(0, tk.END); self.ent_l.insert(0, f"{record['labor_cost']:,.0f}".replace(",", ""))
        self.ent_e.delete(0, tk.END); self.ent_e.insert(0, f"{record['extra_cost']:,.0f}".replace(",", ""))
        self.ent_b.delete(0, tk.END); self.ent_b.insert(0, f"{record['allocated_budget']:,.0f}".replace(",", ""))
        self.status_var.set(record["status"])

        attrs = record.get("attributes", {})
        for k, widget in self.dynamic_inputs.items():
            if k in attrs:
                if isinstance(widget, ttk.Combobox):
                    widget.set(attrs[k])
                elif isinstance(widget, tk.Entry):
                    widget.delete(0, tk.END)
                    widget.insert(0, str(attrs[k]))

    def _build_specific_fields(self, cat: str):
        tk.Label(self.fields_container, text=f"Maxsus parametrlar: {cat}", font=("Helvetica", 10, "bold"), fg="#FFD60A", bg=config.COLOR_BG_SECONDARY).pack(anchor="w", pady=(0, 6))

        # 1. Bino
        if cat == "Bino Parametrlari (Building)":
            self.dynamic_inputs["Bino kengligi (m)"] = self._add_entry("Bino kengligi (metr):", "14")
            self.dynamic_inputs["Bino uzunligi (m)"] = self._add_entry("Bino uzunligi (metr):", "20")
            self.dynamic_inputs["Bino balandligi (m)"] = self._add_entry("Bino umumiy balandligi (metr):", "16.0")
            self.dynamic_inputs["Qavatlar soni"] = self._add_combo("Qavatlar soni:", ["1 qavat", "2 qavat", "3 qavat", "4 qavat", "5 qavat"], 4)
            self.dynamic_inputs["Devor materiali"] = self._add_combo("Devor materiali:", ["Pishiq g'isht (Red Brick)", "Shlakoblok", "Gazoblok", "Monolit"], 0)
            self.dynamic_inputs["Tom turi"] = self._add_combo("Tom turi:", ["Yassi tom (Parapetli zamonaviy)", "Qiya metallocherepitsa tom"], 0)
            self.dynamic_inputs["Maydoni (m2)"] = self._add_entry("Umumiy maydoni (m²):", "1400")

        # 2. Qolip
        elif cat == "Qolip (Formwork)":
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["square meter", "pcs"], 0)
            self.dynamic_inputs["Qolip turi"] = self._add_combo("Qolip tizimi:", ["Monolit poydevor va plita qoliplari (DOKA/PERI)", "Ustun qolipi", "Yog'och karkas qolipi"], 0)
            self.dynamic_inputs["Ijara narxi (UZS)"] = self._add_entry("Ijara xarajati (UZS):", "0")

        # 3. Sement
        elif cat == "Sement (Cement)":
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["kg", "bags (qop)", "tonnes"], 0)
            self.dynamic_inputs["Sement markasi"] = self._add_combo("Sement markasi:", ["M-400 (Qizilqum)", "M-500 (Ohangaron)", "M-400 Sulfatbardosh"], 0)
            self.dynamic_inputs["Bir qop og'irligi (kg)"] = self._add_entry("Bir qop og'irligi (kg):", "50")
            self.dynamic_inputs["Bino maydoni (m2)"] = self._add_entry("Bino maydoni (m²):", "1400")

        # 4. Shag'al
        elif cat == "Shag'al (Gravel)":
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["cubic meter", "tonnes"], 0)
            self.dynamic_inputs["Fraktsiyasi"] = self._add_combo("Fraktsiyasi:", ["Fraktsiya 5-20 mm (Beton uchun)", "Fraktsiya 20-40 mm", "Fraktsiya 40-70 mm"], 0)
            self.dynamic_inputs["Bino maydoni (m2)"] = self._add_entry("Bino maydoni (m²):", "1400")

        # 5. Qum
        elif cat == "Qum (Sand)":
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["cubic meter", "tonnes"], 0)
            self.dynamic_inputs["Qum turi"] = self._add_combo("Qum turi:", ["Yuvilgan daryo qumi (Beton uchun)", "Karyer qumi (Suvoq uchun)"], 0)
            self.dynamic_inputs["Bino maydoni (m2)"] = self._add_entry("Bino maydoni (m²):", "1400")

        # 6. G'isht
        elif cat == "G'isht (Brick)":
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["pcs (dona)", "pallets"], 0)
            self.dynamic_inputs["G'isht standarti"] = self._add_combo("G'isht standarti:", ["Standart 250x120x65 mm", "Bir yarimtalik 250x120x88 mm"], 0)
            self.dynamic_inputs["Paletdagi dona soni"] = self._add_entry("Paletdagi dona soni:", "400")
            self.dynamic_inputs["Bino maydoni (m2)"] = self._add_entry("Bino maydoni (m²):", "1400")

        # 7. Shlakoblok
        elif cat == "Shlakoblok (Cinder Block)":
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["pcs (dona)", "pallets"], 0)
            self.dynamic_inputs["Blok o'lchami"] = self._add_combo("O'lchami:", ["Standart 20x20x40 sm", "Bo'linma 12x20x40 sm"], 0)
            self.dynamic_inputs["Paletdagi dona soni"] = self._add_entry("Paletdagi soni:", "72")

        # 8. Taxtalar
        elif cat == "Taxtalar (Wooden Boards)":
            self.dynamic_inputs["Taxta turi"] = self._add_combo(
                "Material turi:",
                ["Poydevor quyishdagi taxta", "Ustun va devorlar qurishdagi taxta", "Tom qurishdagi taxta", "Pol qurishdagi taxta"], 0
            )
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["cubic meter", "square meter", "pcs"], 0)
            self.dynamic_inputs["Uzunligi (m)"] = self._add_entry("Uzunligi (m):", "4.0")
            self.dynamic_inputs["Kengligi (m)"] = self._add_entry("Kengligi (m):", "0.20")
            self.dynamic_inputs["Qalinligi (mm)"] = self._add_entry("Qalinligi (mm):", "50")

        # 9. Armatura
        elif cat == "Armatura":
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["kg", "tonnes", "pcs"], 0)
            self.dynamic_inputs["Diametri (mm)"] = self._add_entry("Diametri (mm):", "18")
            self.dynamic_inputs["Uzunligi (m)"] = self._add_entry("Uzunligi (m):", "11.7")
            self.dynamic_inputs["Bino maydoni (m2)"] = self._add_entry("Bino maydoni (m²):", "1400")

        # 10. Fasad Materiallari
        elif cat == "Fasad Materiallari":
            self.dynamic_inputs["Fasad turi"] = self._add_combo("Fasad turi:", ["Travertin plitalari", "Alyukobond kompozit", "Granit plitalari", "Mineral dekorativ suvoq"], 0)
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["square meter", "pcs"], 0)
            self.dynamic_inputs["Qoplanish maydoni (m2)"] = self._add_entry("Qoplanish maydoni (m²):", "650")

        # 11. Standart Deraza
        elif cat == "Standart Deraza":
            self.dynamic_inputs["Profil turi"] = self._add_combo("Profil turi:", ["IMZO 60mm Trio", "Akfa 70mm Quattro", "Alyuminiy Thermo 65"], 0)
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["pcs (dona)", "square meter"], 0)
            self.dynamic_inputs["Kengligi (mm)"] = self._add_entry("Kengligi (mm):", "1400")
            self.dynamic_inputs["Balandligi (mm)"] = self._add_entry("Balandligi (mm):", "1600")

        # 12. Eshiklar
        elif cat == "Eshiklar":
            self.dynamic_inputs["Eshik turi"] = self._add_combo("Eshik turi:", ["Temir kirish xavfsizlik eshigi", "MDF xonalararo eshik", "PVX shisha eshik"], 0)
            self.dynamic_inputs["O'lchov birligi"] = self._add_combo("O'lchov birligi:", ["pcs (dona)", "square meter"], 0)
            self.dynamic_inputs["Kengligi (mm)"] = self._add_entry("Kengligi (mm):", "950")
            self.dynamic_inputs["Balandligi (mm)"] = self._add_entry("Balandligi (mm):", "2100")

    def _add_entry(self, label_text, default=""):
        tk.Label(self.fields_container, text=label_text, font=("Helvetica", 8, "bold"), fg=config.COLOR_TEXT_PRIMARY, bg=config.COLOR_BG_SECONDARY).pack(anchor="w", pady=(3, 1))
        ent = tk.Entry(self.fields_container, font=("Helvetica", 10), bg=config.COLOR_INPUT_BG, fg="white", insertbackground="white", relief="flat")
        if default:
            ent.insert(0, default)
        ent.pack(fill=tk.X, ipady=2)
        ent.bind("<KeyRelease>", self._on_field_changed)
        return ent

    def _add_combo(self, label_text, values, default_idx=0):
        tk.Label(self.fields_container, text=label_text, font=("Helvetica", 8, "bold"), fg=config.COLOR_TEXT_PRIMARY, bg=config.COLOR_BG_SECONDARY).pack(anchor="w", pady=(3, 1))
        cmb = ttk.Combobox(self.fields_container, values=values, state="readonly", font=("Helvetica", 10))
        cmb.current(default_idx)
        cmb.pack(fill=tk.X)
        cmb.bind("<<ComboboxSelected>>", self._on_field_changed)
        return cmb

    def _parse_val(self, entry):
        if not entry:
            return 0.0
        val = entry.get().strip().replace(" ", "").replace(",", ".").split()[0]
        return float(val) if val else 0.0

    def _recalc_all(self, event=None):
        try:
            q = self._parse_val(self.ent_q)
            p = self._parse_val(self.ent_p)
            d = self._parse_val(self.ent_d)
            l = self._parse_val(self.ent_l)
            e = self._parse_val(self.ent_e)
            b = self._parse_val(self.ent_b)

            m = calc_material_cost(q, p)
            c = calc_total_cost(q, p, d, l, e)
            r = calc_budget_remaining(b, c) if b > 0 else 0.0
            q_max = calc_affordable_quantity(b, p, d, l, e) if b > 0 else 0.0

            m_txt = f"{m:,.0f}".replace(",", " ")
            c_txt = f"{c:,.0f}".replace(",", " ")
            r_txt = f"{r:,.0f}".replace(",", " ")

            txt = f"Material (M): {m_txt} | Jami (C): {c_txt} | Qoldiq (R): {r_txt} UZS\nSotib olsa bo'ladi (Q max): {q_max:.2f}"
            self.lbl_calc_results.config(text=txt)

            # Audit tekshiruvi
            sqm = 0.0
            if "Maydoni (m2)" in self.dynamic_inputs:
                sqm = self._parse_val(self.dynamic_inputs["Maydoni (m2)"])
            elif "Bino maydoni (m2)" in self.dynamic_inputs:
                sqm = self._parse_val(self.dynamic_inputs["Bino maydoni (m2)"])

            self.latest_audit = AuditEngine.audit_entry(self.current_category, q, p, c, building_sqm=sqm)
            self.status_var.set(self.latest_audit["status"])

            findings_str = "\n• ".join([""] + self.latest_audit["findings"])
            self.lbl_audit_summary.config(text=f"Xulosa: {self.latest_audit['verdict']}{findings_str}")

            dmg = self.latest_audit["damage_amount"]
            if dmg > 0:
                self.lbl_audit_damage.config(text=f"⚠️ ANIQLANGAN BYUDJET ZARARI: {dmg:,.0f} UZS".replace(",", " "), fg="#FF453A")
            else:
                self.lbl_audit_damage.config(text="✓ Byudjetga ortiqcha zarar aniqlanmadi", fg="#81C784")

        except Exception:
            pass

    def _save_record(self, silence=False):
        q = self._parse_val(self.ent_q)
        p = self._parse_val(self.ent_p)
        d = self._parse_val(self.ent_d)
        l = self._parse_val(self.ent_l)
        e = self._parse_val(self.ent_e)
        b = self._parse_val(self.ent_b)

        if q <= 0 or p <= 0:
            if not silence:
                messagebox.showwarning("Xatolik", "Iltimos, Miqdor (Q) va Birlik narxi (P) maydonlarini to'ldiring!", parent=self)
            return False

        c = calc_total_cost(q, p, d, l, e)
        r = calc_budget_remaining(b, c) if b > 0 else 0.0
        q_max = calc_affordable_quantity(b, p, d, l, e) if b > 0 else 0.0

        attrs = {}
        sub_type = ""
        unit = ""

        for key, widget in self.dynamic_inputs.items():
            val = widget.get().strip()
            if "birligi" in key.lower():
                unit = val
            elif "turi" in key.lower() or "standarti" in key.lower():
                sub_type = val
                attrs[key] = val
            else:
                attrs[key] = val

        audit_res = self.latest_audit or {}
        audit_notes_str = "; ".join(audit_res.get("findings", []))

        data = {
            "category": self.current_category,
            "sub_type": sub_type,
            "unit": unit,
            "quantity": q,
            "unit_price": p,
            "delivery_cost": d,
            "labor_cost": l,
            "extra_cost": e,
            "total_cost": c,
            "allocated_budget": b,
            "remaining_budget": r,
            "affordable_quantity": q_max,
            "status": self.status_var.get(),
            "attributes": attrs,
            "market_price": audit_res.get("market_price", p),
            "damage_amount": audit_res.get("damage_amount", 0.0),
            "audit_notes": audit_notes_str
        }

        # Bazaga xavfsiz saqlash (Upsert)
        self.db.upsert_record(data)
        self.on_save_callback()

        self.is_dirty = False
        self.lbl_save_status.config(text="✓ Saqlandi", fg="#81C784")

        if not silence:
            msg = f"{self.current_category} muvaffaqiyatli saqlandi!"
            if audit_res.get("damage_amount", 0) > 0:
                msg += f"\n⚠️ Diqqat: {audit_res['damage_amount']:,.0f} UZS zarar qayd etildi."
            messagebox.showinfo("Muvaffaqiyatli Saqlandi", msg, parent=self)

        return True