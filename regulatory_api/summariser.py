"""
Feature 2: Document Summarisation
----------------------------------
Handles three distinct document types via RurTech NIM (Llama 3.1 70B):
  A) SUGAM Portal Application Data   → structured checklist summaries
  B) SAE Case Narrations             → concise case resolution format
  C) Meeting Transcripts/Audio Text  → decisions, action items, next steps
"""

from config import get_client, get_model

client = get_client()

# ---------------------------------------------------------------------------
# System prompts for each document type
# ---------------------------------------------------------------------------
SYSTEM_PROMPTS = {

    "sugam": """You are a CDSCO regulatory expert. Your task is to extract and synthesize critical regulatory information from the provided SUGAM portal 'Applicant Registration' application data.
The source material contains data for a firm's registration on the SUGAM portal.
Convert the data into a precise, standardised text format enabling due diligence and decision-making by reviewers.
Output EXACTLY this format:

## SUGAM REGISTRATION APPLICATION SUMMARY
**Applicant Details:** [Name, Designation, Email, Mobile, Gender, Nationality]
**Organization Details:** [Organization Name, Type, CIN]
**Corporate Address & Contact:** [Full Address, Pin Code, Contact No, Fax No]
**Mandatory Uploads Compliance:** [Status of ID Proof, Undertaking Document, Corporate Address Proof, Copy of Manufacturing License]
**Manufacturing Sites & Association:** [Listed sites and any association memberships]
**Critical Regulatory Concerns:** [Synthesize missing mandatory data, inconsistencies, or red flags based on the SUGAM Applicant Registration form]
**Reviewer Recommendation:** [Actionable decision: Proceed / Query / Reject]""",

    "sae": """You are a CDSCO pharmacovigilance specialist. Your task is to synthesize the provided Serious Adverse Event (SAE) data into a highly structured narrative report.
Follow the official guidelines for writing SAE narratives. Ensure all relevant medical records are reviewed and summarized in chronological sequence.
Convert the diverse source material into this EXACT standardised format enabling regulatory due diligence:

## SAE NARRATIVE REPORT
**1. Patient Details:** [Age/Birth year, Gender, Race, Height, Weight]
**2. Study Details:** [Indication, Protocol details, Blind status, Phase]
**3. Patient History:** [Medical history, concomitant diseases, family history, previous/rescue medications]
**4. Details of the Study Drug:** [Drug name, Start/End date, Dosage]
**5. Event Description & Treatment:** [Chronological sequence of the event, Diagnosis (preferred over symptoms), Treatment provided]
**6. Laboratory Tests:** [Readings and normal ranges of relevant tests]
**7. Action Taken with Study Drug:** [Decision taken regarding the suspect drug]
**8. Outcome of Event:** [Status: Recovered / Not yet recovered / Recovered with sequelae / Unknown / Fatal. Include cause of death/autopsy if fatal]
**9. Causality Assessment:** [Evidence-based causality by investigator/sponsor]""",

    "meeting": """You are a CDSCO regulatory secretary. Your task is to synthesize key decisions, actionable items, and next steps from the provided lengthy meeting transcript or audio text.
Convert the high-volume source material into a precise, standardised text format enabling due diligence and decision-making by reviewers.
Output EXACTLY this format:

## SEC MEETING SYNTHESIS
**Meeting Context:** [Date, Type, Key Participants]
**Key Decisions Made:** [Synthesize the major resolutions and regulatory decisions]
**Actionable Items:** [List specific actions, owners, and timelines]
**Next Steps & Due Diligence:** [Pending questions, follow-ups required before the next phase]""",

    "voice_call": """You are a CDSCO compliance analyst reviewing a recorded telephonic conversation (e.g., between an investigator and a patient, or two regulatory officials).
Synthesize the contextual narrative of the phone call. Identify the speakers, the core intent, and any critical regulatory or safety issues discussed.
Output EXACTLY this format:

## VOICE CALL CONTEXTUAL SUMMARY
**Call Participants:** [Identify speakers, e.g., Patient and HCP]
**Primary Intent/Topic:** [Main reason for the call]
**Contextual Narrative:** [Concise synthesis of the conversation flow and key points]
**Safety / Compliance Red Flags:** [Identify any adverse events, protocol deviations, or regulatory issues mentioned]
**Actionable Next Steps:** [What should the reviewer or investigator do next?]"""
}

async def summarise_document(text: str, doc_type: str) -> dict:
    """
    Summarise document using RurTech NIM Llama 3.1 70B.
    doc_type: 'sugam' | 'sae' | 'meeting'
    """
    if doc_type not in SYSTEM_PROMPTS:
        raise ValueError(f"Unknown doc_type: {doc_type}. Use 'sugam', 'sae', or 'meeting'.")

    # Chunk large documents — Llama 3.1 70B has 128k context
    # For very large documents, we summarise chunks then merge
    MAX_CHARS = 90000  # ~70k tokens headroom
    chunks = [text[i:i+MAX_CHARS] for i in range(0, len(text), MAX_CHARS)]

    summaries = []
    for i, chunk in enumerate(chunks):
        user_msg = f"[DOCUMENT PART {i+1}/{len(chunks)}]\n\n{chunk}"
        response = client.chat.completions.create(
            model=get_model("summarise"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[doc_type]},
                {"role": "user", "content": user_msg}
            ],
            temperature=0.1,
            max_tokens=2048
        )
        summaries.append(response.choices[0].message.content)

    # If multi-chunk, do a final merge pass
    final_summary = summaries[0]
    if len(summaries) > 1:
        merge_prompt = "Merge these partial summaries into one cohesive final summary following the same structured format:\n\n" + "\n\n---\n\n".join(summaries)
        merge_response = client.chat.completions.create(
            model=get_model("summarise"),
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS[doc_type]},
                {"role": "user", "content": merge_prompt}
            ],
            temperature=0.1,
            max_tokens=2048
        )
        final_summary = merge_response.choices[0].message.content

    return {
        "document_type": doc_type,
        "model_used": get_model("summarise"),
        "chunks_processed": len(chunks),
        "summary": final_summary
    }

