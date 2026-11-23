from database import engine
from sqlalchemy import text

with engine.begin() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS incidents (
            incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            incident_type TEXT,
            status TEXT DEFAULT 'ACTIVE',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS evidence (
            evidence_id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            file_name TEXT NOT NULL,
            file_type TEXT,
            source TEXT,
            raw_text TEXT,
            uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS sensitive_data (
            evidence_id INTEGER,
            data_type TEXT,
            masked_value TEXT
        )
    """))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS timeline_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id INTEGER NOT NULL,
            evidence_id INTEGER,
            event_time TEXT,
            event_type TEXT,
            description TEXT
        )
    """))

print("SQLite tables initialized successfully!")
