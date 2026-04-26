"""
CDSCO Knowledge Base (RAG) Module
-----------------------------------
Loads the CDSCO official PDF documents as a local knowledge base.
Provides a query function that:
  1. Finds the most relevant document sections via keyword/TF-IDF-style scoring
  2. Injects retrieved context into an LLM call (Retrieval-Augmented Generation)
  3. Returns a grounded, citation-aware answer

Documents Loaded:
  - NDCT Rules 2019 (New Drugs and Clinical Trials)
  - SAE User Manual
  - SUGAM Portal Manuals (PSUR, PAC/BABE, Export NOC, Dual Use NOC)
  - Online Payment Manual
  - Cell & Gene Therapeutic Manual
  - Form 12A (Import for Personal Use)
"""

import json
import os
import re
from math import log
from config import get_client, get_model

# ---------------------------------------------------------------------------
# Load Knowledge Base
# ---------------------------------------------------------------------------
KB_PATH = os.path.join(os.path.dirname(__file__), "knowledge_base", "cdsco_knowledge_base.json")

_knowledge_base = None

def _load_kb() -> dict:
    global _knowledge_base
    if _knowledge_base is None:
        with open(KB_PATH, "r", encoding="utf-8") as f:
            _knowledge_base = json.load(f)
    return _knowledge_base


# ---------------------------------------------------------------------------
# Retrieval: BM25-style keyword scoring
# ---------------------------------------------------------------------------
def _tokenize(text: str) -> list[str]:
    return re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())


def _score_document(query_tokens: list[str], doc_text: str) -> float:
    """Score a document chunk using simple TF * IDF-like term frequency scoring."""
    doc_tokens = _tokenize(doc_text)
    doc_len = max(len(doc_tokens), 1)
    tf_map: dict[str, float] = {}
    for t in doc_tokens:
        tf_map[t] = tf_map.get(t, 0) + 1

    score = 0.0
    for qt in query_tokens:
        tf = tf_map.get(qt, 0)
        if tf > 0:
            # BM25-like saturation: tf/(tf+1.5)
            score += (tf / (tf + 1.5))
    return score


def retrieve_context(query: str, top_k: int = 3, chunk_size: int = 3000) -> list[dict]:
    """
    Retrieve the most relevant chunks from the CDSCO knowledge base.
    Returns a list of dicts: {source, chunk, score}
    """
    kb = _load_kb()
    query_tokens = _tokenize(query)

    scored_chunks = []
    for doc_key, doc_data in kb.items():
        text = doc_data.get("text", "")
        if not text:
            continue
        # Split into overlapping chunks
        words = text.split()
        step = chunk_size // 5  # ~600 word stride for overlap
        for i in range(0, len(words), step):
            chunk = " ".join(words[i:i + chunk_size])
            if len(chunk) < 50:
                continue
            score = _score_document(query_tokens, chunk)
            if score > 0:
                scored_chunks.append({
                    "source": doc_data["filename"],
                    "chunk": chunk[:2000],  # Trim chunk for LLM context
                    "score": score
                })

    # Return top K unique sources
    scored_chunks.sort(key=lambda x: x["score"], reverse=True)
    seen_sources = set()
    top_chunks = []
    for c in scored_chunks:
        if c["source"] not in seen_sources:
            top_chunks.append(c)
            seen_sources.add(c["source"])
        if len(top_chunks) >= top_k:
            break
    return top_chunks


# ---------------------------------------------------------------------------
# RAG Query Function
# ---------------------------------------------------------------------------
async def query_knowledge_base(question: str) -> dict:
    """
    Answer a CDSCO regulatory question using RAG over the official PDF knowledge base.
    """
    client = get_client()

    # 1. Retrieve relevant context
    chunks = retrieve_context(question, top_k=3)

    if not chunks:
        context_text = "No directly relevant sections found in the knowledge base."
    else:
        context_text = "\n\n---\n\n".join([
            f"[Source: {c['source']}]\n{c['chunk']}"
            for c in chunks
        ])

    # 2. Build RAG prompt
    system_prompt = """You are a CDSCO regulatory expert assistant. You have access to official CDSCO/SUGAM portal documentation.
Answer the user's regulatory question using ONLY the provided context from official documents.
Always cite the source document name for each fact you state.
If the context does not contain sufficient information, say so clearly - do not hallucinate.
Be concise, structured, and authoritative."""

    user_message = f"""QUESTION: {question}

---
OFFICIAL CDSCO DOCUMENT CONTEXT:
{context_text}
---

Please answer the question based on the above official documents."""

    response = client.chat.completions.create(
        model=get_model("summarise"),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.1,
        max_tokens=2048
    )

    answer = response.choices[0].message.content

    return {
        "question": question,
        "answer": answer,
        "sources_used": [c["source"] for c in chunks],
        "retrieval_scores": [round(c["score"], 3) for c in chunks],
        "model_used": get_model("summarise")
    }
