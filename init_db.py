import sqlite3
from pathlib import Path

def initialize_database():
    db_path = Path("data/event_memory.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
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
            status TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            event_id TEXT PRIMARY KEY,
            total_limit REAL,
            catering_limit REAL,
            staffing_limit REAL
        )
    """)

    # Insert conflicting test record for Scenario S06 / S13
    # Database says 300 (outdated), but document notice says 240!
    cursor.execute("INSERT OR REPLACE INTO venues VALUES ('VENUE-MAIN', 300, 'Keep all exits clear')")
    cursor.execute("INSERT OR REPLACE INTO events VALUES ('EVT-S06', '2026-10-15', 260, 'VENUE-MAIN', 'Active')")
    cursor.execute("INSERT OR REPLACE INTO budgets VALUES ('EVT-S06', 200000.0, 90000.0, 50000.0)")
    
    conn.commit()
    conn.close()
    print("Database initialized with conflicting legacy capacity (300) for EVT-S06.")

if __name__ == "__main__":
    initialize_database()