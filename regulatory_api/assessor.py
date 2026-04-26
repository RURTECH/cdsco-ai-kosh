"""
Feature 3: Completeness Assessment & Document Comparison
---------------------------------------------------------
A) Completeness Check: Validates document against SUGAM mandatory checklist via LLM JSON extraction
B) Document Comparison: Uses RurTech NIM Embeddings for semantic diff + LLM for human-readable diff report
"""

import json
import re
from config import get_client, get_model, SUGAM_MANDATORY_FIELDS

client = get_client()


# ---------------------------------------------------------------------------
# A) Completeness Assessment
# ---------------------------------------------------------------------------
async def assess_completeness(document_text: str, doc_type: str = "sugam_ct") -> dict:
    """
    Extract key fields from document using RurTech NIM in JSON mode.
    Returns a completeness report with missing/incomplete fields flagged.
    """
    fields_list = "\n".join(f"- {f}" for f in SUGAM_MANDATORY_FIELDS)

    system_prompt = f"""You are a CDSCO regulatory compliance checker.
Extract the following fields from the provided document and return a valid JSON object.
For each field, provide the extracted value or null if absent/unclear.

Fields to extract:
{fields_list}

Return ONLY a valid JSON object. No markdown, no explanation."""

    response = client.chat.completions.create(
        model=get_model("classify"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": document_text[:60000]}   # 8B model context limit
        ],
        temperature=0.0,
        max_tokens=2048
    )

    raw = response.choices[0].message.content
    try:
        extracted = json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: extract JSON from response
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        extracted = json.loads(match.group()) if match else {}

    # Compute missing and incomplete fields
    missing = [f for f in SUGAM_MANDATORY_FIELDS if extracted.get(f) is None]
    present = [f for f in SUGAM_MANDATORY_FIELDS if extracted.get(f) is not None]
    completeness_pct = round((len(present) / len(SUGAM_MANDATORY_FIELDS)) * 100, 1)

    return {
        "document_type": doc_type,
        "completeness_percentage": completeness_pct,
        "total_fields": len(SUGAM_MANDATORY_FIELDS),
        "present_fields": len(present),
        "missing_fields": missing,
        "extracted_data": extracted,
        "status": "COMPLETE" if completeness_pct == 100 else "INCOMPLETE" if completeness_pct >= 70 else "CRITICALLY_INCOMPLETE",
        "reviewer_action": "Proceed" if completeness_pct >= 90 else "Query Applicant" if completeness_pct >= 60 else "Return Application"
    }

async def assess_completeness_structured(data: dict, doc_type: str = "sugam_ct") -> dict:
    """
    Assess completeness of structured data (JSON/DB) against CDSCO SUGAM fields via LLM.
    The LLM maps the provided JSON keys to the mandatory checklist and verifies completeness.
    """
    fields_list = "\n".join(f"- {f}" for f in SUGAM_MANDATORY_FIELDS)
    json_str = json.dumps(data, indent=2)

    system_prompt = f"""You are a CDSCO regulatory compliance checker.
Review the following structured JSON submission.
Map the provided data fields to the SUGAM mandatory checklist below.
Determine if each mandatory field is satisfied by the data.

SUGAM Mandatory Fields:
{fields_list}

Return a JSON object with:
1. "extracted_data": A dictionary mapping the mandatory field names to the values found in the input data (or null if missing).
2. "unmapped_data": Any extra fields provided in the input that don't map to the checklist.

Return ONLY a valid JSON object. No markdown, no explanation."""

    response = client.chat.completions.create(
        model=get_model("classify"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": json_str}
        ],
        temperature=0.0
    )

    raw = response.choices[0].message.content
    try:
        if raw.startswith("```json"):
            raw = raw[7:-3]
        elif raw.startswith("```"):
            raw = raw[3:-3]
        result = json.loads(raw.strip())
        extracted = result.get("extracted_data", {})
    except Exception:
        extracted = {}

    missing = [f for f in SUGAM_MANDATORY_FIELDS if not extracted.get(f)]
    present = [f for f in SUGAM_MANDATORY_FIELDS if extracted.get(f)]
    completeness_pct = round((len(present) / len(SUGAM_MANDATORY_FIELDS)) * 100, 1)

    return {
        "document_type": f"{doc_type}_structured",
        "completeness_percentage": completeness_pct,
        "total_fields": len(SUGAM_MANDATORY_FIELDS),
        "present_fields": len(present),
        "missing_fields": missing,
        "extracted_data": extracted,
        "status": "COMPLETE" if completeness_pct == 100 else "INCOMPLETE" if completeness_pct >= 70 else "CRITICALLY_INCOMPLETE",
        "reviewer_action": "Proceed" if completeness_pct >= 90 else "Query Applicant" if completeness_pct >= 60 else "Return Application"
    }

