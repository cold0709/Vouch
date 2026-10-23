# backend/routes/review.py
from fastapi import APIRouter
from models import ReviewRequest
from database import supabase

router = APIRouter()


@router.post("/")
def submit_review(req: ReviewRequest):
    supabase.table("contents").update({"status": req.decision}).eq("id", req.content_id).execute()

    if req.comment:
        supabase.table("comments").insert({
            "content_id": req.content_id,
            "user_name": req.user_name,
            "message": req.comment
        }).execute()

    return {"success": True}


@router.get("/comments/{content_id}")
def get_comments(content_id: str):
    res = supabase.table("comments").select("*").eq("content_id", content_id).order("created_at", desc=True).execute()
    return {"comments": res.data}