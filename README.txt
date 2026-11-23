# FraudLens — AI + Database Integration

## Flow
Browser -> Node backend (port 5000) -> Python AI
                         |
                         -> Python DB bridge -> SQLite (fraudlens.db)

## What is integrated
- Existing FraudLens Python AI pipeline
- Existing SQLite schema/tables from the database team
- Evidence saved after every successful AI analysis
- Sensitive phone/account/URL values saved masked
- Timeline events saved from extracted time/type/raw evidence
- Incident ID returned to the frontend
- Frontend displays DB save status
- AI report rendering handles the current Python pipeline's string output

## Run
1. Keep the existing AI folder at the current path, or set AI_FOLDER in `.env`.
2. In this project's `backend` folder:
   `npm install`
   `node server.js`
3. Open `frontend/case-file-integrated.html`.
4. Go to Incident Report -> Analyze with AI.
5. After analysis, the screen shows the Incident ID.

## Database file
`database/fraudlens.db` is created automatically on first analysis.

## Health checks
- `http://localhost:5000/health`
- `http://localhost:5000/api/db/health`
- `http://localhost:5000/api/incidents`
