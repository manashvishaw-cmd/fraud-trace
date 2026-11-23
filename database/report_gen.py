# backend/report_gen.py
import csv
import io
from database import engine

def generate_csv_report(incident_id: int) -> str:
    """
    Queries Oracle 11g for timeline events and evidence related to an incident
    and returns a clean CSV formatted string for the report.
    """
    query = """
        SELECT e.incident_id, t.evidence_id, t.event_time, t.event_type, t.description
        FROM timeline_events t
        JOIN evidence e ON t.evidence_id = e.evidence_id
        WHERE t.incident_id = :inc_id
        ORDER BY t.event_time
    """
    
    output = io.StringIO()
    writer = csv.writer(output)
    # CSV Header matching hackathon report requirements
    writer.writerow(["incident_id", "evidence_id", "event_time", "event_type", "description"])
    
    with engine.connect() as connection:
        result = connection.execute(query, {"inc_id": incident_id})
        for row in result:
            writer.writerow(row)
            
    return output.getvalue()
