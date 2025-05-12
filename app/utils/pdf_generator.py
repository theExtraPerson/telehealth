from fpdf import FPDF
from datetime import datetime
from pathlib import Path

def generate_pdf_from_record(record, output_path: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header
    pdf.cell(200, 10, txt="Medical Record", ln=1, align='C')
    pdf.ln(10)
    
    # Patient Information
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Patient Information", ln=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Patient ID: {record.patient_id}", ln=1)
    pdf.cell(200, 10, txt=f"Visit Date: {record.date_of_visit.strftime('%Y-%m-%d')}", ln=1)
    pdf.ln(5)
    
    # Medical Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Medical Details", ln=1)
    pdf.set_font("Arial", size=12)
    
    pdf.multi_cell(0, 10, txt=f"Description: {record.description}")
    pdf.ln(2)
    pdf.multi_cell(0, 10, txt=f"Diagnosis: {record.diagnosis or 'N/A'}")
    pdf.ln(2)
    pdf.multi_cell(0, 10, txt=f"Treatment: {record.treatment or 'N/A'}")
    pdf.ln(2)
    pdf.multi_cell(0, 10, txt=f"Medications: {record.medications or 'N/A'}")
    pdf.ln(2)
    pdf.multi_cell(0, 10, txt=f"Notes: {record.notes or 'N/A'}")
    pdf.ln(10)
    
    # Footer
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt=f"Generated on {datetime.now().strftime('%Y-%m-%d')}", ln=1, align='C')
    pdf.cell(200, 10, txt=f"Doctor: {record.doctor_name}", ln=1, align='C')
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    pdf.output(output_path)