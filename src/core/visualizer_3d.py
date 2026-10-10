"""Barcha qurilish elementlari va 4-bosqichli progress evolyutsiyasi uchun to'g'rilangan 3D BIM generator."""
import sys
import os
import json
import tempfile
import subprocess

class Visualizer3D:
    def show_item_3d(self, item: dict):
        self._spawn_process({"mode": "single", "data": item})

    def show_multi_stage_3d(self, records: list):
        self._spawn_process({"mode": "multi_stage", "data": records})

    def _spawn_process(self, payload: dict):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False)
            temp_path = f.name
        subprocess.Popen([sys.executable, os.path.abspath(__file__), temp_path])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(0)

    json_file = sys.argv[1]
    try:
        with open(json_file, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except Exception:
        sys.exit(1)
    finally:
        if os.path.exists(json_file):
            try:
                os.remove(json_file)
            except Exception:
                pass

    import pyvista as pv
    import numpy as np

    pv.set_plot_theme("document")
    mode = payload.get("mode", "single")

    plotter = pv.Plotter(
        title="3D BIM Qurilish Progressi — Hisob Palatasi Auditi",
        window_size=[1300, 800]
    )
    plotter.set_background("#F8F9FA", top="#FFFFFF")
    plotter.add_axes(color="#24292F")

    def _get_f(d: dict, k: str, default: float) -> float:
        try:
            return float(str(d.get(k, default)).replace(" ", "").replace(",", ".").split()[0])
        except (ValueError, TypeError, IndexError):
            return default

    # =========================================================================
    # REJIM 1: 4-BOSQICHLI QURILISH EVOLYUTSIYASI (YANGILANGAN)
    # =========================================================================
    if mode == "multi_stage":
        records = payload.get("data", [])
        b_rec = next((r for r in records if "Bino" in r.get("category", "")), None)
        attrs = b_rec.get("attributes", {}) if b_rec else {}

        w = max(6.0, _get_f(attrs, "Bino kengligi (m)", 14.0))
        d = max(6.0, _get_f(attrs, "Bino uzunligi (m)", 20.0))
        h_total = max(3.2, _get_f(attrs, "Bino balandligi (m)", 16.0))
        floors = max(1, int(round(h_total / 3.2)))
        floor_h = h_total / floors

        # Bosqichlar oralig'i
        gap = w + 9.0

        # Koordinatalar (1-bosqich chapda, 4-bosqich o'ngda)
        ox1 = 0.0
        ox2 = gap
        ox3 = gap * 2.0
        ox4 = gap * 3.0

        # --- YAGONA ZAMIN / QURILISH PLATFORMASI (GROUND PODIUM) ---
        podium_x_min = -6.0
        podium_x_max = ox4 + w + 6.0
        podium_y_min = -6.0
        podium_y_max = d + 8.0

        # Asosiy yer sathi
        plotter.add_mesh(
            pv.Box(bounds=(podium_x_min, podium_x_max, podium_y_min, podium_y_max, -0.8, -0.2)),
            color="#E9ECEF",
            show_edges=True,
            edge_color="#CED4DA"
        )
        # Qurilish chegarasi chiziqlari (yo'laklar)
        plotter.add_mesh(
            pv.Box(bounds=(podium_x_min, podium_x_max, podium_y_min, podium_y_min + 1.5, -0.2, -0.18)),
            color="#ADB5BD"
        )

        # ----------------------------------------------------
        # 1-BOSQICH: POYDEVOR, QOLIPLAR VA ARMATURA KARKASI
        # ----------------------------------------------------
        # Kotlovan chuqurligi va qum yostig'i
        plotter.add_mesh(pv.Box(bounds=(ox1 - 1.0, ox1 + w + 1.0, -1.0, d + 1.0, -0.6, -0.2)), color="#D4A373")
        # Poydevor monolit plitasi
        plotter.add_mesh(pv.Box(bounds=(ox1, ox1 + w, 0.0, d, -0.2, 0.4)), color="#495057", show_edges=True)
        # Qoliplar (DOKA metall shchitlari perimetr bo'ylab)
        plotter.add_mesh(pv.Box(bounds=(ox1 - 0.2, ox1 + w + 0.2, -0.2, 0.0, -0.2, 0.6)), color="#C62828", show_edges=True)
        plotter.add_mesh(pv.Box(bounds=(ox1 - 0.2, ox1 + w + 0.2, d, d + 0.2, -0.2, 0.6)), color="#C62828", show_edges=True)
        plotter.add_mesh(pv.Box(bounds=(ox1 - 0.2, 0.0, 0.0, d, -0.2, 0.6)), color="#C62828", show_edges=True)
        plotter.add_mesh(pv.Box(bounds=(ox1 + w, ox1 + w + 0.2, 0.0, d, -0.2, 0.6)), color="#C62828", show_edges=True)

        # 5 qavatli bino ustunlari uchun yerdan ko'tarilgan armatura karkaslari
        col_xs = [0.8, w / 2.0, w - 0.8]
        col_ys = [0.8, d / 2.0, d - 0.8]
        for cx in col_xs:
            for cy in col_ys:
                plotter.add_mesh(
                    pv.Box(bounds=(ox1 + cx - 0.25, ox1 + cx + 0.25, cy - 0.25, cy + 0.25, 0.4, 3.2)),
                    color="#212529",
                    show_edges=True,
                    edge_color="#6C757D"
                )

        # Qum, shag'al va sement ombori
        plotter.add_mesh(pv.Cone(center=(ox1 + w + 3.0, 4.0, 0.4), direction=(0, 0, 1), height=1.6, radius=2.0), color="#E0A96D")
        plotter.add_mesh(pv.Cone(center=(ox1 + w + 3.0, 9.5, 0.4), direction=(0, 0, 1), height=1.6, radius=2.0), color="#6C757D")
        for si in range(6):
            plotter.add_mesh(pv.Box(bounds=(ox1 + w + 2.0, ox1 + w + 3.2, 13.0 + si * 0.7, 13.6 + si * 0.7, -0.2, 0.4)), color="#90A4AE", show_edges=True)

        plotter.add_point_labels([[ox1 + w / 2.0, d / 2.0, 4.5]], ["1-BOSQICH:\nPoydevor, Qolip & Armatura"], text_color="#C62828", font_size=11, bold=True, shape=None)

        # ----------------------------------------------------
        # 2-BOSQICH: TEMIR-BETON MONOLIT KARKAS
        # ----------------------------------------------------
        plotter.add_mesh(pv.Box(bounds=(ox2, ox2 + w, 0.0, d, -0.2, 0.4)), color="#495057", show_edges=True)
        col_w = 0.50
        slab_th = 0.30

        for fl in range(floors):
            z_f = 0.4 + fl * floor_h
            z_c = 0.4 + (fl + 1) * floor_h
            # Orayopma plitasi
            plotter.add_mesh(pv.Box(bounds=(ox2 - 0.1, ox2 + w + 0.1, -0.1, d + 0.1, z_c - slab_th, z_c)), color="#ADB5BD", show_edges=True)
            # 9 ta yuk ko'taruvchi monolit ustunlar
            for cx in col_xs:
                for cy in col_ys:
                    plotter.add_mesh(pv.Box(bounds=(ox2 + cx - col_w/2, ox2 + cx + col_w/2, cy - col_w/2, cy + col_w/2, z_f, z_c - slab_th)), color="#6C757D", show_edges=True)

        plotter.add_point_labels([[ox2 + w / 2.0, d / 2.0, h_total + 1.8]], ["2-BOSQICH:\nMonolit Karkas Ustunlari"], text_color="#E65100", font_size=11, bold=True, shape=None)

        # ----------------------------------------------------
        # 3-BOSQICH: G'ISHT TERIMI VA DEVORLAR
        # ----------------------------------------------------
        plotter.add_mesh(pv.Box(bounds=(ox3, ox3 + w, 0.0, d, -0.2, 0.4)), color="#495057", show_edges=True)
        for fl in range(floors):
            z_f = 0.4 + fl * floor_h
            z_c = 0.4 + (fl + 1) * floor_h
            plotter.add_mesh(pv.Box(bounds=(ox3 - 0.1, ox3 + w + 0.1, -0.1, d + 0.1, z_c - slab_th, z_c)), color="#ADB5BD", show_edges=True)
            for cx in col_xs:
                for cy in col_ys:
                    plotter.add_mesh(pv.Box(bounds=(ox3 + cx - col_w/2, ox3 + cx + col_w/2, cy - col_w/2, cy + col_w/2, z_f, z_c - slab_th)), color="#6C757D", show_edges=True)

            # Devorlar (Oyna va eshik joylari bo'sh qoldirilgan)
            w_th = 0.30
            for y_min, y_max in [(0.0, w_th), (d - w_th, d)]:
                plotter.add_mesh(pv.Box(bounds=(ox3, ox3 + w, y_min, y_max, z_f, z_f + 0.9)), color="#C84B31", show_edges=True)
                plotter.add_mesh(pv.Box(bounds=(ox3, ox3 + w, y_min, y_max, z_c - slab_th - 0.6, z_c - slab_th)), color="#C84B31", show_edges=True)
            for x_min, x_max in [(0.0, w_th), (w - w_th, w)]:
                plotter.add_mesh(pv.Box(bounds=(ox3 + x_min, ox3 + x_max, 0.0, d, z_f, z_c - slab_th)), color="#C84B31", show_edges=True)

        plotter.add_point_labels([[ox3 + w / 2.0, d / 2.0, h_total + 1.8]], ["3-BOSQICH:\nG'isht Devorlari Terimi"], text_color="#1565C0", font_size=11, bold=True, shape=None)

        # ----------------------------------------------------
        # 4-BOSQICH: TO'LIQ BITGAN BINO (FASAD, ROM, TOM)
        # ----------------------------------------------------
        plotter.add_mesh(pv.Box(bounds=(ox4, ox4 + w, 0.0, d, -0.2, 0.4)), color="#495057", show_edges=True)
        for fl in range(floors):
            z_f = 0.4 + fl * floor_h
            z_c = 0.4 + (fl + 1) * floor_h
            plotter.add_mesh(pv.Box(bounds=(ox4 - 0.1, ox4 + w + 0.1, -0.1, d + 0.1, z_c - slab_th, z_c)), color="#ADB5BD", show_edges=True)
            for cx in col_xs:
                for cy in col_ys:
                    plotter.add_mesh(pv.Box(bounds=(ox4 + cx - col_w/2, ox4 + cx + col_w/2, cy - col_w/2, cy + col_w/2, z_f, z_c - slab_th)), color="#6C757D", show_edges=True)

            w_th = 0.30
            # Fasad va Oynalar
            for y_min, y_max in [(0.0, w_th), (d - w_th, d)]:
                plotter.add_mesh(pv.Box(bounds=(ox4, ox4 + w, y_min, y_max, z_f, z_f + 0.9)), color="#D7CCC8", show_edges=True)
                plotter.add_mesh(pv.Box(bounds=(ox4, ox4 + w, y_min, y_max, z_c - slab_th - 0.6, z_c - slab_th)), color="#D7CCC8", show_edges=True)
                for wx in [w * 0.25, w * 0.5, w * 0.75]:
                    if fl == 0 and abs(wx - w/2.0) < 1.0 and y_min == 0.0:
                        continue
                    plotter.add_mesh(pv.Box(bounds=(ox4 + wx - 0.8, ox4 + wx + 0.8, y_min - 0.02, y_max + 0.02, z_f + 0.9, z_f + 2.4)), color="#212529", show_edges=True)
                    plotter.add_mesh(pv.Box(bounds=(ox4 + wx - 0.72, ox4 + wx + 0.72, (y_min+y_max)/2.0 - 0.01, (y_min+y_max)/2.0 + 0.01, z_f + 0.98, z_f + 2.32)), color="#4FC3F7", opacity=0.6)
            for x_min, x_max in [(0.0, w_th), (w - w_th, w)]:
                plotter.add_mesh(pv.Box(bounds=(ox4 + x_min, ox4 + x_max, 0.0, d, z_f, z_c - slab_th)), color="#D7CCC8", show_edges=True)

        # Asosiy kirish eshigi
        plotter.add_mesh(pv.Box(bounds=(ox4 + w/2.0 - 1.2, ox4 + w/2.0 + 1.2, -0.06, 0.35, 0.4, 2.8)), color="#3E2723", show_edges=True)

        # Valmali tom
        overhang = 0.80
        roof_h = 2.60
        z_base = 0.4 + h_total
        z_top = z_base + roof_h
        ridge_len = max(3.0, d - w * 0.6)
        r_half = ridge_len / 2.0
        x_mid = ox4 + w / 2.0
        y_mid = d / 2.0

        plotter.add_mesh(pv.Box(bounds=(ox4 - overhang, ox4 + w + overhang, -overhang, d + overhang, z_base - 0.2, z_base)), color="#2B2D42", show_edges=True)
        verts = np.array([
            [ox4 - overhang, -overhang, z_base],
            [ox4 + w + overhang, -overhang, z_base],
            [ox4 + w + overhang, d + overhang, z_base],
            [ox4 - overhang, d + overhang, z_base],
            [x_mid, y_mid - r_half, z_top],
            [x_mid, y_mid + r_half, z_top]
        ])
        faces = np.hstack([[3, 0, 1, 4], [3, 2, 3, 5], [4, 1, 2, 5, 4], [4, 3, 0, 4, 5]])
        plotter.add_mesh(pv.PolyData(verts, faces), color="#8B1E1E", show_edges=True, edge_color="#4A0E0E")
        plotter.add_mesh(pv.Cylinder(center=(x_mid, y_mid, z_top), direction=(0, 1, 0), radius=0.10, height=ridge_len), color="#3A0A0A")

        plotter.add_point_labels([[ox4 + w / 2.0, d / 2.0, z_top + 1.8]], ["4-BOSQICH:\nTo'liq Bitgan Bino"], text_color="#2E7D32", font_size=11, bold=True, shape=None)

        # --- ARXITEKTURA KAMERA SOZLAMASI (1 -> 4 TO'G'RI TARTIB) ---
        total_span = ox4 + w
        center_x = total_span / 2.0
        center_y = d / 2.0
        center_z = h_total / 2.0

        plotter.camera_position = [
            (center_x, -d * 2.8, h_total * 2.2),  # Kamera nuqtasi: oldinda va tepada
            (center_x, center_y, center_z * 0.8), # Markazga qarash
            (0, 0, 1)                             # Z o'qi mutlaq vertikal
        ]

        plotter.add_text("HISOB PALATASI: QURILISH BOSQICHLARI AUDITI (1 -> 4)", position="upper_left", font_size=12, color="#1F2328")

    # =========================================================================
    # REJIM 2: YAGONA ELEMENT RENDERI
    # =========================================================================
    else:
        item = payload.get("data", {})
        category = item.get("category", "")
        attrs = item.get("attributes", {})
        status = item.get("status", "Yashil")
        item_id = item.get("id", "N/A")

        if "Bino" in category:
            w = max(6.0, _get_f(attrs, "Bino kengligi (m)", 14.0))
            d = max(6.0, _get_f(attrs, "Bino uzunligi (m)", 20.0))
            h_total = max(3.2, _get_f(attrs, "Bino balandligi (m)", 16.0))
            floors = max(1, int(round(h_total / 3.2)))
            floor_h = h_total / floors

            plotter.add_mesh(pv.Box(bounds=(-2, w + 2, -2, d + 2, -0.6, 0.0)), color="#E9ECEF", show_edges=True)
            col_w = 0.50
            slab_th = 0.30
            for fl in range(floors):
                z_f = fl * floor_h
                z_c = (fl + 1) * floor_h
                plotter.add_mesh(pv.Box(bounds=(-0.1, w + 0.1, -0.1, d + 0.1, z_c - slab_th, z_c)), color="#ADB5BD", show_edges=True)
                for cx in [0.8, w/2, w - 0.8]:
                    for cy in [0.8, d/2, d - 0.8]:
                        plotter.add_mesh(pv.Box(bounds=(cx - col_w/2, cx + col_w/2, cy - col_w/2, cy + col_w/2, z_f, z_c - slab_th)), color="#6C757D", show_edges=True)
                w_th = 0.30
                for y_min, y_max in [(0.0, w_th), (d - w_th, d)]:
                    plotter.add_mesh(pv.Box(bounds=(0, w, y_min, y_max, z_f, z_f + 0.9)), color="#D7CCC8", show_edges=True)
                    plotter.add_mesh(pv.Box(bounds=(0, w, y_min, y_max, z_c - slab_th - 0.6, z_c - slab_th)), color="#D7CCC8", show_edges=True)
                    for wx in [w * 0.25, w * 0.5, w * 0.75]:
                        if fl == 0 and abs(wx - w/2.0) < 1.0 and y_min == 0.0:
                            continue
                        plotter.add_mesh(pv.Box(bounds=(wx - 0.8, wx + 0.8, y_min - 0.02, y_max + 0.02, z_f + 0.9, z_f + 2.4)), color="#212529", show_edges=True)
                        plotter.add_mesh(pv.Box(bounds=(wx - 0.72, wx + 0.72, (y_min+y_max)/2.0 - 0.01, (y_min+y_max)/2.0 + 0.01, z_f + 0.98, z_f + 2.32)), color="#4FC3F7", opacity=0.6)
                for x_min, x_max in [(0.0, w_th), (w - w_th, w)]:
                    plotter.add_mesh(pv.Box(bounds=(x_min, x_max, 0, d, z_f, z_c - slab_th)), color="#D7CCC8", show_edges=True)

            plotter.add_mesh(pv.Box(bounds=(w/2.0 - 1.2, w/2.0 + 1.2, -0.06, 0.35, 0.0, 2.8)), color="#3E2723", show_edges=True)
            overhang = 0.80
            z_top = h_total + 2.60
            ridge_len = max(3.0, d - w * 0.6)
            verts = np.array([
                [-overhang, -overhang, h_total],
                [w + overhang, -overhang, h_total],
                [w + overhang, d + overhang, h_total],
                [-overhang, d + overhang, h_total],
                [w/2.0, d/2.0 - ridge_len/2.0, z_top],
                [w/2.0, d/2.0 + ridge_len/2.0, z_top]
            ])
            faces = np.hstack([[3, 0, 1, 4], [3, 2, 3, 5], [4, 1, 2, 5, 4], [4, 3, 0, 4, 5]])
            plotter.add_mesh(pv.PolyData(verts, faces), color="#8B1E1E", show_edges=True)
        elif "G'isht" in category:
            for row in range(9):
                z = row * 0.075
                for col in range(7):
                    plotter.add_mesh(pv.Box(bounds=(col*0.26, col*0.26 + 0.25, 0, 0.12, z, z + 0.065)), color="#D03B1E", show_edges=True)
        elif "Armatura" in category:
            for cx, cy in [(0.1, 0.1), (0.5, 0.1), (0.5, 0.5), (0.1, 0.5)]:
                plotter.add_mesh(pv.Cylinder(center=(cx, cy, 2.0), direction=(0, 0, 1), radius=0.015, height=4.0), color="#343A40")
        else:
            plotter.add_mesh(pv.Box(bounds=(0, 2, 0, 2, 0, 2)), color="#1976D2", show_edges=True)

        tot_txt = f"{item.get('total_cost', 0):,.0f}".replace(",", " ")
        plotter.add_text(f"{item_id} | {category}\nHolat: {status}\nJami: {tot_txt} UZS", position="upper_left", font_size=11, color="#1F2328")

    plotter.enable_eye_dome_lighting()
    plotter.show()