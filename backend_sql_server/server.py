#!/usr/bin/env python3
"""
TARAZ LOCALHOST SQL BACKEND SERVER (REST API + SQLITE3 RELATIONAL ENGINE)
=========================================================================
Runs out-of-the-box with standard Python 3 (zero pip dependencies required!).
Listens on http://0.0.0.0:8080 so both:
  - Android Emulator (via http://10.0.2.2:8080)
  - Physical Android Phone on Wi-Fi (via http://<PC_LAN_IP>:8080)
  - Desktop / Localhost (via http://127.0.0.1:8080)
can connect seamlessly to the relational SQL database (`taraz_finance.db`).
"""

import hashlib
import json
import os
import sqlite3
import time
import uuid
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DB_PATH = os.path.join(os.path.dirname(__file__), "taraz_finance.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")
PORT = 8080

INITIAL_CATEGORIES = [
    {"suffix": "housing", "type": "expense", "fa": "مسکن و اجاره", "en": "Housing & Rent", "icon": "home", "color": "#0B2D4A", "budget": 18000000},
    {"suffix": "food", "type": "expense", "fa": "خوراک و روزمره", "en": "Food & Groceries", "icon": "shopping_bag", "color": "#9B682F", "budget": 9500000},
    {"suffix": "transport", "type": "expense", "fa": "حمل‌ونقل و خودرو", "en": "Transport & Fuel", "icon": "directions_car", "color": "#4C5D5B", "budget": 3500000},
    {"suffix": "shopping", "type": "expense", "fa": "خرید و پوشاک", "en": "Shopping & Apparel", "icon": "card_giftcard", "color": "#AD8867", "budget": 5000000},
    {"suffix": "health", "type": "expense", "fa": "سلامت و درمان", "en": "Healthcare", "icon": "favorite", "color": "#6B7F7D", "budget": 3000000},
    {"suffix": "entertainment", "type": "expense", "fa": "تفریح و کافه", "en": "Dining & Leisure", "icon": "local_cafe", "color": "#582F0E", "budget": 2800000},
    {"suffix": "bills", "type": "expense", "fa": "قبوض و اشتراک‌ها", "en": "Utilities & Bills", "icon": "bolt", "color": "#284B63", "budget": 1500000},
    {"suffix": "salary", "type": "income", "fa": "حقوق و دستمزد", "en": "Monthly Salary", "icon": "work", "color": "#4C5D5B", "budget": 0},
    {"suffix": "freelance", "type": "income", "fa": "پروژه و فریلنس", "en": "Freelance & Projects", "icon": "computer", "color": "#0B2D4A", "budget": 0},
    {"suffix": "investment", "type": "income", "fa": "سود سرمایه‌گذاری", "en": "Investment Returns", "icon": "trending_up", "color": "#9B682F", "budget": 0},
]


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    conn = get_db()
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()


def hash_str(val: str) -> str:
    """BUG-04 FIX: Unicode-safe SHA-256 hash (supports Persian/IDN emails & passwords)."""
    return hashlib.sha256(val.encode("utf-8")).hexdigest()


def seed_user_if_needed(conn, uid: str, default_jy: int = 1405, default_jm: int = 8):
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM categories WHERE user_uid = ?", (uid,))
    if cur.fetchone()["cnt"] == 0:
        for c in INITIAL_CATEGORIES:
            cat_id = f"{uid}_{c['suffix']}"
            cur.execute(
                """INSERT INTO categories (id, user_uid, type, name_fa, name_en, icon, color, budget)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (cat_id, uid, c["type"], c["fa"], c["en"], c["icon"], c["color"], c["budget"]),
            )
        ym = f"{default_jy}-{default_jm:02d}"
        sample_txs = [
            (f"tx_{uuid.uuid4().hex[:10]}", uid, f"{uid}_salary", "income", 48000000, f"{ym}-01", "حقوق ماهانه شرکت", "Monthly Company Salary"),
            (f"tx_{uuid.uuid4().hex[:10]}", uid, f"{uid}_freelance", "income", 14000000, f"{ym}-10", "پروژه طراحی رابط کاربری", "UI/UX Project"),
            (f"tx_{uuid.uuid4().hex[:10]}", uid, f"{uid}_housing", "expense", 18000000, f"{ym}-02", "اجاره مسکن و شارژ ساختمان", "Apartment Rent"),
            (f"tx_{uuid.uuid4().hex[:10]}", uid, f"{uid}_food", "expense", 3200000, f"{ym}-04", "خرید مواد غذایی هفتگی", "Weekly Groceries"),
            (f"tx_{uuid.uuid4().hex[:10]}", uid, f"{uid}_transport", "expense", 1250000, f"{ym}-07", "بنزین و سرویس تاکسی", "Fuel & Commute"),
            (f"tx_{uuid.uuid4().hex[:10]}", uid, f"{uid}_bills", "expense", 1400000, f"{ym}-09", "قبض اینترنت و برق", "Internet & Electricity"),
            (f"tx_{uuid.uuid4().hex[:10]}", uid, f"{uid}_shopping", "expense", 4100000, f"{ym}-14", "خرید پوشاک پاییزی", "Apparel"),
            (f"tx_{uuid.uuid4().hex[:10]}", uid, f"{uid}_entertainment", "expense", 2100000, f"{ym}-18", "رستوران و سینما", "Dining & Leisure"),
        ]
        cur.executemany(
            """INSERT INTO transactions (id, user_uid, category_id, type, amount, shamsi_date, note_fa, note_en)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            sample_txs,
        )
        conn.commit()


class TarazSQLHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code: int, payload: dict):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_body(self) -> dict:
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw) if raw else {}

    def do_OPTIONS(self):
        self._send_json(200, {"ok": True})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/api/health":
            return self._send_json(200, {"status": "online", "engine": "SQLite3 Relational SQL", "db": DB_PATH})

        if path == "/api/sync":
            uid = qs.get("uid", ["guest_user"])[0]
            conn = get_db()
            try:
                cur = conn.cursor()
                cur.execute("SELECT * FROM users WHERE uid = ?", (uid,))
                user_row = cur.fetchone()
                if not user_row:
                    cur.execute(
                        "INSERT INTO users (uid, email, full_name, password_hash) VALUES (?, ?, ?, ?)",
                        (uid, f"{uid}@taraz.local", "Guest User", hash_str("guest")),
                    )
                    conn.commit()
                    seed_user_if_needed(conn, uid)
                    cur.execute("SELECT * FROM users WHERE uid = ?", (uid,))
                    user_row = cur.fetchone()

                cur.execute("SELECT * FROM categories WHERE user_uid = ? ORDER BY created_at ASC", (uid,))
                cats = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT * FROM transactions WHERE user_uid = ? ORDER BY shamsi_date DESC, created_at DESC", (uid,))
                txs = [dict(r) for r in cur.fetchall()]

                return self._send_json(200, {
                    "user": {
                        "uid": user_row["uid"],
                        "email": user_row["email"],
                        "full_name": user_row["full_name"],
                        "lang": user_row["lang"],
                        "pace_mode": user_row["pace_mode"],
                        "custom_daily_target": user_row["custom_daily_target"],
                    },
                    "categories": cats,
                    "transactions": txs,
                })
            finally:
                conn.close()

        return self._send_json(404, {"error": "Endpoint not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        body = self._read_body()
        conn = get_db()

        try:
            cur = conn.cursor()

            # 1. Authentication (Login / Signup / Guest)
            if path == "/api/auth":
                mode = body.get("mode", "login")
                if mode == "guest":
                    uid = "guest_user"
                    cur.execute("SELECT * FROM users WHERE uid = ?", (uid,))
                    row = cur.fetchone()
                    if not row:
                        cur.execute(
                            "INSERT INTO users (uid, email, full_name, password_hash) VALUES (?, ?, ?, ?)",
                            (uid, "guest@taraz.local", "کاربر مهمان • Guest", hash_str("guest")),
                        )
                        conn.commit()
                    seed_user_if_needed(conn, uid)
                    return self._send_json(200, {"uid": uid, "email": "guest@taraz.local", "full_name": "کاربر مهمان"})

                email = (body.get("email") or "").strip().lower()
                password = body.get("password") or ""
                full_name = (body.get("full_name") or "").strip() or email.split("@")[0]

                if not email or len(password) < 6:
                    return self._send_json(400, {"error": "Invalid email or password (< 6 chars)"})

                uid = "usr_" + hash_str(email)[:16]
                pass_hash = hash_str(password)

                cur.execute("SELECT * FROM users WHERE uid = ?", (uid,))
                existing = cur.fetchone()

                if existing:
                    if mode == "login" and existing["password_hash"] != pass_hash:
                        return self._send_json(401, {"error": "رمز عبور نادرست است • Incorrect password"})
                else:
                    cur.execute(
                        "INSERT INTO users (uid, email, full_name, password_hash) VALUES (?, ?, ?, ?)",
                        (uid, email, full_name, pass_hash),
                    )
                    conn.commit()
                    seed_user_if_needed(conn, uid)

                cur.execute("SELECT * FROM users WHERE uid = ?", (uid,))
                u = cur.fetchone()
                return self._send_json(200, {"uid": u["uid"], "email": u["email"], "full_name": u["full_name"]})

            # 2. Create or Update Category
            if path == "/api/categories":
                uid = body.get("user_uid", "guest_user")
                cat_id = body.get("id") or f"cat_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
                cat_type = body.get("type", "expense")
                name_fa = (body.get("name_fa") or "").strip()
                name_en = (body.get("name_en") or "").strip()
                icon = body.get("icon", "tag")
                color = body.get("color", "#0B2D4A")
                budget = int(body.get("budget", 0)) if cat_type == "expense" else 0

                cur.execute(
                    """INSERT INTO categories (id, user_uid, type, name_fa, name_en, icon, color, budget)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(id) DO UPDATE SET
                         type=excluded.type,
                         name_fa=excluded.name_fa,
                         name_en=excluded.name_en,
                         icon=excluded.icon,
                         color=excluded.color,
                         budget=excluded.budget""",
                    (cat_id, uid, cat_type, name_fa, name_en, icon, color, budget),
                )
                conn.commit()
                return self._send_json(200, {"ok": True, "id": cat_id})

            # 3. Create or Update Transaction (BUG-07 FIX: preserves bilingual notes independently)
            if path == "/api/transactions":
                uid = body.get("user_uid", "guest_user")
                tx_id = body.get("id") or f"tx_{int(time.time()*1000)}_{uuid.uuid4().hex[:6]}"
                cat_id = body.get("category_id")
                tx_type = body.get("type", "expense")
                amount = int(body.get("amount", 0))
                shamsi_date = body.get("shamsi_date")
                note_fa = body.get("note_fa", "")
                note_en = body.get("note_en", "")

                cur.execute(
                    """INSERT INTO transactions (id, user_uid, category_id, type, amount, shamsi_date, note_fa, note_en)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                       ON CONFLICT(id) DO UPDATE SET
                         category_id=excluded.category_id,
                         type=excluded.type,
                         amount=excluded.amount,
                         shamsi_date=excluded.shamsi_date,
                         note_fa=excluded.note_fa,
                         note_en=excluded.note_en""",
                    (tx_id, uid, cat_id, tx_type, amount, shamsi_date, note_fa, note_en),
                )
                conn.commit()
                return self._send_json(200, {"ok": True, "id": tx_id})

            # 4. Update User Pace Settings
            if path == "/api/settings":
                uid = body.get("user_uid", "guest_user")
                pace_mode = body.get("pace_mode", "auto")
                custom_daily = int(body.get("custom_daily_target", 0))
                lang = body.get("lang", "fa")
                cur.execute(
                    "UPDATE users SET pace_mode = ?, custom_daily_target = ?, lang = ? WHERE uid = ?",
                    (pace_mode, custom_daily, lang, uid),
                )
                conn.commit()
                return self._send_json(200, {"ok": True})

            # 5. Batch Import (JSON / CSV)
            if path == "/api/import":
                uid = body.get("user_uid", "guest_user")
                cats = body.get("categories", [])
                txs = body.get("transactions", [])
                for c in cats:
                    cur.execute(
                        """INSERT OR IGNORE INTO categories (id, user_uid, type, name_fa, name_en, icon, color, budget)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (c["id"], uid, c["type"], c["name_fa"], c["name_en"], c.get("icon", "tag"), c.get("color", "#0B2D4A"), int(c.get("budget", 0))),
                    )
                for t in txs:
                    cur.execute(
                        """INSERT OR REPLACE INTO transactions (id, user_uid, category_id, type, amount, shamsi_date, note_fa, note_en)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                        (t["id"], uid, t["category_id"], t["type"], int(t["amount"]), t["shamsi_date"], t.get("note_fa", ""), t.get("note_en", "")),
                    )
                conn.commit()
                return self._send_json(200, {"ok": True, "imported_txs": len(txs)})

            return self._send_json(404, {"error": "Unknown POST endpoint"})
        finally:
            conn.close()

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)
        conn = get_db()

        try:
            cur = conn.cursor()

            # Delete Transaction
            if path == "/api/transactions":
                tx_id = qs.get("id", [""])[0]
                uid = qs.get("uid", ["guest_user"])[0]
                cur.execute("DELETE FROM transactions WHERE id = ? AND user_uid = ?", (tx_id, uid))
                conn.commit()
                return self._send_json(200, {"ok": True})

            # Delete Category (BUG-10 FIX: Prevents deleting the last category of a type & safely reassigns SQL foreign keys)
            if path == "/api/categories":
                cat_id = qs.get("id", [""])[0]
                uid = qs.get("uid", ["guest_user"])[0]

                cur.execute("SELECT * FROM categories WHERE id = ? AND user_uid = ?", (cat_id, uid))
                target = cur.fetchone()
                if not target:
                    return self._send_json(404, {"error": "Category not found"})

                cur.execute("SELECT * FROM categories WHERE user_uid = ? AND type = ? AND id != ?", (uid, target["type"], cat_id))
                remaining = cur.fetchall()
                if len(remaining) == 0:
                    return self._send_json(400, {"error": "Cannot delete the last remaining category of this type"})

                fallback_id = remaining[0]["id"]
                cur.execute("UPDATE transactions SET category_id = ? WHERE category_id = ? AND user_uid = ?", (fallback_id, cat_id, uid))
                cur.execute("DELETE FROM categories WHERE id = ? AND user_uid = ?", (cat_id, uid))
                conn.commit()
                return self._send_json(200, {"ok": True, "reassigned_to": fallback_id})

            return self._send_json(404, {"error": "Unknown DELETE endpoint"})
        finally:
            conn.close()


if __name__ == "__main__":
    init_db()
    print("=" * 68)
    print(f" TARAZ SQL BACKEND SERVER RUNNING ON PORT {PORT}")
    print(f" SQLite Database File : {DB_PATH}")
    print(f" Local PC URL         : http://127.0.0.1:{PORT}/api/health")
    print(f" Android Emulator URL : http://10.0.2.2:{PORT}")
    print("=" * 68)
    server = HTTPServer(("0.0.0.0", PORT), TarazSQLHandler)
    server.serve_forever()
