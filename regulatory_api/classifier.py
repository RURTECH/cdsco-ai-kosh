"""
Feature 4: Classification Tool
--------------------------------
A) Severity classification: Death / Disability / Hospitalisation / Others
B) Duplicate detection: Using RurTech NIM Embeddings + cosine similarity
C) Priority scoring: Composite score to help officers triage efficiently
"""

import json
import re
from config import get_client, get_model, SEVERITY_CLASSES

client = get_client()

# In-memory embedding store — use a vector DB (Milvus/pgvector) in production
_case_store: list[dict] = []   # {"case_id": str, "embedding": list[float], "summary": str}


def _get_single_embedding(text: str) -> list[float]:
    """Get RurTech NIM embedding for a single text."""
    model_name = get_model("embed")
    if not model_name:
        return [0.0] * 1024
    response = client.embeddings.create(
        model=model_name,
        input=[text[:2000]],
        encoding_format="float",
        extra_body={"input_type": "query", "truncate": "END"}
    )
    return response.data[0].embedding

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot / (norm_a * norm_b + 1e-9)


# ---------------------------------------------------------------------------
# A) Severity Classification
# ---------------------------------------------------------------------------
async def classify_severity(case_text: str) -> dict:
    """Classify SAE case into severity categories using RurTech NIM."""
    system_prompt = f"""You are a pharmacovigilance expert at CDSCO India.
Classify the following Adverse Event case into exactly one severity category.

Categories (per CDSCO/ICH E2A guidelines):
- Death: Event resulted in patient death
- Disability: Significant, persistent, or permanent disability
- Hospitalisation: Required initial or prolonged hospitalisation
- Others: All other serious events (life-threatening, congenital anomaly, medically important)

Return a valid JSON with this structure:
{{
  "severity_class": "<one of: Death|Disability|Hospitalisation|Others>",
  "confidence": <0.0 to 1.0>,
  "rationale": "<one sentence justification>",
  "priority_flag": "<High|Medium|Low>",
  "expedited_report_required": <true|false>,
  "report_timeline": "<7-day|15-day|Annual|Not required>"
}}"""

    response = client.chat.completions.create(
        model=get_model("classify"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": case_text[:8000]}
        ],
        temperature=0.0,
        max_tokens=512
    )

    raw = response.choices[0].message.content
    try:
        result = json.loads(raw)
    except Exception:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        result = json.loads(match.group()) if match else {"error": "Parse failed", "raw": raw}

    return result


# ---------------------------------------------------------------------------
# B) Duplicate Detection
# ---------------------------------------------------------------------------
async def check_duplicate(case_id: str, case_text: str, similarity_threshold: float = 0.92) -> dict:
    """
    Detect if a case is a duplicate by comparing its embedding
    against all stored cases using RurTech NIM Embeddings.
    """
    new_embedding = _get_single_embedding(case_text)

    duplicates = []
    for stored in _case_store:
        sim = _cosine_similarity(new_embedding, stored["embedding"])
        if sim >= similarity_threshold:
            duplicates.append({
                "matched_case_id": stored["case_id"],
                "similarity_score": round(sim, 4),
                "is_exact_duplicate": sim >= 0.99
            })

    # Store this case for future comparisons
    _case_store.append({
        "case_id": case_id,
        "embedding": new_embedding,
        "summary": case_text[:200]
    })

    return {
        "case_id": case_id,
        "is_duplicate": len(duplicates) > 0,
        "duplicate_count": len(duplicates),
        "matches": duplicates,
        "total_cases_in_store": len(_case_store)
    }


# ---------------------------------------------------------------------------
# C) Combined Classification + Duplicate Check (main entry point)
# ---------------------------------------------------------------------------
async def classify_and_triage(case_id: str, case_text: str) -> dict:
    """Full triage: classify severity + check for duplicates."""
    severity = await classify_severity(case_text)
    duplicate = await check_duplicate(case_id, case_text)

    # Compute priority score (higher = review first)
    priority_map = {"Death": 10, "Disability": 8, "Hospitalisation": 6, "Others": 3}
    base_score = priority_map.get(severity.get("severity_class", "Others"), 3)
    is_dup_penalty = -5 if duplicate["is_duplicate"] else 0
    priority_score = base_score + is_dup_penalty

    return {
        "case_id": case_id,
        "severity_classification": severity,
        "duplicate_analysis": duplicate,
        "priority_score": max(priority_score, 0),
        "reviewer_action": (
            "URGENT — Review immediately" if priority_score >= 8 else
            "STANDARD — Review within 15 days" if priority_score >= 4 else
            "LOW — Possible duplicate, verify before processing"
        )
    }

