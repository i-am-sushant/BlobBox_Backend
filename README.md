# BlobBox Backend

FastAPI backend for BlobBox.

- Stores files in **Azure Blob Storage** (container: `project-uploads`)
- Stores upload metadata in **PostgreSQL** (`file_metadata` table)
- Intended to be used with the BlobBox frontend (CORS is configured accordingly)

## Tech

- Python + FastAPI
- Azure Blob Storage (`azure-storage-blob`)
- PostgreSQL (`psycopg2-binary`)

## Prerequisites

- Python 3.10+ (3.11 recommended)
- An Azure Storage account + a Blob container named `project-uploads`
- A PostgreSQL database

## Environment variables

Set these before running the API:

- `BLOB_CONN_STR` – Azure Storage connection string
- `POSTGRES_CONN_STR` – PostgreSQL connection string

Example (PowerShell):

```powershell
$env:BLOB_CONN_STR = "DefaultEndpointsProtocol=https;AccountName=..."
$env:POSTGRES_CONN_STR = "postgresql://USER:PASSWORD@HOST:5432/DBNAME"
```

## Database schema

This service expects a table named `file_metadata`.

```sql
CREATE TABLE IF NOT EXISTS file_metadata (
  id SERIAL PRIMARY KEY,
  name   TEXT NOT NULL,
  type   TEXT,
  size   BIGINT,
  folder TEXT
);
```

## Install & run (local)

```powershell
cd BlobBox_Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Then open:

- API docs: http://localhost:8000/docs

## CORS / frontend origin

CORS is currently locked to the deployed frontend origin in `main.py`.

For local frontend development (e.g. React dev server on `http://localhost:3000`), add it to the `allow_origins` list.

## API

Base URL: `http://localhost:8000`

### List files

`GET /files`

Returns blob names from the `project-uploads` container.

### Upload file

`POST /upload/{folder_name}`

- `folder_name` becomes the virtual “folder” prefix in blob storage
- Expects multipart form field named `file`

Example:

```bash
curl -F "file=@./example.pdf" http://localhost:8000/upload/invoices
```

### Download file

`GET /download/{folder_name}/{file_name}`

Returns JSON with `file_content` (raw bytes). For production use, you’ll typically return a streaming response with proper headers instead.

## Notes

- Upload behavior: `upload_blob(...)` will fail if the blob already exists unless `overwrite=True` is used.
- The DB connection and blob client are initialized at import time; missing env vars will cause startup failures.
