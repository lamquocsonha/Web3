"""
Repair corrupted SQLite database.
Usage: python repair_db.py
"""
import sqlite3, shutil, os, sys

DB_PATH = os.path.join('instance', 'unilab.db')

def repair():
    if not os.path.exists(DB_PATH):
        print(f"DB not found: {DB_PATH}")
        sys.exit(1)

    tmp = DB_PATH + '.clean'
    bak = DB_PATH + '.bak'

    # Backup original
    shutil.copy2(DB_PATH, bak)
    print(f"Backup saved: {bak}")

    # Rebuild clean copy
    old = sqlite3.connect(DB_PATH)
    new = sqlite3.connect(tmp)
    old.backup(new)
    new.execute('VACUUM;')
    new.close()
    old.close()

    # Replace original
    shutil.move(tmp, DB_PATH)

    # Verify
    conn = sqlite3.connect(DB_PATH)
    result = conn.execute('PRAGMA integrity_check;').fetchone()
    tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    counts = {}
    for (t,) in tables:
        try:
            c = conn.execute(f'SELECT count(*) FROM "{t}"').fetchone()[0]
            counts[t] = c
        except Exception:
            counts[t] = 'ERROR'
    conn.close()

    print(f"Integrity: {result[0]}")
    print("Tables:")
    for t, c in counts.items():
        print(f"  {t}: {c} rows")
    print("DB repaired!")

if __name__ == '__main__':
    repair()
