-- FraudLens Database Schema
-- Tables, sequences, and auto-increment triggers

-- =========================
-- INCIDENTS
-- =========================
CREATE TABLE incidents (
    incident_id      NUMBER(10) PRIMARY KEY,
    title            VARCHAR2(200) NOT NULL,
    description      CLOB,
    incident_type    VARCHAR2(100),
    status           VARCHAR2(30) DEFAULT 'ACTIVE',
    created_at       TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE SEQUENCE incident_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;

CREATE OR REPLACE TRIGGER incident_bir BEFORE INSERT ON incidents FOR EACH ROW
BEGIN
    IF :NEW.incident_id IS NULL THEN
        SELECT incident_seq.NEXTVAL INTO :NEW.incident_id FROM dual;
    END IF;
END;
/

-- =========================
-- EVIDENCE
-- =========================
CREATE TABLE evidence (
    evidence_id      NUMBER(10) PRIMARY KEY,
    incident_id      NUMBER(10) NOT NULL,
    file_name        VARCHAR2(255) NOT NULL,
    file_type        VARCHAR2(50),
    source           VARCHAR2(100),
    raw_text         CLOB,
    uploaded_at      TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_evidence_incident FOREIGN KEY (incident_id) REFERENCES incidents(incident_id)
);

CREATE SEQUENCE evidence_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;

CREATE OR REPLACE TRIGGER evidence_bir BEFORE INSERT ON evidence FOR EACH ROW
BEGIN
    IF :NEW.evidence_id IS NULL THEN
        SELECT evidence_seq.NEXTVAL INTO :NEW.evidence_id FROM dual;
    END IF;
END;
/

-- =========================
-- TIMELINE_EVENTS
-- =========================
CREATE TABLE timeline_events (
    event_id          NUMBER(10) PRIMARY KEY,
    incident_id       NUMBER(10) NOT NULL,
    evidence_id       NUMBER(10),
    event_time        TIMESTAMP,
    event_type        VARCHAR2(100),
    description       VARCHAR2(2000),
    CONSTRAINT fk_timeline_incident FOREIGN KEY (incident_id) REFERENCES incidents(incident_id),
    CONSTRAINT fk_timeline_evidence FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id)
);

CREATE SEQUENCE timeline_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;

CREATE OR REPLACE TRIGGER timeline_bir BEFORE INSERT ON timeline_events FOR EACH ROW
BEGIN
    IF :NEW.event_id IS NULL THEN
        SELECT timeline_seq.NEXTVAL INTO :NEW.event_id FROM dual;
    END IF;
END;
/

-- =========================
-- SENSITIVE_DATA
-- =========================
CREATE TABLE sensitive_data (
    sensitive_id     NUMBER(10) PRIMARY KEY,
    evidence_id      NUMBER(10) NOT NULL,
    data_type        VARCHAR2(100),
    masked_value     VARCHAR2(500),
    created_at       TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
    CONSTRAINT fk_sensitive_evidence FOREIGN KEY (evidence_id) REFERENCES evidence(evidence_id)
);

CREATE SEQUENCE sensitive_data_seq START WITH 1 INCREMENT BY 1 NOCACHE NOCYCLE;

CREATE OR REPLACE TRIGGER sensitive_data_bir BEFORE INSERT ON sensitive_data FOR EACH ROW
BEGIN
    IF :NEW.sensitive_id IS NULL THEN
        SELECT sensitive_data_seq.NEXTVAL INTO :NEW.sensitive_id FROM dual;
    END IF;
END;
/