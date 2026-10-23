# backend/routes/brand_kit.py
from fastapi import APIRouter # type: ignore
from models import BrandRuleCreate
from database import supabase

router = APIRouter()


@router.get("/")
def get_rules():
    res = supabase.table("brand_rules").select("*").order("created_at", desc=True).execute()
    return {"rules": res.data}


@router.post("/")
def create_rule(rule: BrandRuleCreate):
    res = supabase.table("brand_rules").insert(rule.dict()).execute()
    return {"rule": res.data[0]}


@router.delete("/{rule_id}")
def delete_rule(rule_id: str):
    supabase.table("brand_rules").delete().eq("id", rule_id).execute()
    return {"success": True}