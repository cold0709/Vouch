# backend/routes/check.py
import os
import re
import json
from fastapi import APIRouter
from openai import OpenAI
from pydantic import ValidationError
from models import CheckRequest, CheckResponse
from database import supabase

router = APIRouter()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def run_rule_based_checks(text: str, rules: list) -> list:
    findings = []
    term_rules = [r for r in rules if r["type"] == "terminology"]

    for rule in term_rules:
        if rule.get("avoid_term") and rule["avoid_term"].lower() in text.lower():
            findings.append({
                "type": "terminology",
                "rule_id": rule["id"],
                "status": "CONFLICT",
                "explanation": f'Guideline "{rule["title"]}" states: {rule["content"]}',
                "original_snippet": rule["avoid_term"],
                "suggested_fix": rule["preferred_term"],
                "severity": "medium",
            })

    if re.search(r"!{2,}", text):
        match = re.search(r"\S*!{2,}\S*", text)
        findings.append({
            "type": "tone",
            "rule_id": None,
            "status": "CONFLICT",
            "explanation": "Multiple exclamation marks detected — may appear unprofessional.",
            "original_snippet": match.group(0) if match else "!!",
            "suggested_fix": re.sub(r"!{2,}", ".", text),
            "severity": "low",
        })

    return findings


def run_accessibility_checks(text: str) -> list:
    findings = []
    if "click here" in text.lower():
        findings.append({
            "type": "accessibility",
            "rule_id": None,
            "status": "CONFLICT",
            "explanation": "Vague link text like 'click here' is not accessible for screen readers.",
            "original_snippet": "click here",
            "suggested_fix": "View our offer",
            "severity": "low",
        })
    return findings


def run_ai_checks(text: str, rules: list) -> list:
    facts = [r for r in rules if r["type"] == "fact"]
    tones = [r for r in rules if r["type"] == "tone"]

    facts_str = "\n".join([f'ID: {f["id"]} | {f["content"]}' for f in facts])
    tones_str = "\n".join([f'ID: {t["id"]} | {t["content"]}' for t in tones])

    prompt = f"""
You are a brand compliance checker. You MUST only use the rule IDs provided below.
If you flag something but no rule/fact supports it, set rule_id to null and status to "UNVERIFIED".
Never invent facts or rules that are not listed here.

APPROVED FACTS:
{facts_str}

TONE RULES:
{tones_str}

CONTENT TO REVIEW:
"{text}"

Return ONLY valid JSON in this exact format:
{{
  "findings": [
    {{
      "type": "tone" or "fact_conflict" or "unsupported_claim",
      "rule_id": "exact-id-from-above-or-null",
      "status": "CONFLICT" or "UNVERIFIED",
      "explanation": "why this is an issue, referencing the rule",
      "original_snippet": "exact text from content",
      "suggested_fix": "corrected version or null",
      "severity": "low" or "medium" or "high"
    }}
  ]
}}
If no issues found, return {{"findings": []}}.
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )

    raw = json.loads(completion.choices[0].message.content)

    try:
        validated = CheckResponse(**raw)
        return [f.dict() for f in validated.findings]
    except ValidationError as e:
        print("AI returned invalid schema:", e)
        return []


def validate_citations(findings: list, rules: list) -> list:
    valid_ids = {r["id"] for r in rules}
    for f in findings:
        if f.get("rule_id") and f["rule_id"] not in valid_ids:
            f["rule_id"] = None
            f["status"] = "UNVERIFIED"
    return findings


@router.post("/")
def check_content(req: CheckRequest):
    rules_res = supabase.table("brand_rules").select("*").execute()
    rules = rules_res.data

    rule_based = run_rule_based_checks(req.text, rules)
    a11y = run_accessibility_checks(req.text)
    ai_raw = run_ai_checks(req.text, rules)
    ai_validated = validate_citations(ai_raw, rules)

    all_findings = rule_based + a11y + ai_validated

    version_res = supabase.table("content_versions").insert({
        "content_id": req.content_id,
        "text": req.text
    }).execute()

    version_id = version_res.data[0]["id"] if version_res.data else None

    if version_id:
        for f in all_findings:
            f_copy = {**f, "content_version_id": version_id}
            supabase.table("findings").insert(f_copy).execute()

    return {"findings": all_findings, "version_id": version_id}