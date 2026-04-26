import json
import os
import uuid
import hashlib
from datetime import datetime
from config import get_client, get_model

client = get_client()

# Simulating RurTech.ai Secure Cloud Datastore & On-Device Blockchain
GCP_DATASTORE_FILE = "gcp_patients_db.json"
BLOCKCHAIN_REGISTRY_FILE = "on_device_blockchain_ledger.json"

def _load_db(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        return json.load(f)

def _save_db(file_path, db):
    with open(file_path, "w") as f:
        json.dump(db, f, indent=4)

async def synthesize_patient_context(patient_data: dict, is_new: bool) -> str:
    """Use LLaMA 4 RurTech.ai Core to generate a contextual status for the UI, using pulled token data."""
    if is_new:
        prompt = f"A new patient was just registered via biometrics and secured on the blockchain. Generate a polite welcome message confirming their anonymised vault token {patient_data['vault_token']} has been created and data is secured."
    else:
        prompt = f"Returning patient identified via biometrics. We pulled their token {patient_data['vault_token']} from the blockchain. Their problem: {patient_data['medical_problem']}. Fees pending: {patient_data['fees_pending']}. Generate a polite welcome back message summarizing this context."

    system_prompt = "You are a clinic AI powered by LLaMA 4 RurTech.ai Core. Be extremely concise (2 sentences max)."
    
    response = client.chat.completions.create(
        model=get_model("summarise"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=150
    )
    return response.choices[0].message.content

async def identify_patient_face(image_base64: str) -> dict:
    """
    RurTech.ai Neural Engine Biometric Pipeline (RurTech.ai Secure Cloud Datastore + On-Device Blockchain + RurTech.ai Core LLM)
    """
    db = _load_db(GCP_DATASTORE_FILE)
    ledger = _load_db(BLOCKCHAIN_REGISTRY_FILE)
    
    # For demo purposes, we alternate:
    # If DB is empty -> Register new person (Create Token + Blockchain)
    # If DB has data -> Returning match (Pull Token + LLM context)
    
    is_returning = len(db) > 0
    
    if not is_returning:
        # 1. New User: Create Tokenized Record (Pseudonymisation)
        patient_id = "PAT-" + str(uuid.uuid4())[:8].upper()
        vault_token = "[PHI_VAULT_" + hashlib.sha256(patient_id.encode()).hexdigest()[:8].upper() + "]"
        
        patient_data = {
            "patient_id": patient_id,
            "vault_token": vault_token,
            "name": "Arjun Sharma (Demo Patient)",
            "first_arrival": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "last_arrival": "First Visit Today",
            "medical_problem": "Post-trial safety evaluation and severe headaches.",
            "fees_pending": False,
            "status": "New Registration"
        }
        db[patient_id] = patient_data
        _save_db(GCP_DATASTORE_FILE, db)
        
        # 2. Secure Folder in On-Device Blockchain Registry
        tx_hash = "0x" + hashlib.sha256(json.dumps(patient_data).encode()).hexdigest()
        ledger[tx_hash] = {
            "token": vault_token,
            "timestamp": datetime.now().isoformat(),
            "contract": "0xCDSCO_REGISTRY_SMART_CONTRACT"
        }
        _save_db(BLOCKCHAIN_REGISTRY_FILE, ledger)
        
        match_found = False
        blockchain_tx = tx_hash
        
    else:
        # Returning Patient Matched
        patient_id = list(db.keys())[0]
        patient_data = db[patient_id]
        
        patient_data["last_arrival"] = datetime.now().strftime("%Y-%m-%d %H:%M")
        patient_data["fees_pending"] = True 
        patient_data["status"] = "Returning Match"
        _save_db(GCP_DATASTORE_FILE, db)
        
        match_found = True
        
        # Look up their latest transaction in the ledger
        blockchain_tx = list(ledger.keys())[-1] if ledger else "N/A"

    # 3. Pulled out by LLM for contextual synthesis
    contextual_greeting = await synthesize_patient_context(patient_data, not is_returning)

    return {
        "biometric_match_found": match_found,
        "tokenizer_pseudonymisation": patient_data["vault_token"],
        "blockchain_registry": {
            "secured": True,
            "transaction_hash": blockchain_tx,
            "smart_contract": "0xCDSCO_REGISTRY_SMART_CONTRACT"
        },
        "backend_storage": "RurTech.ai Secure Cloud Datastore",
        "RurTech.ai Neural Engine_model": "RurTech-BioNet-v1 (Simulated Match)",
        "patient_record": patient_data,
        "RurTech.ai Core_contextual_greeting": contextual_greeting
    }

