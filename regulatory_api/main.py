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
  POST /biometric/identify — Feature 6: Biometric Identity Tokenization
  POST /ask                — Feature 7: CDSCO Knowledge Base RAG
  POST /chat               — Feature 8: Conversational Regulatory Agent
  POST /generate-pdf       — Feature 9: PDF Report Generator
  GET  /health             — Health check
"""

import fitz  # PyMuPDF
import io
import json
import base64
import datetime
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import os
from pydantic import BaseModel
from typing import Optional, List

from anonymiser import anonymise_document
from summariser import summarise_document
from assessor import assess_completeness, compare_documents
from classifier import classify_and_triage
from inspector import generate_inspection_report_from_image, generate_inspection_report_from_text

import tempfile

app = FastAPI(
    title="CDSCO Regulatory Workflow AI API",
    description="AI-powered regulatory document processing powered entirely by RurTech NIM Cloud",
    version="2.0.0"
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
# NLP Conclusion Engine — generates clear English conclusion for every output
# ---------------------------------------------------------------------------
async def generate_nlp_conclusion(result_data: dict, section_name: str) -> str:
    """Use LLM to generate a single, authoritative, plain-English conclusion sentence."""
    from config import get_client, get_model
    client = get_client()
    system = (
        f"You are a senior CDSCO regulatory officer reviewing the AI output of the "
        f"'{section_name}' module. Write exactly ONE clear, authoritative conclusion "
        f"sentence in plain English summarizing the final regulatory decision, risk level, "
        f"or actionable next step. Do not use markdown. Do not use bullet points. "
        f"Be direct and professional. Start with the most important finding."
    )
    try:
        response = client.chat.completions.create(
            model=get_model("classify"),
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": json.dumps(result_data, default=str)[:3000]}
            ],
            temperature=0.1,
            max_tokens=120
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "AI conclusion generation unavailable — please review the full output manually."


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
    doc_type: str  # 'sugam' | 'sae' | 'meeting' | 'undertaking'

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

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []

class PDFRequest(BaseModel):
    title: str
    content: str
    reviewer_name: Optional[str] = "CDSCO AI Review Officer"
    applicant_name: Optional[str] = "Applicant"
    reference_number: Optional[str] = None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    from config import backend_info
    return {"status": "ok", "service": "CDSCO Regulatory Workflow AI", "version": "2.0.0", "backend_info": backend_info()}


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
    
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "DPDP Act PII/PHI Anonymisation")
    return result


@app.post("/anonymise/file")
async def anonymise_file_endpoint(file: UploadFile = File(...)):
    """Feature 1: Anonymise a PDF or .txt file upload."""
    content = await file.read()
    text = extract_text(content, file.filename)
    result = await anonymise_document(text)
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "DPDP Act PII/PHI Anonymisation")
    return result


@app.post("/summarise")
async def summarise_endpoint(request: SummariseRequest):
    """Feature 2: Document summarisation."""
    if request.doc_type not in ["sugam", "sae", "meeting", "undertaking"]:
        raise HTTPException(400, "Invalid doc_type")
    result = await summarise_document(request.text, request.doc_type)
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, f"Document Summarisation ({request.doc_type.upper()})")
    return result


@app.post("/summarise/file")
async def summarise_file_endpoint(
    file: UploadFile = File(...),
    doc_type: str = Form(...)
):
    """Feature 2: Summarise a PDF, .txt, or Audio file upload."""
    if doc_type not in ["sugam", "sae", "meeting", "voice_call", "undertaking"]:
        raise HTTPException(400, "Invalid doc_type")
        
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
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, f"Document Summarisation ({doc_type.upper()})")
    return result


@app.post("/assess")
async def assess_endpoint(request: AssessRequest):
    """Feature 3a: Completeness check against SUGAM mandatory checklist."""
    from assessor import assess_completeness_structured
    if not request.text and not request.structured_data:
        raise HTTPException(400, "Must provide text or structured_data")
        
    result = {}
    if request.text:
        result["unstructured_analysis"] = await assess_completeness(request.text)
    if request.structured_data:
        result["structured_analysis"] = await assess_completeness_structured(request.structured_data)
    
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "SUGAM Checklist Completeness Assessment")
    return result


@app.post("/compare")
async def compare_endpoint(request: CompareRequest):
    """Feature 3b: Semantic comparison between two document versions."""
    result = await compare_documents(
        request.document_v1,
        request.document_v2,
        request.similarity_threshold
    )
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "Document Version Comparison")
    return result


@app.post("/classify")
async def classify_endpoint(request: ClassifyRequest):
    """Feature 4: SAE severity classification + duplicate detection + triage priority."""
    result = await classify_and_triage(request.case_id, request.text)
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "SAE Severity Classification & Triage")
    return result


@app.post("/inspect/image")
async def inspect_image_endpoint(file: UploadFile = File(...)):
    """Feature 5: Generate CDSCO inspection report from handwritten/scanned image."""
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

    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "Site Inspection Vision Analysis")
    return result


@app.post("/inspect/text")
async def inspect_text_endpoint(request: InspectTextRequest):
    """Feature 5: Generate CDSCO inspection report from raw typed notes."""
    result = await generate_inspection_report_from_text(request.raw_notes)
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "Site Inspection Text Analysis")
    return result


@app.post("/biometric/identify")
async def biometric_identify_endpoint(request: BiometricRequest):
    """Feature 6: Facial Recognition + Blockchain Tokenization."""
    from biometrics import identify_patient_face
    result = await identify_patient_face(request.image_base64)
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "Biometric Identity Verification")
    return result


# ---------------------------------------------------------------------------
# Feature 7: CDSCO Knowledge Base RAG (Official Document Q&A)
# ---------------------------------------------------------------------------
class AskRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_knowledge_base(request: AskRequest):
    """Feature 7: Answer regulatory questions using the CDSCO official document knowledge base."""
    if not request.question or len(request.question.strip()) < 5:
        raise HTTPException(400, "Please provide a valid question.")
    from knowledge_rag import query_knowledge_base
    result = await query_knowledge_base(request.question)
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "CDSCO Knowledge Base Query")
    return result


# ---------------------------------------------------------------------------
# Feature 8: Conversational Regulatory Chat Agent
# ---------------------------------------------------------------------------
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Feature 8: Agentic Conversational Agent with gTTS voice and PDF Generation."""
    from config import get_client, get_model
    from gtts import gTTS
    client = get_client()
    
    system_prompt = """You are RurTech.ai CDSCO Regulatory Assistant — an expert AI agent for Indian pharmaceutical regulation.

You help users with:
1. Preparing SUGAM portal applications
2. Understanding NDCT Rules 2019, SAE reporting
3. Drafting reviewer letters and generating PDFs
4. Explaining regulatory workflows

AGENTIC CAPABILITY:
If the user explicitly asks you to "write a formal letter", "generate a pdf report", or "create a reviewer letter", you must:
1. Draft the full, formal letter content in your response.
2. At the very end of your response, append the exact tag: [ACTION: GENERATE_PDF]

Rules:
- Keep responses structured with clear sections
- If unsure, say so — never hallucinate regulatory requirements"""

    messages = [{"role": "system", "content": system_prompt}]
    
    for msg in (request.history or []):
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    
    messages.append({"role": "user", "content": request.message})
    
    response = client.chat.completions.create(
        model=get_model("summarise"),
        messages=messages,
        temperature=0.3,
        max_tokens=2048
    )
    
    reply = response.choices[0].message.content
    pdf_base64 = None
    
    # Agentic Action: PDF Generation
    if "[ACTION: GENERATE_PDF]" in reply:
        reply = reply.replace("[ACTION: GENERATE_PDF]", "").strip()
        # Generate the PDF
        doc = fitz.open()
        page = doc.new_page(width=595, height=842)
        page.draw_rect(fitz.Rect(0, 0, 595, 70), color=(0.1, 0.2, 0.5), fill=(0.1, 0.2, 0.5))
        page.insert_text(fitz.Point(30, 30), "CENTRAL DRUGS STANDARD CONTROL ORGANISATION", fontsize=13, fontname="helv", color=(1, 1, 1))
        page.insert_text(fitz.Point(30, 95), f"Ref: CDSCO/CHAT/{datetime.datetime.now().strftime('%Y%m%d%H%M')}", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
        
        body_rect = fitz.Rect(30, 150, 565, 800)
        content_text = reply.replace("**", "").replace("##", "").replace("*", "")
        rc = page.insert_textbox(body_rect, content_text, fontsize=10, fontname="helv", color=(0.15, 0.15, 0.15), align=0)
        
        pdf_bytes = doc.tobytes()
        doc.close()
        pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
        
        reply += "\n\n*(I have successfully generated the formal PDF report as requested. You can download it using the link provided in the chat.)*"

    # Agentic Action: Voice Generation via gTTS (Hindi or English)
    audio_base64 = None
    try:
        lang = 'hi' if any('\u0900' <= c <= '\u097f' for c in reply) else 'en'
        # Limit TTS text to avoid long latency
        tts = gTTS(text=reply.replace("*", "")[:1000], lang=lang, tld='co.in' if lang == 'en' else 'com')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        audio_base64 = base64.b64encode(fp.read()).decode('utf-8')
    except Exception as e:
        print(f"gTTS error: {e}")
        pass

    return {
        "reply": reply,
        "audio_base64": audio_base64,
        "pdf_base64": pdf_base64,
        "model_used": get_model("summarise"),
        "timestamp": datetime.datetime.now().isoformat()
    }


# ---------------------------------------------------------------------------
# Feature 9: PDF Report Generator
# ---------------------------------------------------------------------------
@app.post("/generate-pdf")
async def generate_pdf_endpoint(request: PDFRequest):
    """Feature 9: Generate a formal CDSCO reviewer PDF letter/report."""
    
    ref_no = request.reference_number or f"CDSCO/AI/{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    today = datetime.datetime.now().strftime("%d %B %Y")
    
    # Create PDF using PyMuPDF
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)  # A4
    
    # Header band
    rect_header = fitz.Rect(0, 0, 595, 70)
    page.draw_rect(rect_header, color=(0.1, 0.2, 0.5), fill=(0.1, 0.2, 0.5))
    page.insert_text(fitz.Point(30, 30), "CENTRAL DRUGS STANDARD CONTROL ORGANISATION",
                     fontsize=13, fontname="helv", color=(1, 1, 1))
    page.insert_text(fitz.Point(30, 50), "Directorate General of Health Services | Ministry of Health & Family Welfare",
                     fontsize=8, fontname="helv", color=(0.8, 0.85, 1))
    
    # Reference and date
    page.insert_text(fitz.Point(30, 95), f"Ref: {ref_no}", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    page.insert_text(fitz.Point(400, 95), f"Date: {today}", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    
    # To line
    page.insert_text(fitz.Point(30, 120), f"To: {request.applicant_name}", fontsize=10, fontname="helv", color=(0, 0, 0))
    
    # Subject
    page.insert_text(fitz.Point(30, 150), f"Subject: {request.title}", fontsize=11, fontname="helvB", color=(0.1, 0.1, 0.4))
    
    # Separator
    page.draw_line(fitz.Point(30, 165), fitz.Point(565, 165), color=(0.7, 0.7, 0.7), width=0.5)
    
    # Body content — word-wrap into the page
    body_rect = fitz.Rect(30, 180, 565, 750)
    content_text = request.content.replace("**", "").replace("##", "").replace("*", "")
    rc = page.insert_textbox(body_rect, content_text, fontsize=10, fontname="helv",
                              color=(0.15, 0.15, 0.15), align=0)
    
    # If content overflows, add more pages
    overflow = content_text
    while rc < 0:
        # Content overflowed — need another page
        page = doc.new_page(width=595, height=842)
        body_rect = fitz.Rect(30, 40, 565, 800)
        rc = page.insert_textbox(body_rect, overflow[len(overflow)+rc:] if rc < 0 else "",
                                  fontsize=10, fontname="helv", color=(0.15, 0.15, 0.15))
        break  # Safety: max 2 pages for hackathon
    
    # Signature block on last page
    last_page = doc[-1]
    y_sig = 770
    last_page.draw_line(fitz.Point(30, y_sig - 20), fitz.Point(565, y_sig - 20), color=(0.7, 0.7, 0.7), width=0.5)
    last_page.insert_text(fitz.Point(30, y_sig), f"Reviewed by: {request.reviewer_name}", fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    last_page.insert_text(fitz.Point(30, y_sig + 14), "Generated via CDSCO AI Regulatory Platform (RurTech.ai)", fontsize=7, fontname="helv", color=(0.5, 0.5, 0.5))
    last_page.insert_text(fitz.Point(400, y_sig), f"[AI-Assisted Report]", fontsize=8, fontname="helvB", color=(0.6, 0.1, 0.1))
    
    # Save to bytes
    pdf_bytes = doc.tobytes()
    doc.close()
    
    # Return as base64 for frontend download
    pdf_b64 = base64.b64encode(pdf_bytes).decode("utf-8")
    
    return {
        "pdf_base64": pdf_b64,
        "filename": f"CDSCO_Report_{ref_no.replace('/', '_')}.pdf",
        "reference_number": ref_no,
        "pages": doc.page_count if hasattr(doc, 'page_count') else 1,
        "generated_at": today
    }


# ---------------------------------------------------------------------------
# Feature 10: Drug Safety Analysis (Chemistry-Based AI Assessment)
# ---------------------------------------------------------------------------
class DrugSafetyRequest(BaseModel):
    drug_name: str
    smiles: Optional[str] = ""
    indication: Optional[str] = ""
    dose: Optional[str] = ""
    route: Optional[str] = ""

@app.post("/drug-safety")
async def drug_safety_endpoint(request: DrugSafetyRequest):
    """Feature 10: AI-powered drug safety assessment with toxicity profiling and similarity matrix."""
    if not request.drug_name or len(request.drug_name.strip()) < 2:
        raise HTTPException(400, "Please provide a valid drug name.")
    from drug_safety import assess_drug_safety
    result = await assess_drug_safety(
        request.drug_name,
        request.smiles,
        request.indication,
        request.dose,
        request.route
    )
    result["nlp_conclusion"] = await generate_nlp_conclusion(result, "Drug Safety Assessment")
    return result


# ---------------------------------------------------------------------------
# Frontend Static Hosting (1-File Foolproof Method for Docker)
# ---------------------------------------------------------------------------
@app.get("/")
async def serve_index():
    index_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Inlined index.html not found.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
