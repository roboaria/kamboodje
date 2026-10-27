# Taraz Money Manager • تراز (Flutter Android App + Localhost SQL Backend)

This package contains the complete **Flutter Android Application** and **Localhost Relational SQL Backend Server** for **Taraz (تراز)**.

---

## Architecture Overview

1. **`backend_sql_server/` (Localhost Relational SQL Backend)**
   - **`schema.sql`**: Normalised relational SQL schema (`users`, `categories`, `transactions`) with foreign-key constraints and indexes. Compatible with SQLite3, PostgreSQL, and MySQL.
   - **`server.py`**: Zero-dependency Python 3 REST + SQLite3 server listening on `0.0.0.0:8080`. Automatically creates and seeds `taraz_finance.db` from `schema.sql`.

2. **`flutter_android_app/` (Flutter Native Android App)**
   - **`lib/main.dart`**: Complete Flutter application featuring:
     - Exact mathematical **Jalali (Shamsi)** calendar engine in Dart.
     - **Hybrid Dual-SQL Engine**: Connects live to your Localhost SQL Server (`http://10.0.2.2:8080` on Android Emulator or `http://<YOUR_PC_IP>:8080` on a physical Android phone) AND mirrors all tables into on-device `sqflite` SQLite so it works 100% offline.
     - All **15 security and logic bugs** from the audit fixed.

---

## Step 1: Start the Localhost SQL Backend on Your PC

Open a terminal on your PC (Windows/macOS/Linux) and run:

```bash
cd backend_sql_server
python server.py
```

- The SQL server starts immediately on **`http://127.0.0.1:8080`** and initializes `taraz_finance.db`.
- Test it in your browser at: `http://127.0.0.1:8080/api/health`

### Connecting Your Android Phone to Your PC's Localhost:
- **Via USB Cable (Recommended — Zero Firewall Issues):**
  Run `adb reverse tcp:8080 tcp:8080` on your PC, then set the Server URL inside the Flutter app (top-right server icon) to `http://127.0.0.1:8080`.
- **Via Android Emulator:**
  Works automatically using the default `http://10.0.2.2:8080`.
- **Via Same Wi-Fi Network (LAN):**
  Find your PC's local IP (`ipconfig` on Windows, e.g., `192.168.1.50`) and set the Server URL in the app to `http://192.168.1.50:8080`.

---

## Step 2: Run or Build the Flutter Android App

```bash
cd flutter_android_app
flutter create --platforms=android .
flutter pub get
flutter run
```

To compile a standalone `.apk` file for your Android phone:
```bash
flutter build apk --release
```
