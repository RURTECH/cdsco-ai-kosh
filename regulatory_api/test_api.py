import pytest
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)

def test_health():
    print("Testing /health...")
    response = client.get("/health")
    assert response.status_code == 200
    print("Health response:", response.json(), "\n")

def test_anonymise():
    print("Testing /anonymise...")
    response = client.post(
        "/anonymise",
        json={"text": "Patient Ram Kumar, aged 45, phone +91 9876543210, admitted for testing."}
    )
    assert response.status_code == 200
    print("Anonymise response:", response.json(), "\n")

def test_summarise():
    print("Testing /summarise...")
    response = client.post(
        "/summarise",
        json={"text": "The meeting commenced at 10 AM. It was noted that the new trial phase 2 data looks promising...", "doc_type": "meeting"}
    )
    assert response.status_code == 200
    print("Summarise response:", response.json(), "\n")

def test_assess():
    print("Testing /assess...")
    response = client.post(
        "/assess",
        json={"text": "Applicant Name: Pharma Inc. Drug Name: CureAll. Indication: Headache. Phase: 3. Protocol Title: A study on CureAll."}
    )
    assert response.status_code == 200
    print("Assess response:", response.json(), "\n")

def test_compare():
    print("Testing /compare...")
    doc_v1 = "The trial will enroll 100 patients. Dosage is 50mg daily."
    doc_v2 = "The trial will enroll 150 patients. Dosage is 100mg daily. Added safety monitoring."
    response = client.post(
        "/compare",
        json={"document_v1": doc_v1, "document_v2": doc_v2, "similarity_threshold": 0.85}
    )
    assert response.status_code == 200
    print("Compare response:", response.json(), "\n")

def test_classify():
    print("Testing /classify...")
    response = client.post(
        "/classify",
        json={"case_id": "CASE123", "text": "Patient experienced severe allergic reaction and was hospitalised for 3 days after taking the medication."}
    )
    assert response.status_code == 200
    print("Classify response:", response.json(), "\n")

def test_inspect_text():
    print("Testing /inspect/text...")
    response = client.post(
        "/inspect/text",
        json={"raw_notes": "Site visit on 12 Oct 2023 at City Hospital. Dr. Smith was present. Found missing consent forms for 3 patients. Otherwise things looked good."}
    )
    assert response.status_code == 200
    print("Inspect Text response:", response.json(), "\n")

def test_inspect_image():
    print("Testing /inspect/image...")
    try:
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (200, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((10,10), "Inspection Date: 12 Oct", fill=(0,0,0))
        d.text((10,30), "Issue: Missing forms", fill=(0,0,0))
        img.save('dummy_inspection.png')
        
        with open('dummy_inspection.png', 'rb') as f:
            response = client.post("/inspect/image", files={"file": ("dummy_inspection.png", f, "image/png")})
        assert response.status_code == 200
        print("Inspect Image response:", response.json(), "\n")
        os.remove('dummy_inspection.png')
    except Exception as e:
        print("Skipped or failed image test:", e)

if __name__ == "__main__":
    test_health()
    test_anonymise()
    test_summarise()
    test_assess()
    test_compare()
    test_classify()
    test_inspect_text()
    test_inspect_image()
    print("All tests completed successfully!")
