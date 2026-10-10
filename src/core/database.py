"""SQLite bazasi - Yangi to'liq audit sxemasi bilan."""
import sqlite3
import json
from datetime import datetime
import config

class Database:
    def __init__(self):
        self.db_path = config.DB_PATH
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS construction_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL UNIQUE,
                    sub_type TEXT,
                    unit TEXT,
                    quantity REAL DEFAULT 0,
                    unit_price REAL DEFAULT 0,
                    delivery_cost REAL DEFAULT 0,
                    labor_cost REAL DEFAULT 0,
                    extra_cost REAL DEFAULT 0,
                    total_cost REAL DEFAULT 0,
                    allocated_budget REAL DEFAULT 0,
                    remaining_budget REAL DEFAULT 0,
                    affordable_quantity REAL DEFAULT 0,
                    status TEXT NOT NULL,
                    attributes_json TEXT,
                    created_at TEXT NOT NULL,
                    market_price REAL DEFAULT 0,
                    damage_amount REAL DEFAULT 0,
                    audit_notes TEXT
                )
            """)
            conn.commit()

    def upsert_record(self, data: dict):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO construction_records (
                    category, sub_type, unit, quantity, unit_price,
                    delivery_cost, labor_cost, extra_cost, total_cost,
                    allocated_budget, remaining_budget, affordable_quantity,
                    status, attributes_json, created_at,
                    market_price, damage_amount, audit_notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(category) DO UPDATE SET
                    sub_type = excluded.sub_type,
                    unit = excluded.unit,
                    quantity = excluded.quantity,
                    unit_price = excluded.unit_price,
                    delivery_cost = excluded.delivery_cost,
                    labor_cost = excluded.labor_cost,
                    extra_cost = excluded.extra_cost,
                    total_cost = excluded.total_cost,
                    allocated_budget = excluded.allocated_budget,
                    remaining_budget = excluded.remaining_budget,
                    affordable_quantity = excluded.affordable_quantity,
                    status = excluded.status,
                    attributes_json = excluded.attributes_json,
                    created_at = excluded.created_at,
                    market_price = excluded.market_price,
                    damage_amount = excluded.damage_amount,
                    audit_notes = excluded.audit_notes
            """, (
                data.get("category"),
                data.get("sub_type", ""),
                data.get("unit", ""),
                data.get("quantity", 0.0),
                data.get("unit_price", 0.0),
                data.get("delivery_cost", 0.0),
                data.get("labor_cost", 0.0),
                data.get("extra_cost", 0.0),
                data.get("total_cost", 0.0),
                data.get("allocated_budget", 0.0),
                data.get("remaining_budget", 0.0),
                data.get("affordable_quantity", 0.0),
                data.get("status", "Yashil"),
                json.dumps(data.get("attributes", {}), ensure_ascii=False),
                created_at,
                data.get("market_price", 0.0),
                data.get("damage_amount", 0.0),
                data.get("audit_notes", "")
            ))
            conn.commit()

    def delete_record(self, raw_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM construction_records WHERE id = ?", (raw_id,))
            conn.commit()

    def get_record_by_category(self, category: str):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM construction_records WHERE category = ?", (category,))
            r = cursor.fetchone()
            if not r:
                return None
            return {
                "raw_id": r[0],
                "id": f"UZ-BLD-{r[0]:03d}",
                "category": r[1],
                "sub_type": r[2],
                "unit": r[3],
                "quantity": r[4],
                "unit_price": r[5],
                "delivery_cost": r[6],
                "labor_cost": r[7],
                "extra_cost": r[8],
                "total_cost": r[9],
                "allocated_budget": r[10],
                "remaining_budget": r[11],
                "affordable_quantity": r[12],
                "status": r[13],
                "attributes": json.loads(r[14]) if r[14] else {},
                "created_at": r[15],
                "market_price": r[16],
                "damage_amount": r[17],
                "audit_notes": r[18]
            }

    def get_filled_categories(self) -> set:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM construction_records")
            rows = cursor.fetchall()
            return {r[0] for r in rows}

    def get_records(self, filter_status="Barchasi"):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM construction_records"
            params = ()
            if filter_status != "Barchasi":
                query += " WHERE status = ?"
                params = (filter_status,)
            query += " ORDER BY id DESC"

            cursor.execute(query, params)
            rows = cursor.fetchall()

            records = []
            for r in rows:
                records.append({
                    "raw_id": r[0],
                    "id": f"UZ-BLD-{r[0]:03d}",
                    "category": r[1],
                    "sub_type": r[2],
                    "unit": r[3],
                    "quantity": r[4],
                    "unit_price": r[5],
                    "delivery_cost": r[6],
                    "labor_cost": r[7],
                    "extra_cost": r[8],
                    "total_cost": r[9],
                    "allocated_budget": r[10],
                    "remaining_budget": r[11],
                    "affordable_quantity": r[12],
                    "status": r[13],
                    "attributes": json.loads(r[14]) if r[14] else {},
                    "created_at": r[15],
                    "market_price": r[16],
                    "damage_amount": r[17],
                    "audit_notes": r[18]
                })
            return records