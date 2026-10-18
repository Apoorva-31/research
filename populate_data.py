import os
import sqlite3
import pandas as pd

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# 1. Define Structured Data for S01 - S12
events_data = [
    {"event_id": "EVT-01", "date": "2026-10-15", "attendance": 200, "venue_id": "VENUE-001", "status": "Approved"},
    {"event_id": "EVT-02", "date": "2026-10-16", "attendance": 280, "venue_id": "VENUE-001", "status": "Pending Review"},
    {"event_id": "EVT-03", "date": "2026-10-17", "attendance": 260, "venue_id": "VENUE-002", "status": "Pending Review"},
    {"event_id": "EVT-04", "date": "2026-10-18", "attendance": 200, "venue_id": "VENUE-001", "status": "Budget Revision"},
    {"event_id": "EVT-05", "date": "2026-10-19", "attendance": 200, "venue_id": "VENUE-001", "status": "Layout Review"},
    {"event_id": "EVT-06", "date": "2026-10-20", "attendance": 240, "venue_id": "VENUE-001", "status": "Capacity Update"},
    {"event_id": "EVT-07", "date": "2026-10-21", "attendance": 200, "venue_id": "VENUE-001", "status": "Schedule Shift"},
    {"event_id": "EVT-08", "date": "2026-10-22", "attendance": 180, "venue_id": "VENUE-001", "status": "Dietary Review"},
    {"event_id": "EVT-09", "date": "2026-10-23", "attendance": 201, "venue_id": "VENUE-001", "status": "Staffing Review"},
    {"event_id": "EVT-10", "date": "2026-10-24", "attendance": 200, "venue_id": "VENUE-001", "status": "Budget Limit Review"},
    {"event_id": "EVT-11", "date": "2026-10-25", "attendance": 200, "venue_id": "VENUE-001", "status": "Policy Review"},
    {"event_id": "EVT-12", "date": "2026-10-26", "attendance": 240, "venue_id": "VENUE-003", "status": "Complex Revision"}
]

budgets_data = [
    {"event_id": "EVT-01", "total_limit": 200000, "catering_limit": 100000, "staffing_limit": 50000},
    {"event_id": "EVT-02", "total_limit": 200000, "catering_limit": 100000, "staffing_limit": 50000},
    {"event_id": "EVT-03", "total_limit": 200000, "catering_limit": 100000, "staffing_limit": 50000},
    {"event_id": "EVT-04", "total_limit": 160000, "catering_limit": 80000, "staffing_limit": 40000},
    {"event_id": "EVT-05", "total_limit": 200000, "catering_limit": 100000, "staffing_limit": 50000},
    {"event_id": "EVT-06", "total_limit": 200000, "catering_limit": 100000, "staffing_limit": 50000},
    {"event_id": "EVT-07", "total_limit": 200000, "catering_limit": 100000, "staffing_limit": 50000},
    {"event_id": "EVT-08", "total_limit": 180000, "catering_limit": 90000, "staffing_limit": 45000},
    {"event_id": "EVT-09", "total_limit": 200000, "catering_limit": 100000, "staffing_limit": 50000},
    {"event_id": "EVT-10", "total_limit": 100000, "catering_limit": 90000, "staffing_limit": 10000},
    {"event_id": "EVT-11", "total_limit": 200000, "catering_limit": 100000, "staffing_limit": 50000},
    {"event_id": "EVT-12", "total_limit": 190000, "catering_limit": 95000, "staffing_limit": 45000}
]

catering_data = [
    {"event_id": "EVT-01", "meal_type": "Standard", "required_quantity": 200, "unit_cost": 450},
    {"event_id": "EVT-02", "meal_type": "Standard", "required_quantity": 280, "unit_cost": 450},
    {"event_id": "EVT-03", "meal_type": "Standard", "required_quantity": 260, "unit_cost": 450},
    {"event_id": "EVT-04", "meal_type": "Standard", "required_quantity": 200, "unit_cost": 400},
    {"event_id": "EVT-05", "meal_type": "Standard", "required_quantity": 200, "unit_cost": 450},
    {"event_id": "EVT-06", "meal_type": "Standard", "required_quantity": 240, "unit_cost": 450},
    {"event_id": "EVT-07", "meal_type": "Standard", "required_quantity": 200, "unit_cost": 450},
    {"event_id": "EVT-08", "meal_type": "Vegetarian/Vegan", "required_quantity": 180, "unit_cost": 450},
    {"event_id": "EVT-09", "meal_type": "Standard", "required_quantity": 201, "unit_cost": 450},
    {"event_id": "EVT-10", "meal_type": "Standard", "required_quantity": 200, "unit_cost": 450},
    {"event_id": "EVT-11", "meal_type": "Standard", "required_quantity": 200, "unit_cost": 450},
    {"event_id": "EVT-12", "meal_type": "Standard", "required_quantity": 240, "unit_cost": 450}
]

