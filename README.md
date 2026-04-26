<div align="center">
  <img src="http://rurtechforarayans.com/wp-content/uploads/2026/04/icon-1.png" alt="RurTech.ai Logo" width="150" />
  <h1>CDSCO AI Regulatory Workflow Automation Platform</h1>
  <p><strong>Developed by RurTech.ai | AIKosh Hackathon Submission</strong></p>
  <p>
    <a href="https://cdsco-ai-kosh.pages.dev"><img src="https://img.shields.io/badge/Live_Demo-Cloudflare_Pages-orange?style=for-the-badge&logo=cloudflare" /></a>
    <a href="https://cdsco-ai-kosh-production.up.railway.app/health"><img src="https://img.shields.io/badge/API-Railway_Backend-blue?style=for-the-badge&logo=railway" /></a>
  </p>
</div>

---

## 🟢 Live Application Demo
**Test the live 24/7 Cloud Application here:** 👉 [https://cdsco-ai-kosh.pages.dev](https://cdsco-ai-kosh.pages.dev)

> Accessible worldwide from any Desktop or Mobile device. No installation required.

---

## 📖 Problem Statement & Solution

This platform addresses the critical bottlenecks in the CDSCO regulatory ecosystem by automating **five core features** mandated by the hackathon guidelines, plus additional value-added capabilities.

### ✅ Feature Coverage (As Per Submission Guidelines)

| # | Required Feature | Status | API Endpoint | Description |
|---|---|---|---|---|
| **1** | **PII/PHI Anonymisation** | ✅ Done | `POST /anonymise` | Automatically detects and redacts Personally Identifiable Information (PII) and Protected Health Information (PHI) from clinical documents, ensuring DPDP Act 2023 compliance. Handles both structured JSON and unstructured text. |
| **2** | **Document Summarisation** | ✅ Done | `POST /summarise` | Summarises SUGAM application data, SAE case narrations (per PMC5950607 standards), meeting transcripts, voice calls, and CDSCO Undertaking/Affidavit documents into structured regulatory formats. |
| **3** | **Completeness Assessment** | ✅ Done | `POST /assess` | Cross-references application data against the official SUGAM Applicant Registration mandatory checklist (26 fields). Returns completeness percentage, missing fields, and reviewer action recommendation. |
| **4** | **SAE Classification & Triage** | ✅ Done | `POST /classify` | Classifies Serious Adverse Events into severity categories (Death, Disability, Hospitalisation, Others), detects duplicates, assigns triage priority, and generates structured narrative reports. |
| **5** | **Inspection Report Generation** | ✅ Done | `POST /inspect/image` `POST /inspect/text` | Converts handwritten notes (via Vision LLM) or typed observations into standardised CDSCO inspection report format. |

### 🚀 Additional Value-Added Features

| # | Feature | Endpoint | Description |
|---|---|---|---|
| 6 | **Biometric Identity Tokenization** | `POST /biometric/identify` | Facial recognition with blockchain pseudonymisation for patient identity management. |
| 7 | **CDSCO Knowledge Base (RAG)** | `POST /ask` | Retrieval-Augmented Generation over 11 official CDSCO PDFs (NDCT Rules 2019, SAE Manual, PSUR, Export NOC, etc.). |
| 8 | **Conversational Chat Agent** | `POST /chat` | Multi-turn regulatory assistant with voice input/output for application prep and compliance guidance. |
| 9 | **PDF Report Generator** | `POST /generate-pdf` | Generates formal computerized CDSCO reviewer letters to applicants as downloadable PDFs. |

---

## 🏗️ Architecture

```
┌──────────────────────────────────┐      ┌──────────────────────────────────┐
│   Cloudflare Pages (Edge CDN)    │      │   Railway (Python Backend)       │
│   https://cdsco-ai-kosh.pages.dev│◄────►│   FastAPI + PyMuPDF + OpenAI     │
│   Tailwind CSS + Voice I/O       │ CORS │   9 API Endpoints                │
│   Chat Agent + PDF Download      │      │   CDSCO Knowledge Base (RAG)     │
└──────────────────────────────────┘      └──────────────────────────────────┘
                                                       │
                                                       ▼
                                          ┌──────────────────────────┐
                                          │  NVIDIA NIM Cloud API    │
                                          │  Llama 4 Maverick 17B   │
                                          │  Llama 3.2 90B Vision   │
                                          │  NV-EmbedQA-E5-v5       │
                                          └──────────────────────────┘
```

## 🔧 Technology Stack

- **Frontend:** HTML5 + Tailwind CSS + Web Speech API (Voice I/O)
- **Backend:** Python 3.11 + FastAPI + PyMuPDF
- **AI Models:** NVIDIA NIM (Llama 4 Maverick 17B, Llama 3.2 90B Vision, NV-EmbedQA)
- **Deployment:** Cloudflare Pages (Frontend) + Railway (Backend Docker)
- **Knowledge Base:** 11 official CDSCO PDFs with BM25 retrieval

## 📁 Repository Structure

```
cdsco hackathon/
├── Dockerfile                     # Container config for Railway
├── requirements.txt               # Python dependencies
├── README.md                      # This file
├── cloudflare_frontend/
│   └── index.html                 # Production Tailwind UI (deployed to Cloudflare)
├── regulatory_api/
│   ├── main.py                    # FastAPI app — all 9 endpoints
│   ├── config.py                  # Model config + SUGAM mandatory fields
│   ├── anonymiser.py              # Feature 1: PII/PHI Anonymisation
│   ├── summariser.py              # Feature 2: Document Summarisation
│   ├── assessor.py                # Feature 3: Completeness + Version Comparison
│   ├── classifier.py              # Feature 4: SAE Classification
│   ├── inspector.py               # Feature 5: Inspection Report Generation
│   ├── biometrics.py              # Feature 6: Facial Recognition
│   ├── knowledge_rag.py           # Feature 7: RAG Knowledge Base Engine
│   ├── index.html                 # Docker-served fallback UI
│   ├── test_api.py                # API test suite
│   └── knowledge_base/
│       ├── cdsco_knowledge_base.json  # Extracted text from 11 CDSCO PDFs
│       └── *.pdf                      # Official CDSCO documents
└── frontend/                      # Legacy frontend (pre-Cloudflare)
```

## 🚀 Quick Start (Local)

```bash
cd regulatory_api
pip install -r ../requirements.txt
python main.py
# API runs at http://localhost:8080
```

## 🐳 Docker

```bash
docker build -t cdsco-ai .
docker run -p 8080:8080 cdsco-ai
```

---

<div align="center">
  <p><strong>Built with ❤️ by RurTech.ai</strong></p>
  <p>Powered by NVIDIA NIM Cloud Infrastructure</p>
</div>
