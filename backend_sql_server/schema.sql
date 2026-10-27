-- ============================================================================
-- TARAZ MONEY MANAGER • تراز (SQL RELATIONAL DATABASE SCHEMA)
-- Compatible with SQLite3, PostgreSQL, and MySQL
-- ============================================================================

PRAGMA foreign_keys = ON;

-- 1. Users Table (Unicode-safe UID, SHA-256 Password Hash, Budget Pacing Config)
CREATE TABLE IF NOT EXISTS users (
    uid TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    full_name TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    lang TEXT DEFAULT 'fa' CHECK(lang IN ('fa', 'en')),
    pace_mode TEXT DEFAULT 'auto' CHECK(pace_mode IN ('auto', 'custom')),
    custom_daily_target INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Categories Table (Bilingual Farsi/English, Expense/Income, Monthly Budget)
CREATE TABLE IF NOT EXISTS categories (
    id TEXT PRIMARY KEY,
    user_uid TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
    name_fa TEXT NOT NULL,
    name_en TEXT NOT NULL,
    icon TEXT DEFAULT 'tag',
    color TEXT DEFAULT '#0B2D4A',
    budget INTEGER DEFAULT 0 CHECK(budget >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uid) REFERENCES users(uid) ON DELETE CASCADE
);

-- 3. Transactions Table (Shamsi Date YYYY-MM-DD, Bilingual Notes preserved independently)
CREATE TABLE IF NOT EXISTS transactions (
    id TEXT PRIMARY KEY,
    user_uid TEXT NOT NULL,
    category_id TEXT NOT NULL,
    type TEXT NOT NULL CHECK(type IN ('expense', 'income')),
    amount INTEGER NOT NULL CHECK(amount > 0),
    shamsi_date TEXT NOT NULL, -- Format: YYYY-MM-DD (e.g., 1405-08-05)
    note_fa TEXT DEFAULT '',
    note_en TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_uid) REFERENCES users(uid) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_tx_user_date ON transactions(user_uid, shamsi_date);
CREATE INDEX IF NOT EXISTS idx_cat_user_type ON categories(user_uid, type);
