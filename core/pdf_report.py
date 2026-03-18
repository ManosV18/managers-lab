# -*- coding: utf-8 -*-
from fpdf import FPDF
from datetime import datetime

class StrategyPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(30, 58, 138)
        self.cell(0, 10, 'MANAGERS LAB | STRATEGY OS', 0, 1, 'L')
        self.set_draw_color(30, 58, 138)
        self.line(10, 18, 200, 18)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def safe_str(text):
    """Μετατρέπει οποιοδήποτε κείμενο σε μορφή που ΔΕΝ σπάει την FPDF."""
    if text is None: return ""
    # Μετατροπή σε string, αντικατάσταση του Ευρώ και αφαίρεση μη-latin1 χαρακτήρων
    s = str(text).replace('€', 'EUR').replace('\u20ac', 'EUR')
    return s.encode('latin-1', 'ignore').decode('latin-1')

def generate_professional_pdf(metrics, scenario_name):
    pdf = StrategyPDF()
    pdf.add_page()
    
    # Title Section
    pdf.set_font('Arial', 'B', 20)
    pdf.cell(0, 15, safe_str("Executive Decision Report"), 0, 1, 'L')
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 7, f"Scenario: {safe_str(scenario_name)}", 0, 1, 'L')
    pdf.cell(0, 7, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'L')
    pdf.ln(10)

    # --- SECTION 1: PERFORMANCE ---
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, safe_str(" 1. Strategic Metrics"), 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 11)
    # Προσοχή: Εδώ βάζουμε "EUR" απευθείας στον κώδικα
    perf_data = [
        ["ROIC", f"{metrics.get('roic', 0)*100:.2f}%"],
        ["Net Profit", f"EUR {metrics.get('net_profit', 0):,.2f}"],
        ["Revenue", f"EUR {metrics.get('revenue', 0):,.2f}"]
    ]
    
    for row in perf_data:
        pdf.cell(100, 8, safe_str(row[0]), 0, 0)
        pdf.cell(0, 8, safe_str(row[1]), 0, 1)

    pdf.ln(5)

    # --- SECTION 2: SAFETY ---
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, safe_str(" 2. Survival Analysis"), 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    mos = metrics.get('margin_of_safety', 0) * 100
    safety_data = [
        ["Break-Even", f"{metrics.get('bep_units', 0):,.0f} Units"],
        ["Margin of Safety", f"{mos:.2f}%"]
    ]
    
    for row in safety_data:
        pdf.cell(100, 8, safe_str(row[0]), 0, 0)
        pdf.cell(0, 8, safe_str(row[1]), 0, 1)

    # --- SECTION 3: CASH ---
    pdf.ln(5)
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, safe_str(" 3. Liquidity"), 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    cash_data = [
        ["Net Cash Position", f"EUR {metrics.get('net_cash_position', 0):,.2f}"],
        ["Runway", f"{metrics.get('runway_months', 0):.1f} Months"]
    ]
    
    for row in cash_data:
        pdf.cell(100, 8, safe_str(row[0]), 0, 0)
        pdf.cell(0, 8, safe_str(row[1]), 0, 1)

    # Output as bytes - Το τελικό φιλτράρισμα
    return pdf.output(dest='S').encode('latin-1', 'ignore')
