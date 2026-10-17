import datetime
from io import BytesIO
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def gerar_pdf_relatorio(df: pd.DataFrame) -> BytesIO:
    """Gera um relatório formal em formato PDF com cabeçalho institucional e tabela de dados."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    elements = []
    styles = getSampleStyleSheet()

    header_style = ParagraphStyle(
        name="HeaderStyle",
        parent=styles['Heading1'],
        fontName="Helvetica-Bold",
        fontSize=15,
        textColor=colors.HexColor("#1E3A8A"),
        alignment=1
    )
    elements.append(Paragraph("Docente360 — Relatório Oficial de Ausências e Substituições", header_style))
    elements.append(Paragraph(
        f"Emitido em: {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}",
        ParagraphStyle('Data', parent=styles['Normal'], alignment=1, fontSize=9, textColor=colors.gray)
    ))
    elements.append(Spacer(1, 14))

    col_widths = [65, 110, 130, 110, 85]
    data_tabela = [["Data", "Professor", "Disciplina", "Turma", "Status"]]
    for _, row in df.iterrows():
        data_tabela.append([
            str(row.get("Data", "")),
            str(row.get("Professor", ""))[:20],
            str(row.get("Disciplina", ""))[:22],
            str(row.get("Turma", ""))[:18],
            str(row.get("Status", ""))
        ])

    t = Table(data_tabela, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    elements.append(t)
    doc.build(elements)
    buffer.seek(0)
    return buffer
