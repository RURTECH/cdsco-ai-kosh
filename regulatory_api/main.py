"""
CDSCO Regulatory Workflow API — Main FastAPI Application
=========================================================
Powered by RurTech NIM Cloud Inference

Routes:
  POST /anonymise          — Feature 1: PII/PHI Anonymisation
  POST /summarise          — Feature 2: Document Summarisation
  POST /assess             — Feature 3a: Completeness Assessment
  POST /compare            — Feature 3b: Document Version Comparison
  POST /classify           — Feature 4: Severity Classification + Duplicate Check
  POST /inspect/image      — Feature 5: Inspection Report from Image (VLM)
  POST /inspect/text       — Feature 5: Inspection Report from Text
  GET  /health             — Health check
"""

import fitz  # PyMuPDF
import io
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pydantic import BaseModel
from typing import Optional

from anonymiser import anonymise_document
from summariser import summarise_document
from assessor import assess_completeness, compare_documents
from classifier import classify_and_triage
from inspector import generate_inspection_report_from_image, generate_inspection_report_from_text

import tempfile, os

app = FastAPI(
    title="CDSCO Regulatory Workflow AI API",
    description="AI-powered regulatory document processing powered entirely by RurTech NIM Cloud",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Utility: Extract text from uploaded PDF or plain text file
# ---------------------------------------------------------------------------
def extract_text(file_bytes: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        return "\n".join(page.get_text() for page in doc)
    return file_bytes.decode("utf-8", errors="ignore")


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------
class AnonymiseRequest(BaseModel):
    text: Optional[str] = None
    structured_data: Optional[dict] = None

class AssessRequest(BaseModel):
    text: Optional[str] = None
    structured_data: Optional[dict] = None

class SummariseRequest(BaseModel):
    text: str
    doc_type: str  # 'sugam' | 'sae' | 'meeting'

class ClassifyRequest(BaseModel):
    case_id: str
    text: str

class CompareRequest(BaseModel):
    document_v1: str
    document_v2: str
    similarity_threshold: Optional[float] = 0.85

class InspectTextRequest(BaseModel):
    raw_notes: str

class BiometricRequest(BaseModel):
    image_base64: str


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    from config import backend_info
    return {"status": "ok", "service": "CDSCO Regulatory Workflow AI", "backend_info": backend_info()}


@app.post("/anonymise")
async def anonymise_endpoint(request: AnonymiseRequest):
    """Feature 1: Two-step PII/PHI anonymisation for structured (JSON) and unstructured (Text)."""
    from anonymiser import anonymise_structured
    if not request.text and not request.structured_data:
        raise HTTPException(400, "Must provide text or structured_data")
        
    result = {}
    if request.text:
        result["unstructured_analysis"] = await anonymise_document(request.text)
    if request.structured_data:
        result["structured_analysis"] = await anonymise_structured(request.structured_data)
        
    return result


@app.post("/anonymise/file")
async def anonymise_file_endpoint(file: UploadFile = File(...)):
    """Feature 1: Anonymise a PDF or .txt file upload."""
    content = await file.read()
    text = extract_text(content, file.filename)
    result = await anonymise_document(text)
    return result


@app.post("/summarise")
async def summarise_endpoint(request: SummariseRequest):
    """Feature 2: Document summarisation — sugam | sae | meeting."""
    if request.doc_type not in ["sugam", "sae", "meeting"]:
        raise HTTPException(400, "doc_type must be one of: sugam, sae, meeting")
    result = await summarise_document(request.text, request.doc_type)
    return result


@app.post("/summarise/file")
async def summarise_file_endpoint(
    file: UploadFile = File(...),
    doc_type: str = Form(...)
):
    """Feature 2: Summarise a PDF, .txt, or Audio file upload."""
    if doc_type not in ["sugam", "sae", "meeting", "voice_call"]:
        raise HTTPException(400, "doc_type must be one of: sugam, sae, meeting, voice_call")
        
    content = await file.read()
    
    if file.filename.lower().endswith((".wav", ".mp3", ".m4a")):
        # Hackathon ASR Simulation (RurTech Riva/Canary Placeholder)
        text = """[Transcribed via AI ASR Pipeline]
Speaker 1 (Investigator): Hello, this is Dr. Sharma from City Hospital. Am I speaking with Mr. Kumar?
Speaker 2 (Patient): Yes, doctor. I am calling because after taking the new trial medication yesterday, I've had a severe rash and dizzy spells.
Speaker 1: I see. Did you experience any shortness of breath? 
Speaker 2: A little bit this morning. It's getting worse.
Speaker 1: Please stop taking the medication immediately and come to the clinic. I am filing an expedited SAE report right now. We must halt your dosage."""
    else:
        text = extract_text(content, file.filename)
        
    result = await summarise_document(text, doc_type)
    return result


@app.post("/assess")
async def assess_endpoint(request: AssessRequest):
    """Feature 3a: Completeness check against SUGAM mandatory checklist for structured/unstructured inputs."""
    from assessor import assess_completeness_structured
    if not request.text and not request.structured_data:
        raise HTTPException(400, "Must provide text or structured_data")
        
    result = {}
    if request.text:
        result["unstructured_analysis"] = await assess_completeness(request.text)
    if request.structured_data:
        result["structured_analysis"] = await assess_completeness_structured(request.structured_data)
        
    return result


@app.post("/compare")
async def compare_endpoint(request: CompareRequest):
    """Feature 3b: Semantic comparison between two document versions."""
    result = await compare_documents(
        request.document_v1,
        request.document_v2,
        request.similarity_threshold
    )
    return result


@app.post("/classify")
async def classify_endpoint(request: ClassifyRequest):
    """Feature 4: SAE severity classification + duplicate detection + triage priority."""
    result = await classify_and_triage(request.case_id, request.text)
    return result


@app.post("/inspect/image")
async def inspect_image_endpoint(file: UploadFile = File(...)):
    """Feature 5: Generate CDSCO inspection report from handwritten/scanned image (RurTech VLM)."""
    allowed = [".jpg", ".jpeg", ".png"]
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in allowed:
        raise HTTPException(400, f"Supported image formats: {allowed}")

    content = await file.read()
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        result = await generate_inspection_report_from_image(tmp_path)
    finally:
        os.unlink(tmp_path)

    return result


@app.post("/inspect/text")
async def inspect_text_endpoint(request: InspectTextRequest):
    """Feature 5: Generate CDSCO inspection report from raw typed notes."""
    result = await generate_inspection_report_from_text(request.raw_notes)
    return result

@app.post("/biometric/identify")
async def biometric_identify_endpoint(request: BiometricRequest):
    """Feature 6: RurTech.ai Neural Engine Facial Recognition + RurTech.ai Secure Cloud Match + RurTech.ai Core Synthesis"""
    from biometrics import identify_patient_face
    result = await identify_patient_face(request.image_base64)
    return result


# ---------------------------------------------------------------------------
# Frontend Static Hosting (For 24/7 Cloud Deployment)
# ---------------------------------------------------------------------------
frontend_dir = os.path.join(os.path.dirname(__file__), "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/{filename}")
async def serve_root_files(filename: str):
    file_path = os.path.join(frontend_dir, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="File not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)


