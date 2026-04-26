<div align="center">
  <img src="http://rurtechforarayans.com/wp-content/uploads/2026/04/icon-1.png" alt="RurTech.ai Logo" width="150" />
  <h1>CDSCO Regulatory Workflow Automation Platform</h1>
  <p><strong>Developed by RurTech.ai</strong></p>
</div>

---

## 📖 Overview
Welcome to the official repository for the **RurTech.ai CDSCO Regulatory Workflow Automation Platform**. I built this end-to-end, AI-driven automation pipeline to specifically address the critical bottlenecks in the CDSCO regulatory ecosystem. 

### 🚀 Our Unique Selling Proposition (USP)
Unlike standard regulatory software, this platform operates on a **zero-trust, fully anonymised AI pipeline**. Our USP is the seamless integration of **On-Device Blockchain Biometrics** with localized tokenization. When a patient or document is processed, all PHI/PII is instantly stripped, tokenized, and secured on a local ledger *before* any data reaches the analytical models. This ensures unparalleled compliance with the DPDP Act 2023, NDHM, and ICMR standards while still unlocking advanced AI summarisation and triage.

*(Note: The Stage 2 requirements for the workflow are already fully integrated and ready for you to check and test out-of-the-box!)*

### Core Features
1. **Intelligent Anonymisation Pipeline:** A robust pseudonymisation and tokenization engine that redacts structured (JSON) and unstructured (PDF/TXT) data.
2. **Contextual Document Summarisation:** Automated synthesis of high-volume application data across multiple SUGAM checklists, SAE narrations, and audio transcripts.
3. **Completeness Assessment:** Instant regulatory checklist verifications mapping fields directly to CDSCO mandates.
4. **Severity Classification & Prioritisation:** Automated triage classifying SAE cases (Death, Disability, Hospitalisation, Others) while detecting semantic duplicates via vector embeddings.
5. **Live Biometric Queue:** Native mobile camera biometric recognition mapped to an encrypted on-device blockchain registry, fetching tokenized medical records securely.

---

## ⚙️ Setup & Installation Instructions

I designed this project to be incredibly easy to spin up. It is separated into a **FastAPI Backend** and a **Vanilla JS Frontend**, both of which run seamlessly together from a single command. 

### Prerequisites
* Python 3.10 or higher installed on your system.

### Step 1: Start the Backend & Frontend Server
The FastAPI backend powers all the core RurTech.ai intelligence models and automatically serves the frontend UI simultaneously.
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd regulatory_api
   ```
2. Install the required Python packages:
   ```bash
   pip install -r ../requirements.txt
   ```
3. Run the API Server:
   ```bash
   python main.py
   ```
   *The server will automatically bind to `0.0.0.0:8080`, allowing it to accept API calls from both your local machine and your local Wi-Fi network.*

---

## 🧪 Testing the Application

### Option A: Testing on Desktop
1. Open your web browser and navigate to: `http://localhost:8080`
2. You will see the RurTech.ai Dashboard. Click through the tabs (Anonymise, Summarise, Classify, etc.) to test the features.

### Option B: Testing on Mobile (Portability Mode)
To test the **Live Biometric Queue** or **Site Inspection Camera**, you should access the dashboard from your mobile phone.
1. Ensure your phone is connected to the **same Wi-Fi network** as your computer.
2. Find your computer's local IP address (e.g., `192.168.1.5` by running `ipconfig` on Windows or `ifconfig` on Mac/Linux).
3. Open your mobile browser and navigate to: `http://<YOUR_LOCAL_IP>:8080`
4. The dashboard will load. When you navigate to the **Biometric Queue** or **Site Inspection** tabs, tapping the "Take Photo with Phone" button will seamlessly open your device's native camera!

---

## ☁️ 24/7 Cloud Deployment
If you want to host this permanently online:
1. Fork or push this repository to your own GitHub account.
2. Go to [Render.com](https://render.com) and deploy a new **Web Service**.
3. Set the Build Command: `pip install -r requirements.txt`
4. Set the Start Command: `uvicorn regulatory_api.main:app --host 0.0.0.0 --port $PORT`
