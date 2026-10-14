from datetime import datetime
from decimal import Decimal
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

INVOICE_DIR = Path("invoices")  # not under /uploads, so it is not publicly served

def _money(value) -> str:
    return f"INR {Decimal(str(value or 0)):,.2f}"

def generate_service_invoice(request, record) -> str:
    INVOICE_DIR.mkdir(parents=True, exist_ok=True)
    file_path = INVOICE_DIR / f"CZ-INV-{request.id:06d}.pdf"

    styles = getSampleStyleSheet()
    title = ParagraphStyle("title", parent=styles["Title"], textColor=colors.HexColor("#1f2937"))
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9, textColor=colors.grey)

    doc = SimpleDocTemplate(str(file_path), pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm)
    story = [
        Paragraph("CarZen Service Invoice", title),
        Paragraph("CarZen Service Provider", small),
        Spacer(1, 8 * mm),
    ]

    car = request.car
    car_label = " ".join(
        str(x) for x in [getattr(car, "brand_name", None), getattr(car, "model_name", None),
                         getattr(car, "title", None)] if x
    ) or f"Car #{request.car_id}"

    info = [
        ["Invoice No:", f"CZ-INV-{request.id:06d}", "Date:", datetime.now().strftime("%d %b %Y")],
        ["Request ID:", str(request.id), "Service Date:", str(request.scheduled_date or "-")],
        ["Vehicle:", car_label, "Odometer:", str(record.odometer_reading or "-")],
    ]
    t = Table(info, colWidths=[28 * mm, 55 * mm, 28 * mm, 55 * mm])
    t.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (2, 0), (2, -1), "Helvetica-Bold"),
    ]))
    story += [t, Spacer(1, 8 * mm)]

    rows = [["#", "Service", "Qty", "Unit Price", "Total"]]
    for i, item in enumerate(request.items, 1):
        rows.append([str(i), item.service_name, "1", _money(item.unit_price), _money(item.unit_price)])
    items_table = Table(rows, colWidths=[10 * mm, 80 * mm, 15 * mm, 35 * mm, 35 * mm], repeatRows=1)
    items_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.lightgrey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f9fafb")]),
    ]))
    story += [items_table, Spacer(1, 6 * mm)]

    summary = [
        ["Base amount", _money(request.base_amount)],
        ["Parts cost", _money(request.parts_cost)],
        ["Labor cost", _money(request.labor_cost)],
        ["Total payable", _money(request.total_amount)],
    ]
    s = Table(summary, colWidths=[40 * mm, 40 * mm], hAlign="RIGHT")
    s.setStyle(TableStyle([
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("FONTNAME", (0, -1), (-1, -1), "Helvetica-Bold"),
        ("LINEABOVE", (0, -1), (-1, -1), 0.8, colors.black),
    ]))
    story.append(s)

    note = record.description or request.admin_note
    if note:
        story += [Spacer(1, 8 * mm), Paragraph(f"<b>Notes:</b> {note}", styles["Normal"])]
    if record.next_service_date or record.next_service_mileage:
        story += [Spacer(1, 4 * mm), Paragraph(
            f"<b>Next service:</b> {record.next_service_date or '-'} / {record.next_service_mileage or '-'} km",
            styles["Normal"])]

    story += [Spacer(1, 14 * mm), Paragraph("Thank you for choosing CarZen.", small)]
    doc.build(story)
    return str(file_path)