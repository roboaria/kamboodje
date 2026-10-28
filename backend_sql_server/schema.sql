PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    uid TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    lang TEXT DEFAULT 'fa',
    pace_mode TEXT DEFAULT 'auto',
    custom_daily_target INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    user_uid TEXT NOT NULL,
    type TEXT NOT NULL,
    name_fa TEXT NOT NULL,
    name_en TEXT NOT NULL,
    icon TEXT DEFAULT 'ph-tag',
    color TEXT DEFAULT '#0B2D4A',
    budget INTEGER DEFAULT 0,
    FOREIGN KEY (user_uid) REFERENCES users(uid) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    user_uid TEXT NOT NULL,
    category_id TEXT NOT NULL,
    type TEXT NOT NULL,
    amount INTEGER NOT NULL,
    shamsi_date TEXT NOT NULL,
    note_fa TEXT DEFAULT '',
    note_en TEXT DEFAULT '',
    FOREIGN KEY (user_uid) REFERENCES users(uid) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);
