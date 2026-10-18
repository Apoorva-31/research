import sqlite3
from pathlib import Path

def setup_conflict_environment():
    # 1. Ensure directories exist
    Path("data").mkdir(exist_ok=True)
    Path("documents/change_notices").mkdir(parents=True, exist_ok=True)
    
    # 2. Populate SQLite Database with Outdated Legacy Facts
    db_path = "data/event_memory.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venues (
            venue_id TEXT PRIMARY KEY,
            capacity INTEGER,
            emergency_exit_rules TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            event_id TEXT PRIMARY KEY,
            date TEXT,
            attendance INTEGER,
            venue_id TEXT,
            status TEXT,
            FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
        )
    """)
    
    # Insert conflicting legacy data (DB says capacity 300, but actual attendance is 260)
    cursor.execute("REPLACE INTO venues (venue_id, capacity, emergency_exit_rules) VALUES (?, ?, ?)",
                   ("VENUE-MAIN", 300, "All emergency exits must remain unobstructed."))
    
    cursor.execute("REPLACE INTO events (event_id, date, attendance, venue_id, status) VALUES (?, ?, ?, ?, ?)",
                   ("S06", "2026-10-15", 260, "VENUE-MAIN", "Scheduled"))
    
    conn.commit()
    conn.close()
    print("[+] SQLite database initialized with legacy conflicting venue capacity (300).")

    # 3. Write Binding Change Notice Documents
    notice_1 = """# Document ID: NOTICE-2026-01
# Title: Urgent Notice - Main Hall Capacity Revision
# Version: 1.0
# Status: Current / Signed Approval
# Effective Date: 5 October 2026

- Due to structural engineering updates, the Main Hall capacity is officially revised from 300 down to **240**. 
- All event planners and departmental leads must enforce this 240 cap immediately, superseding any legacy documentation mentioning 300.
"""

    notice_2 = """# Document ID: NOTICE-2026-02
# Title: Schedule Shift Notice for Multi-Department Alignment
# Version: 1.0
# Status: Current
# Effective Date: 8 October 2026

- Event timings are officially shifted from 10:00–16:00 to **12:00–18:00**.
- Catering, security shifts, and staffing hours must align with the updated 12-hour/6-hour operational window without schedule contradiction.
"""

    Path("documents/change_notices/NOTICE-2026-01.md").write_text(notice_1, encoding="utf-8")
    Path("documents/change_notices/NOTICE-2026-02.md").write_text(notice_2, encoding="utf-8")
    print("[+] Change notice markdown documents created successfully in documents/change_notices/.")

if __name__ == "__main__":
    setup_conflict_environment()