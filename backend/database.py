# backend/database.py
import os
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
from supabase import create_client, Client # type: ignore

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)