# Testing and verification

Run backend checks from `backend/`:

```powershell
python -m pip install -r requirements.txt
python -m compileall app
uvicorn app.main:app --reload
```

Visit `/docs`, register a user, upload a small CSV, then submit `/agent/run` with its `file_id` and a goal asking for analysis. Confirm that the returned row/column counts match the CSV. Also try an unsupported upload and an ID owned by another user; those should fail safely. Automated tests should be expanded phase by phase for authentication, ownership, tool outputs, malformed files, task planning, and recovery.
