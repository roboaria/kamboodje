#!/usr/bin/env python3
import http.server
import socketserver
import json
import sqlite3
import os
import hashlib
import uuid

PORT = 8080
DB_PATH = os.path.join(os.path.dirname(__file__), "taraz_finance.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def init_db():
    conn = get_db()
    conn.execute("CREATE TABLE IF NOT EXISTS users (uid TEXT PRIMARY KEY, email TEXT, full_name TEXT, password_hash TEXT);")
    conn.execute("CREATE TABLE IF NOT EXISTS categories (id TEXT PRIMARY KEY, user_uid TEXT, type TEXT, name_fa TEXT, name_en TEXT, icon TEXT, color TEXT, budget INTEGER);")
    conn.execute("CREATE TABLE IF NOT EXISTS transactions (id TEXT PRIMARY KEY, user_uid TEXT, category_id TEXT, type TEXT, amount INTEGER, shamsi_date TEXT, note_fa TEXT, note_en TEXT);")
    conn.commit()
    conn.close()

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if "/api/health" in self.path:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "online", "sql": "SQLite3 relational active"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    init_db()
    print(f"Taraz Localhost SQL Backend running on port {PORT}...")
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        httpd.serve_forever()
