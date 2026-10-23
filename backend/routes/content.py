# backend/routes/content.py
from fastapi import APIRouter
from models import ContentCreate
from database import supabase

router = APIRouter()


@router.post("/")
def create_content(content: ContentCreate):
    res = supabase.table("contents").insert({
        "title": content.title,
        "current_text": content.text,
        "status": "DRAFT"
    }).execute()
    return {"content": res.data[0]}


@router.get("/")
def list_content():
    res = supabase.table("contents").select("*").order("created_at", desc=True).execute()
    return {"contents": res.data}


@router.get("/{content_id}")
def get_content(content_id: str):
    content_res = supabase.table("contents").select("*").eq("id", content_id).single().execute()

    versions_res = supabase.table("content_versions").select("id").eq("content_id", content_id).execute()
    version_ids = [v["id"] for v in versions_res.data]

    findings = []
    if version_ids:
        findings_res = supabase.table("findings").select("*").in_("content_version_id", version_ids).order("created_at", desc=True).execute()
        findings = findings_res.data

    return {"content": content_res.data, "findings": findings}


@router.put("/{content_id}")
def update_content(content_id: str, content: ContentCreate):
    supabase.table("contents").update({"current_text": content.text}).eq("id", content_id).execute()
    return {"success": True}