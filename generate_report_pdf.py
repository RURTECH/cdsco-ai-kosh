import re
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class PDFReport(FPDF):
    def header(self):
        self.set_fill_color(30, 64, 175) # Tailwind blue-800
        self.rect(0, 0, 210, 25, 'F')
        self.set_font("helvetica", "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "RurTech.ai - CDSCO Regulatory Automation", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.set_font("helvetica", "I", 10)
        self.cell(0, 5, "Official Hackathon Project Report & Key Findings", new_x=XPos.LMARGIN, new_y=YPos.NEXT, align="C")
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def sanitize(text):
    text = text.replace('\u2014', '-')
    text = text.replace('\u2013', '-')
    text = text.replace('\u2018', "'")
    text = text.replace('\u2019', "'")
    text = text.replace('\u201c', '"')
    text = text.replace('\u201d', '"')
    text = text.replace('\u2026', '...')
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf():
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    with open("IndiaAI_Project_Report.md", "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue
            
        line = sanitize(line)
            
        if line.startswith("## "):
            pdf.ln(5)
            pdf.set_font("helvetica", "B", 14)
            pdf.set_text_color(15, 23, 42) # slate-900
            pdf.cell(0, 10, line.replace("## ", "").replace("*", ""), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_draw_color(200, 200, 200)
            pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
            pdf.ln(3)
        elif line.startswith("### "):
            pdf.ln(4)
            pdf.set_font("helvetica", "B", 12)
            pdf.set_text_color(51, 65, 85) # slate-700
            pdf.cell(0, 8, line.replace("### ", "").replace("*", ""), new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        elif line.startswith("* **") or line.startswith("- **"):
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(30, 30, 30)
            clean_line = line.replace("* **", "- ").replace("- **", "- ").replace("**", ":")
            clean_line = clean_line.replace("`", "")
            pdf.multi_cell(0, 6, clean_line)
        elif line.startswith("**"):
            pdf.set_font("helvetica", "B", 10)
            pdf.set_text_color(0, 0, 0)
            clean_line = line.replace("**", "")
            pdf.cell(0, 6, clean_line, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        else:
            pdf.set_font("helvetica", "", 10)
            pdf.set_text_color(50, 50, 50)
            clean_line = line.replace("**", "").replace("*", "").replace("`", "")
            if clean_line.startswith("- "):
                clean_line = "  " + clean_line
            pdf.multi_cell(0, 6, clean_line)

    pdf.output("IndiaAI_Project_Report.pdf")
    print("PDF Generated successfully!")

if __name__ == "__main__":
    generate_pdf()
