# Model Card: RurTech Agentic Regulatory Stack
**Organization:** RurTech for Arayans LLP

## 1. Model Details
- **Architecture Type:** Orchestrated Multi-Agent Transformer System utilizing RAG.
- **Core Base Models:** `Llama-3.1-70B-Instruct` (Reasoning), `Llama-3.2-90B-Vision` (OCR), `NV-EmbedQA` (Semantic Vectorization), and `NVIDIA MolMIM` (Drug Analysis).
- **Primary Use Case:** CDSCO Regulatory Automation (PII Anonymisation, SUGAM Completeness Assessment, SAE Severity Triage, Inspection Note Generation, and Molecular Screening).

## 2. Intended Use
- **Primary Purpose:** Assisting government CDSCO reviewers by providing high-speed, automated first-pass screening and compliance validation of clinical documents.
- **Out-of-Scope Uses:** Autonomous final regulatory approval. The system provides an algorithmic "Triage Score" but mandates human-in-the-loop oversight for final decision-making.

## 3. Privacy Aspects
- **Strict PII/PHI Redaction:** The platform enforces a two-step pseudonymisation process before core processing begins. Patient names, Aadhaar numbers, and exact birthdates are flagged via semantic NER and replaced with format-preserving secure tokens (e.g., `[PAT_ID_104]`). 
- **Zero-Retention API:** The backend API operates entirely statelessly. No clinical application data or case narratives are persistently stored or logged post-analysis. 
- **DPDP Act Compliance:** End-to-end data processing ensures strict alignment with India's Digital Personal Data Protection (DPDP) Act 2023. User prompts are never utilized to fine-tune the underlying base weights.

## 4. Security Aspects
- **Cryptographic Tokenization:** Redacted identities are hashed using secure algorithms and mapped via a ledger. De-anonymisation is only possible via authorized cryptographic keys.
- **Transport Security:** Data in transit is secured via TLS 1.3 edge-level encryption between the frontend interface and the highly secure NVIDIA NIM cloud backend.
- **Adversarial Mitigation & Guardrails:** To prevent prompt injection or hallucinated policy interpretations, the system employs strict JSON schema enforcing, strict Temperature control (T=0.3), and bounds the LLM purely to official CDSCO vector documents via RAG.

## 5. Solution Architecture Diagram
*(The complete flowchart illustrating the multi-agent orchestration, security layers, and data flow is provided below).*
