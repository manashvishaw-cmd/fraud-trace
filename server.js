require('dotenv').config();

const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');
const path = require('path');

const app = express();

app.use(cors());
app.use(express.json({ limit: '10mb' }));

const PORT = process.env.PORT || 5000;

// =========================
// PYTHON AI
// =========================
const AI_FOLDER = path.join(
  process.env.USERPROFILE,
  'Downloads',
  'ignithon',
  'ignithon',
  'fraudlens_ai'
);

const AI_SCRIPT = path.join(AI_FOLDER, 'run_pipeline.py');

// =========================
// DATABASE
// =========================
const DB_FOLDER = path.join(__dirname, 'database');
const DB_SCRIPT = path.join(DB_FOLDER, 'db_bridge.py');


// =========================
// HEALTH CHECK
// =========================
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    service: 'fraud-incident-backend',
    ai: 'python-fraudlens',
    database: 'sqlite-fraudlens'
  });
});


// =========================
// RUN PYTHON SCRIPT
// =========================
function runPython(script, cwd, input) {
  return new Promise((resolve, reject) => {

    const python = spawn('py', [script], {
      cwd,
      windowsHide: true
    });

    let output = '';
    let errorOutput = '';

    python.stdout.on('data', (data) => {
      output += data.toString();
    });

    python.stderr.on('data', (data) => {
      errorOutput += data.toString();
    });

    python.on('error', (err) => {
      reject(err);
    });

    python.on('close', (code) => {

      if (code !== 0) {
        reject(
          new Error(
            errorOutput || `Python exited with code ${code}`
          )
        );
        return;
      }

      try {
        const result = JSON.parse(output.trim());
        resolve(result);
      } catch (err) {
        reject(
          new Error(
            'Python returned invalid JSON.\n' + output
          )
        );
      }
    });

    python.stdin.write(
      JSON.stringify(input),
      'utf8'
    );

    python.stdin.end();
  });
}


// =========================
// AI FUNCTION
// =========================
function runPythonAI(evidence) {
  return runPython(
    AI_SCRIPT,
    AI_FOLDER,
    { evidence }
  );
}


// =========================
// DATABASE FUNCTION
// =========================
function runDatabase(action, data = {}) {
  return runPython(
    DB_SCRIPT,
    DB_FOLDER,
    {
      action,
      ...data
    }
  );
}


// =========================
// AI + DATABASE
// =========================
app.post('/api/analyze-incident', async (req, res) => {

  try {

    const { evidence } = req.body;

    if (!Array.isArray(evidence) || evidence.length === 0) {
      return res.status(400).json({
        error: 'evidence is required'
      });
    }

    console.log(
      `AI analysis started for ${evidence.length} evidence items`
    );

    // Run AI
    const result = await runPythonAI(evidence);

    console.log('AI analysis completed');


    // Save to database
    let database = {
      saved: false
    };

    try {

      database = await runDatabase(
        'save_case',
        {
          evidence,
          title: 'FraudLens Incident',
          incident_type: 'FRAUD'
        }
      );

      console.log(
        `Database save completed: incident ${database.incident_id}`
      );

    } catch (dbError) {

      console.error(
        'DATABASE ERROR:',
        dbError
      );

      database = {
        saved: false,
        error: dbError.message
      };
    }


    res.json({
      ...result,
      database
    });

  } catch (err) {

    console.error(
      'AI ERROR:',
      err
    );

    res.status(500).json({
      error: 'AI analysis failed',
      detail: err.message
    });
  }
});


// =========================
// GET SAVED INCIDENTS
// =========================
app.get('/api/incidents', async (req, res) => {

  try {

    const result = await runDatabase(
      'list_incidents'
    );

    res.json(result);

  } catch (err) {

    res.status(500).json({
      error: 'Database read failed',
      detail: err.message
    });
  }
});


// =========================
// DATABASE HEALTH
// =========================
app.get('/api/db/health', async (req, res) => {

  try {

    const result = await runDatabase(
      'list_incidents'
    );

    res.json({
      status: 'ok',
      database: 'sqlite',
      incident_count: result.incidents.length
    });

  } catch (err) {

    res.status(500).json({
      status: 'error',
      database: 'sqlite',
      detail: err.message
    });
  }
});


// =========================
// START SERVER
// =========================
app.listen(PORT, () => {

  console.log(
    `Server running on http://localhost:${PORT}`
  );

  console.log(
    `Python AI connected: ${AI_SCRIPT}`
  );

  console.log(
    `Database connected: ${DB_SCRIPT}`
  );

});