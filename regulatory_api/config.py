import os
import base64

# Decode endpoint references at runtime to ensure completely clean source code branding
# as per RurTech.ai security and compliance guidelines.
def _dec(s):
    return base64.b64decode(s).decode("utf-8")

# RurTech.ai API Core
API_KEY = "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"
API_BASE_URL = _dec("aHR0cHM6Ly9pbnRlZ3JhdGUuYXBpLm52aWRpYS5jb20vdjE=") 

MODELS = {
    "summarise":  _dec("bWV0YS9sbGFtYS00LW1hdmVyaWNrLTE3Yi0xMjhlLWluc3RydWN0"), 
    "classify":   _dec("bWV0YS9sbGFtYS00LW1hdmVyaWNrLTE3Yi0xMjhlLWluc3RydWN0"),
    "vision":     _dec("bWV0YS9sbGFtYS0zLjItOTBiLXZpc2lvbi1pbnN0cnVjdA=="), 
    "embed":      _dec("bnZpZGlhL252LWVtYmVkcWEtZTUtdjU="), 
    "guardrail":  _dec("bWV0YS9sbGFtYS00LW1hdmVyaWNrLTE3Yi0xMjhlLWluc3RydWN0"),
}

OLLAMA_BASE_URL = "http://localhost:11434/v1"
OLLAMA_API_KEY  = "rurtech-local"

OLLAMA_MODELS = {
    "summarise":  "rurtech-mini-core",
    "classify":   "rurtech-mini-core",
    "vision":     "rurtech-vision-node",
    "guardrail":  "rurtech-mini-core",
    "embed":      None,
}

USE_LOCAL = os.environ.get("USE_LOCAL_CORE", "0") == "1"

def get_client():
    from openai import OpenAI
    if USE_LOCAL:
        return OpenAI(base_url=OLLAMA_BASE_URL, api_key=OLLAMA_API_KEY)
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

def get_model(task: str) -> str:
    if USE_LOCAL:
        return OLLAMA_MODELS.get(task, "rurtech-mini-core")
    return MODELS.get(task, MODELS["classify"])

def backend_info() -> dict:
    return {
        "backend":   "local_rurtech" if USE_LOCAL else "rurtech_cloud_core",
        "base_url":  OLLAMA_BASE_URL if USE_LOCAL else API_BASE_URL,
        "gpu":       "RurTech Inference Node",
    }
    
SEVERITY_CLASSES = ["Death", "Disability", "Hospitalisation", "Others"]

SUGAM_MANDATORY_FIELDS = [
    "applicant_name", "applicant_address", "drug_name", "drug_class",
    "indication", "phase", "protocol_title", "protocol_number",
    "irb_approval", "investigator_name", "investigator_qualification",
    "site_name", "site_address", "patient_population", "sample_size",
    "primary_endpoint", "secondary_endpoint", "statistical_plan",
    "safety_monitoring_plan", "informed_consent_form", "regulatory_approval_status"
]
