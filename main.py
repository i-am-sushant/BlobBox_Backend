from fastapi import FastAPI, UploadFile, HTTPException
from azure.storage.blob import BlobServiceClient
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import os

app = FastAPI()

# Load configuration from environment variables
BLOB_CONN_STR = os.getenv("BLOB_CONN_STR")
POSTGRES_CONN_STR = os.getenv("POSTGRES_CONN_STR")

# Initialize Blob Service Client
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONN_STR)
container_name = "project-uploads"

# Connect to PostgreSQL
conn = psycopg2.connect(POSTGRES_CONN_STR)
cursor = conn.cursor()

@app.post("/upload/{folder_name}")
async def upload_file(folder_name: str, file: UploadFile):
    try:
        # Upload to Blob Storage
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=f"{folder_name}/{file.filename}"
        )
        blob_client.upload_blob(file.file)

        # Save metadata in PostgreSQL
        cursor.execute(
            "INSERT INTO file_metadata (name, type, size, folder) VALUES (%s, %s, %s, %s)",
            (file.filename, file.content_type, file.size, folder_name),
        )
        conn.commit()

        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/download/{folder_name}/{file_name}")
async def download_file(folder_name: str, file_name: str):
    try:
        # Download file from Blob Storage
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=f"{folder_name}/{file_name}"
        )
        stream = blob_client.download_blob()
        return {"file_content": stream.readall()}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


app.add_middleware(
    CORSMiddleware,
    allow_origins=["<frontend-url>"],  # Replace with your Azure Static Web App URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/files")
async def list_files():
    cursor.execute("SELECT * FROM file_metadata")
    files = cursor.fetchall()
    file_list = [
        {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "size": row[3],
            "folder": row[4],
            "uploaded_at": row[5],
        }
        for row in files
    ]
    return {"files": file_list}

