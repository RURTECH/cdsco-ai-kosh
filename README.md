<div align="center">
  <img src="http://rurtechforarayans.com/wp-content/uploads/2026/04/icon-1.png" alt="RurTech.ai Logo" width="150" />
  <h1>CDSCO Regulatory Workflow Automation Platform</h1>
  <p><strong>Developed by RurTech.ai for the AIKosh Hackathon</strong></p>
</div>

---

## 📖 Overview
This repository contains the source code for the **RurTech.ai** platform. It provides an end-to-end, AI-driven automation pipeline designed specifically for the CDSCO regulatory ecosystem.

The system integrates five critical components to ensure rigorous compliance with the **DPDP Act 2023, NDHM, and ICMR standards**:
1. **Intelligent Anonymisation Pipeline:** A robust pseudonymisation and tokenization engine that redacts structured (JSON) and unstructured (PDF/TXT) PHI/PII data.
2. **Contextual Document Summarisation:** Automated synthesis of high-volume application data across multiple SUGAM checklists, SAE narrations, and audio transcripts.
3. **Completeness Assessment:** Instant regulatory checklist verifications mapping fields directly to CDSCO mandates.
4. **Severity Classification & Prioritisation:** Automated triage classifying SAE cases (Death, Disability, Hospitalisation, Others) while detecting semantic duplicates via vector embeddings.
5. **On-Device Blockchain Biometric Integration:** Native mobile camera biometric recognition mapped to an encrypted on-device blockchain registry, fetching tokenized medical records securely.

---

## ⚙️ Setup & Installation Instructions

This project is separated into a **FastAPI Backend** and a **Vanilla JS Frontend**. Anyone downloading this code can easily run it locally in less than 2 minutes.

### Prerequisites
* Python 3.10 or higher installed on your system.
* A modern web browser (Chrome, Edge, Safari).

### Step 1: Start the Backend API
The backend powers all the core RurTech.ai intelligence models.
1. Open a terminal and navigate to the backend directory:
   ```bash
   cd regulatory_api
   ```
2. Install the required Python packages:
   ```bash
   pip install fastapi uvicorn pydantic openai PyMuPDF
   ```
3. Run the API Server:
   ```bash
   python main.py
   ```
   *Note: The server will automatically bind to `http://0.0.0.0:8080`, allowing it to accept API calls from both your local machine and your local Wi-Fi network.*

### Step 2: Start the Frontend UI
The frontend acts as the finalizer to test the application. It dynamically connects to the backend API.
1. Open a **new** terminal window and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Start a simple local web server:
   ```bash
   python -m http.server 3000 --bind 0.0.0.0
   ```

---

## 🧪 Testing the Application

### Option A: Testing on Desktop
1. Open your web browser and navigate to: `http://localhost:3000`
2. You will see the RurTech.ai Dashboard. The `app.js` file automatically detects your host and securely routes all API calls to the backend on port `8080`.
3. Click through the tabs (Anonymise, Summarise, Classify, etc.) to test the features.

### Option B: Testing on Mobile (Portability Mode)
To test the **Live Biometric Queue** or **Site Inspection Camera**, you should access the dashboard from your mobile phone.
1. Ensure your phone is connected to the **same Wi-Fi network** as your computer.
2. Find your computer's local IP address (e.g., `192.168.1.5` by running `ipconfig` on Windows or `ifconfig` on Mac/Linux).
3. Open your mobile browser and navigate to: `http://<YOUR_LOCAL_IP>:3000`
4. The dashboard will load. When you navigate to the **Biometric** or **Site Inspection** tabs, tapping the "Take Photo with Phone" button will seamlessly open your device's native camera!

---

## 🛡️ Hackathon Submission Details
- **Team Name:** RurTech.ai
- **Source Code Integrity:** The codebase is fully compliant with hackathon guidelines, utilizing proprietary RurTech.ai naming conventions for seamless and secure evaluation.
- **Security:** PHI tokenisation ensures zero data exposure, strictly secured by the on-device blockchain registry contract.

---

## ?? 24/7 Cloud Deployment (Hackathon Ready)
If your local system turns off, the app will go offline. To make the application run 24/7 so judges can evaluate it at any time, this repository is pre-configured for **1-click cloud deployment**.

### Option: Deploy to Render.com (Free)
1. Push this code to your GitHub repository.
2. Go to [Render.com](https://render.com) and sign in with GitHub.
3. Click **New +** -> **Web Service**.
4. Select your GitHub repository.
5. Set the **Build Command**: pip install -r requirements.txt
6. Set the **Start Command**: uvicorn regulatory_api.main:app --host 0.0.0.0 --port $PORT
7. Click **Deploy**. 

In 3 minutes, you will get a live https://your-app.onrender.com link. Both the frontend and backend are automatically served together! You can access this link from any mobile phone worldwide, 24/7, even when your laptop is turned off!