staffing_data = [
    {"event_id": "EVT-01", "role": "Security Guard", "minimum_required": 4, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-02", "role": "Security Guard", "minimum_required": 6, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-03", "role": "Security Guard", "minimum_required": 5, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-04", "role": "Security Guard", "minimum_required": 4, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-05", "role": "Security Guard", "minimum_required": 4, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-06", "role": "Security Guard", "minimum_required": 5, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-07", "role": "Security Guard", "minimum_required": 4, "shift_start": "12:00", "shift_end": "18:00"},
    {"event_id": "EVT-08", "role": "Security Guard", "minimum_required": 4, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-09", "role": "Security Guard", "minimum_required": 5, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-10", "role": "Security Guard", "minimum_required": 4, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-11", "role": "Security Guard", "minimum_required": 4, "shift_start": "09:00", "shift_end": "17:00"},
    {"event_id": "EVT-12", "role": "Security Guard", "minimum_required": 5, "shift_start": "10:00", "shift_end": "18:00"}
]

venues_data = [
    {"venue_id": "VENUE-001", "capacity": 250, "emergency_exit_rules": "Must remain unobstructed."},
    {"venue_id": "VENUE-002", "capacity": 220, "emergency_exit_rules": "Must remain unobstructed."},
    {"venue_id": "VENUE-003", "capacity": 260, "emergency_exit_rules": "Must remain unobstructed."}
]

# 2. Save DataFrames to CSV
pd.DataFrame(events_data).to_csv("data/events.csv", index=False)
pd.DataFrame(budgets_data).to_csv("data/budgets.csv", index=False)
pd.DataFrame(catering_data).to_csv("data/catering.csv", index=False)
pd.DataFrame(staffing_data).to_csv("data/staffing.csv", index=False)

print("CSV files successfully created in data/")

# 3. Build and Sync SQLite Database (event_memory.db)
db_path = "data/event_memory.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create Tables
cursor.execute("DROP TABLE IF EXISTS events;")
cursor.execute("DROP TABLE IF EXISTS venues;")
cursor.execute("DROP TABLE IF EXISTS budgets;")
cursor.execute("DROP TABLE IF EXISTS catering;")
cursor.execute("DROP TABLE IF EXISTS staffing;")

cursor.execute("""
CREATE TABLE venues (
    venue_id TEXT PRIMARY KEY,
    capacity INTEGER,
    emergency_exit_rules TEXT
);
""")

cursor.execute("""
CREATE TABLE events (
    event_id TEXT PRIMARY KEY,
    date TEXT,
    attendance INTEGER,
    venue_id TEXT,
    status TEXT,
    FOREIGN KEY(venue_id) REFERENCES venues(venue_id)
);
""")

cursor.execute("""
CREATE TABLE budgets (
    event_id TEXT PRIMARY KEY,
    total_limit REAL,
    catering_limit REAL,
    staffing_limit REAL,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);
""")

cursor.execute("""
CREATE TABLE catering (
    event_id TEXT,
    meal_type TEXT,
    required_quantity INTEGER,
    unit_cost REAL,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);
""")

cursor.execute("""
CREATE TABLE staffing (
    event_id TEXT,
    role TEXT,
    minimum_required INTEGER,
    shift_start TEXT,
    shift_end TEXT,
    FOREIGN KEY(event_id) REFERENCES events(event_id)
);
""")

# Insert Data into SQLite
pd.DataFrame(venues_data).to_sql("venues", conn, if_exists="append", index=False)
pd.DataFrame(events_data).to_sql("events", conn, if_exists="append", index=False)
pd.DataFrame(budgets_data).to_sql("budgets", conn, if_exists="append", index=False)
pd.DataFrame(catering_data).to_sql("catering", conn, if_exists="append", index=False)
pd.DataFrame(staffing_data).to_sql("staffing", conn, if_exists="append", index=False)

conn.commit()
conn.close()

print("SQLite database `data/event_memory.db` successfully initialized and populated!")