import os
import re
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Image
from reportlab.lib.colors import HexColor

def generate_pdf():
    doc = SimpleDocTemplate("CDSCO_IndiaAI_Hackathon_Report.pdf", pagesize=A4,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    
    styles = getSampleStyleSheet()
    
    style_title = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=18, textColor=HexColor("#1e3a8a"), spaceAfter=14, alignment=1)
    style_h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, textColor=HexColor("#0f172a"), spaceAfter=10, spaceBefore=10)
    style_h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=12, textColor=HexColor("#334155"), spaceAfter=8, spaceBefore=8)
    style_body = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, textColor=HexColor("#333333"), spaceAfter=6, leading=14)
    style_bullet = ParagraphStyle('Bullet', parent=styles['Normal'], fontSize=10, textColor=HexColor("#333333"), leftIndent=20, spaceAfter=6, leading=14)

    elements = []
    
    # 1. Insert Logo
    if os.path.exists("logo.png"):
        logo = Image("logo.png", width=120, height=40)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 10))
    
    with open("IndiaAI_Project_Report.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        line = re.sub(r'\*(.*?)\*', r'<i>\1</i>', line)
        line = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', line)
        
        if line.startswith("# "):
            elements.append(Paragraph(line[2:], style_title))
            elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=15))
        elif line.startswith("## "):
            elements.append(Paragraph(line[3:], style_h2))
            
            # Inject Architecture Image after first H2 (Model Code and Documentation)
            if "Model Code" in line and os.path.exists("architecture.png"):
                elements.append(Spacer(1, 10))
                arch_img = Image("architecture.png", width=400, height=200)
                arch_img.hAlign = 'CENTER'
                elements.append(arch_img)
                elements.append(Spacer(1, 10))
                
        elif line.startswith("### "):
            elements.append(Paragraph(line[4:], style_h3))
            
            # Inject Accuracy Image after Evaluation section
            if "Evaluation" in line and os.path.exists("accuracy.png"):
                elements.append(Spacer(1, 10))
                acc_img = Image("accuracy.png", width=400, height=200)
                acc_img.hAlign = 'CENTER'
                elements.append(acc_img)
                elements.append(Spacer(1, 10))
                
        elif line.startswith("---"):
            elements.append(HRFlowable(width="100%", thickness=1, color=HexColor("#cbd5e1"), spaceAfter=15, spaceBefore=15))
        elif line.startswith("* ") or line.startswith("- "):
            elements.append(Paragraph("• " + line[2:], style_bullet))
        elif re.match(r'^\d+\.\s', line):
            elements.append(Paragraph(line, style_bullet))
        else:
            elements.append(Paragraph(line, style_body))

    doc.build(elements)
    print("ReportLab PDF Generated successfully!")

if __name__ == "__main__":
    generate_pdf()
