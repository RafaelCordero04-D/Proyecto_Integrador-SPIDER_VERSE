import os
from supabase import create_client, Client
from typing import Optional
from fastapi import UploadFile
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL_SPIDER")
key = os.getenv("SUPABASE_KEY_SPIDER")
bucket = os.getenv("SUPABASE_BUCKET_SPIDER")

_supabase_client:Optional[Client] = None

def get_supabase_client():
    global _supabase_client
    if _supabase_client is None:
        if not url or not key:
            raise ValueError(
                "No estan las credenciales"
            )
        _supabase_client = create_client(url, key)

        return _supabase_client

async def upload_to_bucket(file: UploadFile):
    client = get_supabase_client()

    try:
        file_content = await file.read()
        file_path = f"public/{file.filename}"
        result = client.storage.from_(bucket).upload(
            path=file_path,
            file=file_content,
            file_options={
                "content-type": file.content_type
            }
        )
        public_url = client.storage.from_(bucket).get_public_url(file_path)
        return public_url
    except Exception as e:
        raise e