# ---------------------------------------------------------------------------
# B) Document Comparison / Version Diff
# ---------------------------------------------------------------------------
def _chunk_text(text: str, chunk_size: int = 500) -> list[str]:
    """Split text into overlapping chunks for embedding comparison."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - 50):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
    return chunks

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x ** 2 for x in a) ** 0.5
    norm_b = sum(x ** 2 for x in b) ** 0.5
    return dot / (norm_a * norm_b + 1e-9)

def _get_embeddings(texts: list[str]) -> list[list[float]]:
    """Get RurTech NIM embeddings for a list of text chunks."""
    model_name = get_model("embed")
    if not model_name:
        return [[0.0] * 1024 for _ in texts]
    response = client.embeddings.create(
        model=model_name,
        input=texts,
        encoding_format="float",
        extra_body={"input_type": "query", "truncate": "END"}
    )
    return [item.embedding for item in response.data]

async def compare_documents(doc_v1: str, doc_v2: str, threshold: float = 0.85) -> dict:
    """
    Compare two document versions using RurTech embeddings.
    Sections with cosine similarity below threshold are flagged as changed.
    Then LLM generates a human-readable diff report.
    """
    chunks_v1 = _chunk_text(doc_v1)
    chunks_v2 = _chunk_text(doc_v2)

    # Get embeddings via RurTech NIM
    emb_v1 = _get_embeddings(chunks_v1[:50])  # API batch limit
    emb_v2 = _get_embeddings(chunks_v2[:50])

    # Find changed sections
    changed_sections = []
    min_len = min(len(emb_v1), len(emb_v2))
    for i in range(min_len):
        sim = _cosine_similarity(emb_v1[i], emb_v2[i])
        if sim < threshold:
            changed_sections.append({
                "section_index": i,
                "similarity_score": round(sim, 4),
                "v1_snippet": chunks_v1[i][:300],
                "v2_snippet": chunks_v2[i][:300],
                "change_magnitude": "Major" if sim < 0.6 else "Moderate" if sim < 0.75 else "Minor"
            })

    # LLM-generated diff report for top changed sections
    top_changes = changed_sections[:5]  # Summarise most significant changes
    diff_context = "\n\n".join([
        f"Section {c['section_index']+1} [{c['change_magnitude']}]:\n"
        f"V1: {c['v1_snippet']}\nV2: {c['v2_snippet']}"
        for c in top_changes
    ])

    llm_report = ""
    if diff_context:
        diff_response = client.chat.completions.create(
            model=get_model("summarise"),
            messages=[
                {"role": "system", "content": "You are a regulatory document analyst. Describe the substantive changes between the two document versions below. Focus on regulatory significance: changes to endpoints, patient populations, dosing, safety data, or form fields. Be concise and structured."},
                {"role": "user", "content": diff_context}
            ],
            temperature=0.1,
            max_tokens=1024
        )
        llm_report = diff_response.choices[0].message.content

    return {
        "total_sections_compared": min_len,
        "changed_sections_count": len(changed_sections),
        "unchanged_sections_count": min_len - len(changed_sections),
        "change_rate_percent": round((len(changed_sections) / max(min_len, 1)) * 100, 1),
        "changed_sections": changed_sections,
        "llm_diff_report": llm_report,
        "embedding_model": get_model("embed"),
        "similarity_threshold_used": threshold
    }

