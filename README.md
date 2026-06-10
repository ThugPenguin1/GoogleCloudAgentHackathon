# Atlas Study Companion — Rapid Hackathon Build

This repo contains the Atlas Study Companion demo for the MongoDB partner track. It is built to look and feel like a real student study dashboard, not just a tool stub.

Quick start (local):

1. Create a free MongoDB Atlas cluster and get the connection string.
2. Export your URI into the environment:

```bash
export MONGO_URI="your-mongodb-connection-string"
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python study_server.py
```

3. Open the dashboard:

```bash
python study_server.py
```

Then visit `http://localhost:8080` for the full dashboard.

4. Seed the sample MongoDB data first:

```bash
python test_mongo.py
```

Key files:
- `mongodb_tools.py` — MongoDB logic for progress, scheduling, calibration, and dashboard assembly
- `study_server.py` — Flask server exposing `/tool/<name>` and `/api/student/<id>/dashboard`
- `web/index.html` — polished dashboard UI
- `sample_data.json` — richer seed data for the semester demo
- `system_prompt.txt` — Agent Builder instructions
- `test_mongo.py` — seed script for MongoDB Atlas
- `requirements.txt` — Python dependencies

Notes on deployment:
- Store `MONGO_URI` in Google Secret Manager and reference it from Cloud Run.
- Deploy `study_server.py` to Cloud Run, enable ingress, and use the resulting URL in Agent Builder MCP tool config.

Demo flow:
1. Open the Cloud Run URL root page.
2. Show the dashboard progress cards and semester roadmap.
3. Log a study session and refresh to show MongoDB writes.
4. Search materials, open Desmos, and show the knowledge tree.
5. Finish by showing the study recommendation output and progress calibration.
