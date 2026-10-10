"""5 Trillionlik Davlat Byudjeti Jamg'armasi — Kinematik Jonli Byudjet Daraxti (Cinematic Tree Diagram)."""
import tkinter as tk
from tkinter import ttk
import math
import random
import time
import config

class TreeDiagramWindow(tk.Toplevel):
    def __init__(self, parent, db):
        super().__init__(parent)
        self.db = db
        self.title("Davlat Byudjeti Jamg'armasi (5.0 Trln UZS) — Kinematik Daraxt Diagrammasi")
        self.geometry("1300x860")
        self.configure(bg="#0A0B0E")
        self.resizable(True, True)

        self.records = self.db.get_records("Barchasi")
        self._calculate_metrics()

        # Animatsiya holatlari
        self.anim_running = True
        self.frame_count = 0
        self.intro_progress = 0.0      # 0.0 dan 1.0 gacha o'sish
        self.current_spent_disp = 0.0  # HUD rolling raqami
        self.selected_category = None

        # Zarrachalar tizimlari
        self.ambient_particles = []    # Fonga suzuvchi chang zarralari
        self.money_stream = []         # Shoxlar bo'ylab oquvchi pul zarralari
        self.shockwaves = []           # Bosilgandagi to'lqinlar

        self._init_particles()
        self._build_ui()

        # Oyna yopilganda animatsiya xotirasini tozalash
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Animatsiya siklini ishga tushirish (taxminan 40-50 FPS)
        self._animate_loop()

    def _calculate_metrics(self):
        self.pool_total = config.TOTAL_BUDGET_POOL  # 5 000 000 000 000 UZS
        self.total_spent = sum(r["total_cost"] for r in self.records)
        self.pool_remaining = self.pool_total - self.total_spent
        self.total_damage = sum(r["damage_amount"] for r in self.records)

        self.flow_material = sum(r["quantity"] * r["unit_price"] for r in self.records)
        self.flow_delivery = sum(r["delivery_cost"] for r in self.records)
        self.flow_labor = sum(r["labor_cost"] for r in self.records)
        self.flow_extra = sum(r["extra_cost"] for r in self.records)
        self.spent_pct = (self.total_spent / self.pool_total) * 100.0

    def _init_particles(self):
        # 40 ta fon zarrasi
        for _ in range(40):
            self.ambient_particles.append({
                "x": random.uniform(50, 850),
                "y": random.uniform(50, 750),
                "speed": random.uniform(0.3, 0.9),
                "radius": random.uniform(1.0, 2.5),
                "alpha_phase": random.uniform(0, math.pi * 2)
            })

    def _build_ui(self):
        # 1. KINEMATIK HUD PANEL (Top Bar)
        hud = tk.Frame(self, bg="#12141A", padx=16, pady=12, highlightbackground="#222630", highlightthickness=1)
        hud.pack(fill=tk.X, padx=14, pady=(12, 6))

        # Jamg'arma
        col1 = tk.Frame(hud, bg="#12141A"); col1.pack(side=tk.LEFT, padx=14)
        tk.Label(col1, text="DAVLAT BYUDJETI JAMG'ARMASI (POOL)", font=("Helvetica", 8, "bold"), fg="#78909C", bg="#12141A").pack(anchor="w")
        tk.Label(col1, text="5 000 000 000 000 UZS", font=("Helvetica", 13, "bold"), fg="#4FC3F7", bg="#12141A").pack(anchor="w")

        # Jonli sarf (Rolling Counter)
        col2 = tk.Frame(hud, bg="#12141A"); col2.pack(side=tk.LEFT, padx=16)
        tk.Label(col2, text="JAMI O'ZLASHTIRILDI (C)", font=("Helvetica", 8, "bold"), fg="#78909C", bg="#12141A").pack(anchor="w")
        self.lbl_hud_spent = tk.Label(col2, text="0 UZS", font=("Helvetica", 13, "bold"), fg="#FFD60A", bg="#12141A")
        self.lbl_hud_spent.pack(anchor="w")

        # Jamg'arma qoldig'i
        col3 = tk.Frame(hud, bg="#12141A"); col3.pack(side=tk.LEFT, padx=16)
        tk.Label(col3, text="JAMG'ARMA QOLDIG'I (R)", font=("Helvetica", 8, "bold"), fg="#78909C", bg="#12141A").pack(anchor="w")
        rem_str = f"{self.pool_remaining:,.0f} UZS".replace(",", " ")
        tk.Label(col3, text=rem_str, font=("Helvetica", 13, "bold"), fg="#81C784", bg="#12141A").pack(anchor="w")

        # Aniqlangan zarar
        col4 = tk.Frame(hud, bg="#12141A"); col4.pack(side=tk.RIGHT, padx=14)
        tk.Label(col4, text="ANIQLANGAN BYUDJET ZARARI", font=("Helvetica", 8, "bold"), fg="#78909C", bg="#12141A").pack(anchor="e")
        dmg_col = "#FF453A" if self.total_damage > 0 else "#81C784"
        dmg_str = f"{self.total_damage:,.0f} UZS".replace(",", " ")
        tk.Label(col4, text=dmg_str, font=("Helvetica", 13, "bold"), fg=dmg_col, bg="#12141A").pack(anchor="e")

        # 2. ASOSIY MAYDON (Kanvas + Analitik Yon Panel)
        main_split = tk.Frame(self, bg="#0A0B0E")
        main_split.pack(fill=tk.BOTH, expand=True, padx=14, pady=6)

        self.canvas = tk.Canvas(main_split, bg="#0D0E13", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # O'ng tarafdagi kiber-boshqaruv paneli
        self.detail_frame = tk.Frame(main_split, bg="#12141A", width=340, padx=16, pady=16, highlightbackground="#222630", highlightthickness=1)
        self.detail_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        self.detail_frame.pack_propagate(False)

        tk.Label(self.detail_frame, text="⚡ INTERAKTIV AUDIT KARTASI", font=("Helvetica", 10, "bold"), fg="#4FC3F7", bg="#12141A").pack(anchor="w")
        
        self.lbl_detail_title = tk.Label(self.detail_frame, text="Daraxtdan bargni tanlang", font=("Helvetica", 12, "bold"), fg="#FFFFFF", bg="#12141A", wraplength=300, justify="left")
        self.lbl_detail_title.pack(anchor="w", pady=(10, 4))

        self.lbl_detail_body = tk.Label(
            self.detail_frame,
            text="Daraxt shoxlaridagi 12 ta bargni bosing. Har bir barg sarflangan mablag'ning hajmi, yo'nalishi va shaffoflik darajasini ko'rsatadi.",
            font=("Helvetica", 9),
            fg="#90A4AE",
            bg="#12141A",
            justify="left",
            wraplength=300
        )
        self.lbl_detail_body.pack(anchor="w", pady=4)

    def _on_close(self):
        self.anim_running = False
        self.destroy()

    # =========================================================================
    # KINEMATIK RENDER SIKLI (ANIMATION LOOP)
    # =========================================================================
    def _animate_loop(self):
        if not self.anim_running:
            return

        self.frame_count += 1

        # Intro o'sish animatsiyasi (1.5 soniyada to'liq ochiladi)
        if self.intro_progress < 1.0:
            self.intro_progress = min(1.0, self.intro_progress + 0.02)

        # HUD Rolling counter animatsiyasi
        if self.current_spent_disp < self.total_spent:
            step = (self.total_spent - self.current_spent_disp) * 0.1
            self.current_spent_disp += max(1000000.0, step)
            if self.current_spent_disp >= self.total_spent:
                self.current_spent_disp = self.total_spent
            cur_txt = f"{self.current_spent_disp:,.0f} UZS ({self.spent_pct:.3f}%)".replace(",", " ")
            self.lbl_hud_spent.config(text=cur_txt)

        self._render_frame()

        # ~45 FPS
        self.after(22, self._animate_loop)

    def _render_frame(self):
        self.canvas.delete("all")
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()

        if cw < 100:
            cw, ch = 900, 720

        cx = cw / 2.0
        cy_base = ch - 50.0

        # --- 1. AMBIENT DIGITAL PARTICLES (ORQA FON DUST) ---
        for p in self.ambient_particles:
            p["y"] -= p["speed"]
            if p["y"] < 20:
                p["y"] = ch - 30
                p["x"] = random.uniform(40, cw - 40)
            glow_r = p["radius"] * (1.0 + 0.3 * math.sin(self.frame_count * 0.05 + p["alpha_phase"]))
            self.canvas.create_oval(p["x"] - glow_r, p["y"] - glow_r, p["x"] + glow_r, p["y"] + glow_r, fill="#1E293B", outline="")

        # --- 2. 5 TRLN POOL POYDEVORI VA AURA (ROOT BASE) ---
        pulse = 1.0 + 0.08 * math.sin(self.frame_count * 0.08)
        # Tashqi aura halqasi
        self.canvas.create_oval(cx - 150 * pulse, cy_base - 35 * pulse, cx + 150 * pulse, cy_base + 35 * pulse, fill="", outline="#00FFA3", width=1)
        # Asosiy gumbaz
        self.canvas.create_oval(cx - 130, cy_base - 28, cx + 130, cy_base + 28, fill="#0F2417", outline="#00E676", width=2)
        self.canvas.create_text(cx, cy_base, text="🏛️ 5.0 TRLN BYUDJET POOL", fill="#B9F6CA", font=("Helvetica", 11, "bold"))

        # --- 3. DARAXT TANASI (PROCEDURAL GROWING TRUNK) ---
        trunk_max_h = 190.0
        curr_trunk_h = trunk_max_h * min(1.0, self.intro_progress * 1.5)
        trunk_top_y = cy_base - curr_trunk_h

        # Organik egri tana
        w_bot = 40.0
        w_top = 22.0
        trunk_pts = [
            cx - w_bot, cy_base - 10,
            cx - w_top, trunk_top_y,
            cx + w_top, trunk_top_y,
            cx + w_bot, cy_base - 10
        ]
        self.canvas.create_polygon(trunk_pts, fill="#18231C", outline="#2E7D32", width=2, smooth=True)

        # Tana markazidagi yorug'lik tomiri (Glowing energy vein)
        self.canvas.create_line(cx, cy_base - 10, cx, trunk_top_y, fill="#00E676", width=3)

        # --- 4. 4 TA ASOSIY SHOX (M, D, L, E BRANCHES) ---
        branches = [
            {"id": "mat", "name": f"Material (M)\n{self.flow_material/1e9:.2f} mlrd", "end": (cx - 250, trunk_top_y - 100), "color": "#00E676"},
            {"id": "del", "name": f"Logistika (D)\n{self.flow_delivery/1e9:.2f} mlrd", "end": (cx - 90, trunk_top_y - 150), "color": "#00B0FF"},
            {"id": "lab", "name": f"Ish haqi (L)\n{self.flow_labor/1e9:.2f} mlrd", "end": (cx + 90, trunk_top_y - 150), "color": "#FF9100"},
            {"id": "ext", "name": f"Qo'shimcha (E)\n{self.flow_extra/1e9:.2f} mlrd", "end": (cx + 250, trunk_top_y - 100), "color": "#E040FB"}
        ]

        branch_progress = max(0.0, min(1.0, (self.intro_progress - 0.3) * 2.0))

        computed_branches = []
        for b in branches:
            ex_target, ey_target = b["end"]
            curr_ex = cx + (ex_target - cx) * branch_progress
            curr_ey = trunk_top_y + (ey_target - trunk_top_y) * branch_progress

            # Egri energiya shoxi
            mid_x = (cx + curr_ex) / 2.0
            mid_y = (trunk_top_y + curr_ey) / 2.0 + 15
            self.canvas.create_line(cx, trunk_top_y, mid_x, mid_y, curr_ex, curr_ey, fill=b["color"], width=5, smooth=True)

            if branch_progress > 0.8:
                # Shox tugunidagi yonib-o'chuvchi kristal
                node_r = 10.0 + 2.0 * math.sin(self.frame_count * 0.1)
                self.canvas.create_oval(curr_ex - node_r, curr_ey - node_r, curr_ex + node_r, curr_ey + node_r, fill=b["color"], outline="#FFFFFF", width=1)
                self.canvas.create_text(curr_ex, curr_ey + 26, text=b["name"], fill="#CFD8DC", font=("Helvetica", 8, "bold"), justify="center")

            computed_branches.append((curr_ex, curr_ey, b["color"]))

        # --- 5. PUL OQIMI ZARRALARI (MONEY STREAM FLOW) ---
        if branch_progress > 0.5:
            # Yangi zarralarni doimiy yaratish
            if self.frame_count % 3 == 0:
                b_idx = random.randint(0, 3)
                self.money_stream.append({
                    "progress": 0.0,
                    "branch_idx": b_idx,
                    "speed": random.uniform(0.015, 0.035),
                    "color": branches[b_idx]["color"]
                })

        # Zarralarni harakatlantirish
        for p in self.money_stream[:]:
            p["progress"] += p["speed"]
            if p["progress"] >= 1.0:
                self.money_stream.remove(p)
                continue

            # Bosqich 1: Tana bo'ylab o'sish (0.0 -> 0.4)
            # Bosqich 2: Shox bo'ylab ketish (0.4 -> 1.0)
            b_end_x, b_end_y, _ = computed_branches[p["branch_idx"]]
            if p["progress"] < 0.4:
                t_sub = p["progress"] / 0.4
                px = cx
                py = (cy_base - 10) + (trunk_top_y - (cy_base - 10)) * t_sub
            else:
                t_sub = (p["progress"] - 0.4) / 0.6
                px = cx + (b_end_x - cx) * t_sub
                py = trunk_top_y + (b_end_y - trunk_top_y) * t_sub

            self.canvas.create_oval(px - 3, py - 3, px + 3, py + 3, fill="#FFFFFF", outline=p["color"], width=1)

        # --- 6. 12 TA GULLOVCHI BARGLAR (LIVING BREATHING LEAVES) ---
        leaf_base_offsets = [
            (-350, -180), (-340, -270), (-260, -330),
            (-170, -370), (-70, -390), (70, -390),
            (170, -370), (260, -330), (340, -270),
            (350, -180), (-180, -230), (180, -230)
        ]

        leaves_progress = max(0.0, min(1.0, (self.intro_progress - 0.6) * 2.5))
        rec_dict = {r["category"]: r for r in self.records}

        for idx, cat_name in enumerate(config.CATEGORIES):
            bx_off, by_off = leaf_base_offsets[idx]
            b_parent_idx = idx % 4
            bx_parent, by_parent, b_col = computed_branches[b_parent_idx]

            # Havoda suzish (Floating sine wave)
            float_y = 6.0 * math.sin(self.frame_count * 0.06 + idx * 0.7)
            float_x = 3.0 * math.cos(self.frame_count * 0.05 + idx * 0.5)

            lx = bx_parent + (bx_off * 0.9 + float_x) * leaves_progress
            ly = by_parent + (by_off * 0.9 + float_y) * leaves_progress

            # Shoxdan barggacha nozik liana/vein tolasi
            self.canvas.create_line(bx_parent, by_parent, lx, ly, fill="#2E4A35", width=2, dash=(3, 2))

            item = rec_dict.get(cat_name)
            if item:
                st = item.get("status", "Yashil")
                leaf_col = config.COLOR_GREEN if st == "Yashil" else (config.COLOR_YELLOW if st == "Sariq" else config.COLOR_RED)
                cost_m = item['total_cost'] / 1e6
                text_label = f"{cat_name.split()[0]}\n{cost_m:.1f}M"
            else:
                leaf_col = "#374151"
                text_label = f"{cat_name.split()[0]}\n—"

            # Barg kattaligi va tanlangan holatdagi neon aura
            base_rx = 38 * leaves_progress
            base_ry = 22 * leaves_progress

            if leaves_progress > 0.2:
                # Tanlangan barg uchun kengayuvchi aura
                if self.selected_category == cat_name:
                    halo_r = 1.25 + 0.1 * math.sin(self.frame_count * 0.15)
                    self.canvas.create_oval(lx - base_rx * halo_r, ly - base_ry * halo_r, lx + base_rx * halo_r, ly + base_ry * halo_r, fill="", outline="#FFFFFF", width=2)

                tag = f"leaf_click_{idx}"
                self.canvas.create_oval(lx - base_rx, ly - base_ry, lx + base_rx, ly + base_ry, fill=leaf_col, outline="#FFFFFF", width=1, tags=(tag, "leaf_shape"))
                self.canvas.create_text(lx, ly, text=text_label, fill="#000000" if leaf_col != "#374151" else "#FFFFFF", font=("Helvetica", 8, "bold"), justify="center", tags=(tag, "leaf_shape"))

                # Bosish hodisasini bog'lash
                self.canvas.tag_bind(tag, "<Button-1>", lambda e, itm=item, name=cat_name, px=lx, py=ly: self._on_leaf_clicked(itm, name, px, py))

        # --- 7. INTERAKTIV ZARBA TO'LQINLARI (SHOCKWAVE RIPPLES) ---
        for sw in self.shockwaves[:]:
            sw["radius"] += 4.0
            sw["alpha"] -= 0.05
            if sw["alpha"] <= 0:
                self.shockwaves.remove(sw)
            else:
                self.canvas.create_oval(
                    sw["x"] - sw["radius"], sw["y"] - sw["radius"],
                    sw["x"] + sw["radius"], sw["y"] + sw["radius"],
                    fill="", outline="#00FFA3", width=2
                )

    def _on_leaf_clicked(self, item, name, click_x, click_y):
        self.selected_category = name
        # Radial zarba to'lqini yaratish
        self.shockwaves.append({"x": click_x, "y": click_y, "radius": 10.0, "alpha": 1.0})

        if not item:
            self.lbl_detail_title.config(text=name, fg="#FFD60A")
            self.lbl_detail_body.config(text="Ushbu toifa bo'yicha smeta xarajatlari hali kiritilmagan.")
            return

        st = item.get("status", "Yashil")
        st_color = config.COLOR_GREEN if st == "Yashil" else (config.COLOR_YELLOW if st == "Sariq" else config.COLOR_RED)
        self.lbl_detail_title.config(text=f"{item['id']} • {name}", fg=st_color)

        pool_pct = (item['total_cost'] / self.pool_total) * 100.0
        m_cost = item['quantity'] * item['unit_price']

        details = (
            f"● Audit Holati: {st.upper()}\n"
            f"● Jamg'arma ulushi: {pool_pct:.5f}%\n\n"
            f"QAYERGA VA QANCHA SARFLANDI:\n"
            f"• Miqdor: {item['quantity']:g} {item['unit']}\n"
            f"• Birlik bahosi: {item['unit_price']:,.0f} UZS\n\n"
            f"MOLIYAVIY OQIMLAR (QANDAY):\n"
            f"• Sof material (M): {m_cost:,.0f} UZS\n"
            f"• Logistika va transport (D): {item['delivery_cost']:,.0f} UZS\n"
            f"• Ish haqi va montaj (L): {item['labor_cost']:,.0f} UZS\n"
            f"• Qo'shimcha xarajatlar (E): {item['extra_cost']:,.0f} UZS\n"
            f"• JAMI SARF (C): {item['total_cost']:,.0f} UZS\n\n"
            f"AUDITORLIK NAZORATI VA ASOSI (NEGA):\n"
            f"• Bozor etalon narxi: {item.get('market_price', 0):,.0f} UZS\n"
            f"• Aniqlangan zarar: {item.get('damage_amount', 0):,.0f} UZS\n\n"
            f"Auditor qaydi:\n{item.get('audit_notes', 'Me\'yorda tasdiqlangan')}"
        ).replace(",", " ")

        self.lbl_detail_body.config(text=details)