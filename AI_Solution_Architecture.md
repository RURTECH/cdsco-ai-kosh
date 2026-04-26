# RurTech for Arayans LLP
## AI Solution Architecture & Methodology

**Functionality & Features:** A self-implemented Agentic AI platform automating CDSCO regulatory workflows, including PII anonymisation, application completeness assessment, SAE severity triage, and MolMIM molecular drug safety screening.

**Core AI Technologies:** Powered entirely by self-implemented advanced Transformers: `Llama-3.1-70B-Instruct` (reasoning/extraction), `Llama-3.2-90B-Vision` (OCR), `NV-EmbedQA` (RAG semantic search), and `NVIDIA MolMIM` (chemistry).

**Training & Validation Data:** Data provenance ensures strict compliance, using official NDCT Rules 2019 and SUGAM manuals. The high-quality RAG corpus ensures comprehensive regulatory coverage, validated against 500+ noisy synthetic applications.

**Data Preparation Strategies:** Unstructured documents undergo rigid sanitization, OCR extraction, and overlapping chunking before NV-EmbedQA vectorization into our secure database.

**AI/ML Selection, Tuning & Monitoring:** Llama-3.1-70B was selected for zero-shot accuracy. We avoided weight-retraining to prevent catastrophic forgetting, utilizing precision prompt engineering instead. Hyper-parameters are strict (Temperature=0.3) for legal determinism. The system is monitored via empirical vector-similarity thresholds (>85% for duplicate detection), providing algorithmic "Triage Scores" for human-in-the-loop oversight.

**Solution Replicability:** The domain-agnostic Agentic architecture (Anonymiser, Assessor, Classifier) easily scales across sectors. By swapping the Vector Database, it readily adapts to Banking (KYC verification), Judiciary (legal summaries), and Healthcare (insurance claims validation).
