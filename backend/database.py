# backend/database.py
import os
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]
from supabase import create_client, Client # type: ignore

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

print("DEBUG - Supabase URL:", SUPABASE_URL)  #Temporary debug print
print("DEBUG - Supabase Key:", SUPABASE_KEY)  #Temporary debug print

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)