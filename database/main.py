from fastapi import FastAPI, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import text
from database import engine

app = FastAPI(title="FraudLens Database Module", version="1.0")

# Helper function to mask sensitive data
def mask_sensitive_info(data_str: str) -> str:
    if not data_str or len(data_str) <= 2:
        return "**"
    return data_str[:2] + "X" * (len(data_str) - 2)

class SensitiveInput(BaseModel):
    evidence_id: int
    data_type: str
    raw_value: str

class TimelineItem(BaseModel):
    incident_id: int
    evidence_id: int
    event_time: str
    event_type: str
    description: str

@app.post("/incidents/sensitive-data")
def store_sensitive_data(item: SensitiveInput):
    try:
        masked_val = mask_sensitive_info(item.raw_value)

        with engine.begin() as connection:
            sql = text("""
                INSERT INTO sensitive_data (evidence_id, data_type, masked_value)
                VALUES (:evidence_id, :data_type, :masked_value)
            """)
            connection.execute(
                sql,
                {
                    "evidence_id": item.evidence_id,
                    "data_type": item.data_type,
                    "masked_value": masked_val
                }
            )

        return {
            "status": "success",
            "message": "Sensitive data securely masked and stored!",
            "data_type": item.data_type,
            "masked_value": masked_val
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/incidents/timeline")
def add_timeline_event(item: TimelineItem):
    try:
        with engine.begin() as connection:
            sql = text("""
                INSERT INTO timeline_events (incident_id, evidence_id, event_time, event_type, description)
                VALUES (:incident_id, :evidence_id, :event_time, :event_type, :description)
            """)
            connection.execute(
                sql,
                {
                    "incident_id": item.incident_id,
                    "evidence_id": item.evidence_id,
                    "event_time": item.event_time,
                    "event_type": item.event_type,
                    "description": item.description
                }
            )
        return {"status": "success", "message": "Timeline event stored successfully!"}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/")
def home():
    return {"message": "FraudLens Backend with Privacy Redaction is Live!"}
