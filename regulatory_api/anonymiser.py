"""
Feature 1: AI-Powered Data Anonymisation (PII/PHI)
--------------------------------------------------
Two-step pipeline:
  Step 1 — Pseudonymisation: Replace identifiers with secure tokens (reversible, stored in vault)
  Step 2 — Irreversible Anonymisation: Generalise residual sensitive info via RurTech NIM LLM

Compliant with: DPDP Act 2023, NDHM, ICMR, CDSCO guidelines
"""

import re
import hashlib
import json
from config import get_client, get_model

# ---------------------------------------------------------------------------
# Rule-based Indian PII recogniser patterns
# ---------------------------------------------------------------------------
INDIAN_PII_PATTERNS = {
    "AADHAAR":      r"\b[2-9]{1}[0-9]{3}\s?[0-9]{4}\s?[0-9]{4}\b",
    "PAN":          r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
    "INDIAN_PHONE": r"\b(\+91[\-\s]?)?[6-9]\d{9}\b",
    "PASSPORT_IN":  r"\b[A-Z]{1}[0-9]{7}\b",
    "VOTER_ID":     r"\b[A-Z]{3}[0-9]{7}\b",
    "EMAIL":        r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Z|a-z]{2,}\b",
    "DOB":          r"\b(0?[1-9]|[12][0-9]|3[01])[\/\-](0?[1-9]|1[0-2])[\/\-](\d{2}|\d{4})\b",
    "IP_ADDRESS":   r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
    "MRN":          r"\bMRN[\-:\s]?[A-Z0-9]{6,12}\b",
}

# In-memory pseudonymisation vault (use encrypted DB in production)
_token_vault: dict = {}

def _generate_token(entity_type: str, value: str) -> str:
    """Create a deterministic, collision-resistant token for pseudonymisation."""
    h = hashlib.sha256(value.encode()).hexdigest()[:10].upper()
    return f"[{entity_type}_{h}]"

def rule_based_pseudonymise(text: str) -> tuple[str, dict]:
    """Step 1: Replace Indian PII via regex → secure tokens."""
    replacements = {}
    for entity_type, pattern in INDIAN_PII_PATTERNS.items():
        matches = re.findall(pattern, text)
        for match in matches:
            raw = match if isinstance(match, str) else " ".join(match)
            token = _generate_token(entity_type, raw)
            _token_vault[token] = raw       # store in vault for reversal
            replacements[raw] = token
            text = text.replace(raw, token)
    return text, replacements

async def llm_anonymise(text: str) -> str:
    """
    Step 2: Send pseudonymised text to active backend (NIM Cloud or Ollama).
    The LLM finds residual contextual PII/PHI missed by regex
    (e.g. relative addresses, disease specifics) and generalises them.
    """
    client = get_client()

    system_prompt = """You are a medical data privacy officer compliant with India's DPDP Act 2023, NDHM, ICMR, and CDSCO guidelines.
Your task is to perform IRREVERSIBLE ANONYMISATION on the text below.
Rules:
1. Replace any remaining patient names with [PATIENT_ID].
2. Replace specific ages with generalised age bands: e.g. "45 years old" → "[AGE_GROUP: 40-50]".
3. Replace specific diagnosis details with generalised categories: e.g. "Stage 4 Glioblastoma" → "[SEVERE_NEUROLOGICAL_ONCOLOGY]".
4. Replace hospital/clinic names with [HEALTHCARE_FACILITY].
5. Replace doctor names with [HCP_ID].
6. Replace all geographical details more specific than state level with [LOCATION].
7. DO NOT change clinical measurements, dosages, or timelines — these are needed for regulatory review.
8. Return ONLY the anonymised text. No explanations."""

    response = client.chat.completions.create(
        model=get_model("guardrail"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text}
        ],
        temperature=0.0,
        max_tokens=4096
    )
    return response.choices[0].message.content

async def anonymise_document(text: str) -> dict:
    """Full two-step anonymisation pipeline."""
    # Step 1: Rule-based pseudonymisation
    pseudonymised, replacements = rule_based_pseudonymise(text)

    # Step 2: LLM-based irreversible anonymisation
    anonymised = await llm_anonymise(pseudonymised)

    return {
        "original_length": len(text),
        "anonymised_text": anonymised,
        "pii_detected_count": len(replacements),
        "entities_replaced": list(replacements.values()),
        "compliance": ["DPDP Act 2023", "NDHM", "ICMR", "CDSCO"],
        "reversible_step": "pseudonymisation (vault secured)",
        "irreversible_step": "llm_generalisation"
    }

async def anonymise_structured(data: dict) -> dict:
    """Anonymise structured data (forms, databases) while preserving schema.
    Uses a strict system prompt to ensure JSON schema is maintained."""
    client = get_client()
    json_str = json.dumps(data, indent=2)
    
    system_prompt = """You are a CDSCO medical data privacy officer.
Perform IRREVERSIBLE ANONYMISATION on this STRUCTURED JSON data.
Rules:
1. Preserve all JSON keys and schema structure exactly.
2. Replace values containing PII/PHI with tokens (e.g. [PATIENT_ID], [AGE_GROUP], [HEALTHCARE_FACILITY], [LOCATION]).
3. Do not alter non-sensitive clinical values or measurements.
4. Output ONLY valid JSON, no markdown formatting."""

    response = client.chat.completions.create(
        model=get_model("guardrail"), # Utilizing RurTech NIM Guardrail/LLM
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
        return {
            "original_keys": list(data.keys()),
            "anonymised_data": json.loads(raw.strip()),
            "compliance": ["DPDP Act 2023", "NDHM"],
            "model_used": get_model("guardrail")
        }
    except Exception:
        return {"error": "Failed to parse anonymised JSON", "raw": raw}


