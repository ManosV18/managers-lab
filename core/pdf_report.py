from fpdf import FPDF
from datetime import datetime
import io

class StrategyPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.set_text_color(30, 58, 138) # Dark Blue
        self.cell(0, 10, 'MANAGERS LAB | STRATEGY OS', 0, 1, 'L')
        self.set_draw_color(30, 58, 138)
        self.line(10, 18, 200, 18)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_professional_pdf(metrics, scenario_name):
    pdf = StrategyPDF()
    pdf.add_page()
    
    # Title Section
    pdf.set_font('Arial', 'B', 20)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 15, "Executive Decision Report", 0, 1, 'L')
    
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 7, f"Scenario: {scenario_name}", 0, 1, 'L')
    pdf.cell(0, 7, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1, 'L')
    pdf.ln(10)

    # --- SECTION 1: FINANCIAL PERFORMANCE ---
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, " 1. Strategic Performance Metrics", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 11)
    # ΑΛΛΑΓΗ: Χρησιμοποιούμε "EUR" αντί για "€" για να αποφύγουμε το Latin-1 Error
    data = [
        ["ROIC", f"{metrics.get('roic', 0)*100:.2f}%"],
        ["Net Profit (NOPAT)", f"EUR {metrics.get('nopat', 0):,.2f}"],
        ["Total Revenue", f"EUR {metrics.get('revenue', 0):,.2f}"]
    ]
    
    for item in data:
        pdf.cell(100, 8, item[0], 0, 0)
        pdf.cell(0, 8, item[1], 0, 1)

    pdf.ln(5)

    # --- SECTION 2: SURVIVAL & MARGINS ---
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, " 2. Survival & Safety Analysis", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 11)
    mos = metrics.get('margin_of_safety', 0) * 100
    safety_status = "STABLE" if mos > 15 else "FRAGILE"
    
    data_safety = [
        ["Break-Even Point", f"{metrics.get('bep_units', 0):,.0f} Units"],
        ["Margin of Safety", f"{mos:.2f}%"],
        ["Survival Status", safety_status]
    ]
    
    for item in data_safety:
        pdf.cell(100, 8, item[0], 0, 0)
        pdf.cell(0, 8, item[1], 0, 1)

    pdf.ln(5)

    # --- SECTION 3: LIQUIDITY & CASH FLOW ---
    pdf.set_fill_color(241, 245, 249)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, " 3. Cash & Liquidity Position", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font('Arial', '', 11)
    data_cash = [
        ["Net Cash Position", f"EUR {metrics.get('net_cash_position', 0):,.2f}"],
        ["Cash Conversion Cycle", f"{metrics.get('ccc', 0):.1f} Days"],
        ["Runway", f"{metrics.get('runway_months', 0):.1f} Months"]
    ]
    
    for item in data_cash:
        pdf.cell(100, 8, item[0], 0, 0)
        pdf.cell(0, 8, item[1], 0, 1)

    # --- COLD ANALYTICAL VERDICT ---
    pdf.ln(10)
    pdf.set_fill_color(30, 58, 138)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, " STRATEGIC VERDICT", 0, 1, 'C', fill=True)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', 'I', 11)
    pdf.ln(2)
    
    # Verdict Logic
    if metrics.get('net_cash_position', 0) < 0:
        verdict = "WARNING: Operation is burning through capital. Immediate liquidity injection required."
    elif mos < 10:
        verdict = "CRITICAL: Extremely low Margin of Safety. Volume volatility could trigger insolvency."
    else:
        verdict = "STABLE: Strategy shows resilience. Focus on ROIC optimization."
        
    pdf.multi_cell(0, 8, verdict, 0, 'C')

    # ΤΕΛΙΚΟ CHECK: Μετατροπή σε latin-1 με παράλειψη αγνώστων χαρακτήρων
    return pdf.output(dest='S').encode('latin-1', 'ignore')
