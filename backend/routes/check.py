import os
import re
import json
from fastapi import APIRouter
from openai import OpenAI
from pydantic import ValidationError
from models import CheckRequest, CheckResponse
from database import supabase

router = APIRouter()
client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)


def run_rule_based_checks(text: str, rules: list) -> list:
    findings = []
    term_rules = [r for r in rules if r["type"] == "terminology"]

    # 1. Terminology checks (case-insensitive search, exact match capture)
    for rule in term_rules:
        avoid_term = rule.get("avoid_term")
        if not avoid_term:
            continue
        match = re.search(re.escape(avoid_term), text, re.IGNORECASE)
        if match:
            findings.append({
                "type": "terminology",
                "rule_id": rule["id"],
                "status": "CONFLICT",
                "explanation": f'Guideline "{rule["title"]}" states: {rule["content"]}',
                "original_snippet": match.group(0),  # Preserves actual casing from content
                "suggested_fix": rule["preferred_term"],
                "severity": "medium",
            })

    # 2. Tone / Exclamation checks
    if re.search(r"!{2,}", text):
        match = re.search(r"\S*!{2,}\S*", text)
        snippet = match.group(0) if match else "!!"
        findings.append({
            "type": "tone",
            "rule_id": None,
            "status": "CONFLICT",
            "explanation": "Multiple exclamation marks detected — may appear unprofessional.",
            "original_snippet": snippet,
            "suggested_fix": re.sub(r"!{2,}", ".", snippet),  # Fixes snippet only, NOT whole text
            "severity": "low",
        })

    return findings


def run_accessibility_checks(text: str) -> list:
    findings = []
    match = re.search(r"click here", text, re.IGNORECASE)
    if match:
        findings.append({
            "type": "accessibility",
            "rule_id": None,
            "status": "CONFLICT",
            "explanation": "Vague link text like 'click here' is not accessible for screen readers.",
            "original_snippet": match.group(0),
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

IMPORTANT: "original_snippet" MUST be an EXACT, character-for-character substring copied directly from CONTENT TO REVIEW above. Do not reword or paraphrase. If you cannot extract an exact substring, set "original_snippet" to null.

If no issues found, return {{"findings": []}}.
"""

    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.2,
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