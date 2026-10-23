# backend/routes/insights.py
from fastapi import APIRouter
from database import supabase
from collections import Counter

router = APIRouter()


@router.get("/")
def get_insights():
    findings_res = supabase.table("findings").select("*, brand_rules(title)").execute()
    findings = findings_res.data

    rule_counter = Counter()
    gaps = []

    for f in findings:
        rule_info = f.get("brand_rules")
        rule_title = rule_info.get("title") if rule_info else "Unmapped / Unverified"
        rule_counter[rule_title] += 1
        if f.get("marked_as_gap"):
            gaps.append(f)

    top_issues = [{"name": k, "count": v} for k, v in rule_counter.most_common()]

    return {"topIssues": top_issues, "gaps": gaps}


@router.post("/mark-gap/{finding_id}")
def mark_gap(finding_id: str):
    supabase.table("findings").update({"marked_as_gap": True}).eq("id", finding_id).execute()
    return {"success": True}