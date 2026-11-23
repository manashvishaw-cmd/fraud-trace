import json
import sys
from sqlalchemy import text
from database import engine

def init_tables():
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

def mask_sensitive_info(value):
    if not value:
        return value
    if len(value) <= 2:
        return "**"
    return value[:2] + "X" * (len(value) - 2)

def save_case(payload):
    init_tables()
    evidence = payload.get("evidence", [])
    incident_title = payload.get("title") or "Fraud Incident"
    incident_type = payload.get("incident_type") or "FRAUD"
    description = payload.get("description") or "Evidence analyzed by FraudLens AI."

    with engine.begin() as conn:
        result = conn.execute(text("""
            INSERT INTO incidents (title, description, incident_type, status)
            VALUES (:title, :description, :incident_type, 'ACTIVE')
        """), {
            "title": incident_title,
            "description": description,
            "incident_type": incident_type
        })
        incident_id = result.lastrowid

        saved_evidence = 0
        saved_sensitive = 0
        saved_timeline = 0

        for item in evidence:
            fields = item.get("fields") or {}
            cur = conn.execute(text("""
                INSERT INTO evidence
                (incident_id, file_name, file_type, source, raw_text)
                VALUES (:incident_id, :file_name, :file_type, :source, :raw_text)
            """), {
                "incident_id": incident_id,
                "file_name": item.get("id") or f"evidence-{saved_evidence+1}",
                "file_type": item.get("type") or "unknown",
                "source": "FraudLens frontend",
                "raw_text": item.get("raw") or ""
            })
            evidence_id = cur.lastrowid
            saved_evidence += 1

            for key in ("phone", "account", "url"):
                value = fields.get(key)
                if value:
                    conn.execute(text("""
                        INSERT INTO sensitive_data
                        (evidence_id, data_type, masked_value)
                        VALUES (:evidence_id, :data_type, :masked_value)
                    """), {
                        "evidence_id": evidence_id,
                        "data_type": key,
                        "masked_value": mask_sensitive_info(str(value))
                    })
                    saved_sensitive += 1

            event_time = fields.get("time")
            if event_time or item.get("raw"):
                conn.execute(text("""
                    INSERT INTO timeline_events
                    (incident_id, evidence_id, event_time, event_type, description)
                    VALUES (:incident_id, :evidence_id, :event_time, :event_type, :description)
                """), {
                    "incident_id": incident_id,
                    "evidence_id": evidence_id,
                    "event_time": event_time or "Unknown",
                    "event_type": item.get("type") or "evidence",
                    "description": item.get("raw") or ""
                })
                saved_timeline += 1

    return {
        "saved": True,
        "incident_id": incident_id,
        "evidence_count": saved_evidence,
        "sensitive_data_count": saved_sensitive,
        "timeline_count": saved_timeline
    }

def list_incidents():
    init_tables()
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT incident_id, title, incident_type, status, created_at
            FROM incidents
            ORDER BY incident_id DESC
        """)).mappings().all()
    return [dict(r) for r in rows]

def main():
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        action = payload.get("action")

        if action == "save_case":
            result = save_case(payload)
        elif action == "list_incidents":
            result = {"incidents": list_incidents()}
        else:
            raise ValueError("Unknown database action")

        print(json.dumps(result, ensure_ascii=False, default=str))
    except Exception as e:
        print(json.dumps({"saved": False, "error": str(e)}))

if __name__ == "__main__":
    main()
