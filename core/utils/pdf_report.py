from fpdf import FPDF
import tempfile

def generate_pdf_report(metrics, scenario_name="Scenario"):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Managers Lab - Executive Decision Report", ln=True)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Scenario: {scenario_name}", ln=True)

    pdf.ln(5)

    for key, value in metrics.items():

        label = key.replace("_"," ").title()

        try:
            value = f"{value:,.2f}"
        except:
            pass

        pdf.cell(0, 8, f"{label}: {value}", ln=True)

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")

    pdf.output(tmp.name)

    return tmp.name
