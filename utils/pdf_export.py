from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas


def recap_to_pdf_bytes(title: str, body: str) -> bytes:
    """Create a simple PDF recap and return its bytes."""
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=LETTER)
    width, height = LETTER

    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(0.75 * inch, height - 1 * inch, title)

    pdf.setFont("Helvetica", 11)
    text_object = pdf.beginText(0.75 * inch, height - 1.5 * inch)
    for line in body.splitlines():
        text_object.textLine(line)
    pdf.drawText(text_object)

    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return buffer.read()
