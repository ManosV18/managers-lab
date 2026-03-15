from fpdf import FPDF
import tempfile

def generate_pdf_report(metrics):

    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0,10,"Managers Lab - Executive Decision Report",ln=True)

    pdf.set_font("Arial","",12)

    for k,v in metrics.items():

        label = k.replace("_"," ").title()

        try:
            value = f"{v:,.2f}"
        except:
            value = str(v)

        pdf.cell(0,8,f"{label}: {value}",ln=True)

    tmp = tempfile.NamedTemporaryFile(delete=False,suffix=".pdf")

    pdf.output(tmp.name)

    return tmp.name
