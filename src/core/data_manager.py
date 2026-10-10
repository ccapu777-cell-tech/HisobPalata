"""Data handling and filtering logic."""

class DataManager:
    def __init__(self):
        # Initial mock items matching Hisob Palatasi audit categories
        self._items = [
            {"id": "HP-101", "title": "Boshqarma hisoboti tekshiruvi", "status": "Qizil", "date": "2026-10-01"},
            {"id": "HP-102", "title": "Xaridlar monitoringi auditi", "status": "Sariq", "date": "2026-10-03"},
            {"id": "HP-103", "title": "Ish haqi fondi taqsimoti", "status": "Yashil", "date": "2026-10-04"},
            {"id": "HP-104", "title": "Subsidiyalar auditi tahlili", "status": "Qizil", "date": "2026-10-05"},
            {"id": "HP-105", "title": "Moddiy aktivlar inventarizatsiyasi", "status": "Yashil", "date": "2026-10-06"},
            {"id": "HP-106", "title": "Qurilish obyektlari sarf-xarajati", "status": "Sariq", "date": "2026-10-07"},
        ]

    def get_items(self, filter_name="Barchasi"):
        """Return items filtered by category."""
        if filter_name == "Barchasi":
            return self._items
        return [item for item in self._items if item["status"] == filter_name]