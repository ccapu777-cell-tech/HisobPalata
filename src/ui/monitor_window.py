"""2-OYNA: Monitoring, majburiy toifalar checklisti, 3D Render va Tree Diagram."""
import tkinter as tk
from tkinter import messagebox
import config
from src.ui.styles import apply_styles, DarkButton
from src.ui.components import FilterBar, ContentList
from src.core.visualizer_3d import Visualizer3D
from src.ui.tree_diagram_window import TreeDiagramWindow

class MonitorWindow:
    def __init__(self, root, db, open_form_callback, x_pos, y_pos):
        self.root = root
        self.db = db
        self.open_form_callback = open_form_callback
        self.current_filter = "Barchasi"
        self.visualizer_3d = Visualizer3D()

        self.root.title("Qurilish Monitoringi (Hisob Palatasi)")
        self.root.geometry(f"{config.MONITOR_WIDTH}x{config.MONITOR_HEIGHT}+{x_pos}+{y_pos}")
        self.root.minsize(config.MONITOR_WIDTH, config.MONITOR_HEIGHT)
        self.root.resizable(False, False)
        self.root.configure(bg=config.COLOR_BG_PRIMARY)

        apply_styles(self.root)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # 1. Yuqori sarlavha paneli
        top_header = tk.Frame(self.root, bg=config.COLOR_BG_PRIMARY)
        top_header.pack(fill=tk.X, padx=12, pady=(10, 4))

        tk.Label(
            top_header,
            text="Qurilish Xarajatlari Auditi",
            font=("Helvetica", 13, "bold"),
            fg=config.COLOR_TEXT_PRIMARY,
            bg=config.COLOR_BG_PRIMARY
        ).pack(side=tk.LEFT)

        btn_new = DarkButton(
            top_header,
            text="+ Yangi Smeta",
            bg="#2E3238",
            fg="#64B5F6",
            hover_bg="#007AFF",
            command=self.open_form_callback
        )
        btn_new.pack(side=tk.RIGHT)

        # 2. CHECKLIST VA TREE DIAGRAM / 4-BOSQICH TUGMALARI
        progress_bar_frame = tk.Frame(self.root, bg="#1E2024", padx=10, pady=8, highlightbackground="#2C3038", highlightthickness=1)
        progress_bar_frame.pack(fill=tk.X, padx=12, pady=(2, 6))

        self.lbl_checklist = tk.Label(
            progress_bar_frame,
            text="To'ldirilgan toifalar: 0 / 12",
            font=("Helvetica", 9, "bold"),
            fg="#FFD60A",
            bg="#1E2024"
        )
        self.lbl_checklist.pack(side=tk.LEFT)

        # 4-Bosqichli 3D Render
        self.btn_multi_3d = DarkButton(
            progress_bar_frame,
            text="🏗️ 4-Bosqichli 3D",
            bg="#2E3238",
            fg="#FFFFFF",
            hover_bg="#2E7D32",
            command=self.launch_multi_stage_3d
        )
        self.btn_multi_3d.pack(side=tk.RIGHT, padx=(4, 0))

        # YANGI: TREE DIAGRAM TUGMASI (Daraxt Diagrammasi)
        self.btn_tree = DarkButton(
            progress_bar_frame,
            text="🌳 Tree Diagram",
            bg="#2E3238",
            fg="#81C784",
            hover_bg="#1B5E20",
            command=self.open_tree_diagram
        )
        self.btn_tree.pack(side=tk.RIGHT, padx=(0, 4))

        # 3. Filtr tugmalari
        self.filter_bar = FilterBar(self.root, on_filter_selected=self.on_filter_changed)
        self.filter_bar.pack(fill=tk.X, padx=12, pady=(0, 6))

        # 4. Kartochkalar ro'yxati
        self.content_list = ContentList(self.root, on_delete_record=self.delete_item)
        self.content_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

    def open_tree_diagram(self):
        TreeDiagramWindow(self.root, self.db)

    def launch_multi_stage_3d(self):
        filled = self.db.get_filled_categories()
        all_cats = set(config.CATEGORIES)
        missing = sorted(list(all_cats - filled))

        if missing:
            missing_text = "\n• " + "\n• ".join(missing)
            msg = (
                f"DIQQAT: To'liq 4-bosqichli 3D progress renderini ochish uchun barcha "
                f"12 ta smeta formasi to'ldirilishi shart!\n\n"
                f"Hozir to'ldirilgan: {len(filled)} / {len(all_cats)}\n"
                f"Qolgan toifalar:{missing_text}"
            )
            messagebox.showwarning("Forma to'liq emas", msg)
            return

        all_records = self.db.get_records("Barchasi")
        self.visualizer_3d.show_multi_stage_3d(all_records)

    def delete_item(self, raw_id: int):
        self.db.delete_record(raw_id)
        self.refresh()

    def on_filter_changed(self, filter_name: str):
        self.current_filter = filter_name
        self.refresh()

    def refresh(self):
        items = self.db.get_records(self.current_filter)
        self.content_list.render_items(items)

        filled = self.db.get_filled_categories()
        total = len(config.CATEGORIES)
        self.lbl_checklist.config(text=f"To'ldirilgan toifalar: {len(filled)} / {total}")
        if len(filled) == total:
            self.lbl_checklist.config(fg="#81C784")
        else:
            self.lbl_checklist.config(fg="#FFD60A")