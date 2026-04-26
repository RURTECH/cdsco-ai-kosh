"""
Feature 5: Inspection Report Generation
-----------------------------------------
Converts unstructured/handwritten site inspection observations
into standardised CDSCO formal inspection reports via RurTech VLM (Vision-Language Model).

Supports: Scanned PDFs, JPG/PNG images of handwritten notes, typed text
"""

import base64
import json
import re
from pathlib import Path
from config import get_client, get_model

client = get_client()

CDSCO_INSPECTION_TEMPLATE = """
## CDSCO SITE INSPECTION REPORT

**Report Number:** [AUTO-GENERATED]
**Inspection Date:** {inspection_date}
**Site Name:** {site_name}
**Site Address:** {site_address}
**Inspectors:** {inspectors}
**Inspection Type:** {inspection_type}

---

### 1. SCOPE OF INSPECTION
{scope}

### 2. OBSERVATIONS

#### 2a. Critical Observations (Major Non-Compliances)
{critical_observations}

#### 2b. Major Observations
{major_observations}

#### 2c. Minor Observations
{minor_observations}

### 3. GOOD PRACTICES NOTED
{good_practices}

### 4. CORRECTIVE ACTION REQUIRED
{corrective_actions}

### 5. RESPONSE DEADLINE
{response_deadline}

### 6. INSPECTOR'S DECLARATION
This report accurately reflects observations made during the site inspection.

**Signatures:** {inspector_signatures}
**Date of Report:** {report_date}
"""

def _encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 for VLM API."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

async def generate_inspection_report_from_image(image_path: str) -> dict:
    """
    Use RurTech NIM Vision Model to:
    1. Extract text from handwritten/scanned inspection notes
    2. Structure them into official CDSCO template
    """
    image_data = _encode_image_to_base64(image_path)
    ext = Path(image_path).suffix.lower()
    mime_type = "image/png" if ext == ".png" else "image/jpeg"

    system_prompt = """You are a CDSCO regulatory affairs officer digitising a handwritten site inspection report.
Extract ALL text from the image and structure it into the CDSCO inspection report format.

Return a valid JSON object with these keys:
{
  "inspection_date": "...",
  "site_name": "...",
  "site_address": "...",
  "inspectors": "...",
  "inspection_type": "...",
  "scope": "...",
  "critical_observations": "...",
  "major_observations": "...",
  "minor_observations": "...",
  "good_practices": "...",
  "corrective_actions": "...",
  "response_deadline": "...",
  "inspector_signatures": "...",
  "report_date": "...",
  "raw_extracted_text": "... (full verbatim extraction from image)"
}
If a field is not found in the image, use "Not specified"."""

    response = client.chat.completions.create(
        model=get_model("vision"),
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract and structure the inspection observations from this image:"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{image_data}"}
                    }
                ]
            }
        ],
        temperature=0.0,
        max_tokens=2048
    )

    raw = response.choices[0].message.content
    try:
        fields = json.loads(raw)
    except Exception:
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        fields = json.loads(match.group()) if match else {}

    # Fill CDSCO template
    formatted_report = CDSCO_INSPECTION_TEMPLATE.format(**{
        k: fields.get(k, "Not specified") for k in [
            "inspection_date", "site_name", "site_address", "inspectors",
            "inspection_type", "scope", "critical_observations",
            "major_observations", "minor_observations", "good_practices",
            "corrective_actions", "response_deadline", "inspector_signatures", "report_date"
        ]
    })

    return {
        "source_image": image_path,
        "extracted_fields": fields,
        "formatted_report": formatted_report,
        "model_used": get_model("vision"),
        "status": "SUCCESS"
    }

async def generate_inspection_report_from_text(raw_notes: str) -> dict:
    """Fallback: generate structured report from typed/pasted raw notes."""
    system_prompt = """You are a CDSCO regulatory affairs officer. 
Structure these unorganised inspection notes into a formal CDSCO inspection report.
Return a valid JSON object with the same fields as the vision extraction endpoint."""

    response = client.chat.completions.create(
        model=get_model("summarise"),   # Use 70B for text-only
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": raw_notes[:20000]}
        ],
        temperature=0.0,
        max_tokens=2048,
        response_format={"type": "json_object"}
    )

    fields = json.loads(response.choices[0].message.content)
    formatted_report = CDSCO_INSPECTION_TEMPLATE.format(**{
        k: fields.get(k, "Not specified") for k in [
            "inspection_date", "site_name", "site_address", "inspectors",
            "inspection_type", "scope", "critical_observations",
            "major_observations", "minor_observations", "good_practices",
            "corrective_actions", "response_deadline", "inspector_signatures", "report_date"
        ]
    })

    return {
        "source": "text_input",
        "extracted_fields": fields,
        "formatted_report": formatted_report,
        "model_used": get_model("summarise")
    }

