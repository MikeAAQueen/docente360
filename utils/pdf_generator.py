import datetime
from io import BytesIO
import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# ==============================================================================
# CANVAS COM NUMERAÇÃO DINÂMICA DE PÁGINAS (Página X de Y)
# ==============================================================================
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748B"))

        # Linha e texto de rodapé
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(36, 30, 792 - 36, 30)

        self.drawString(36, 18, "Docente360 — Sistema Integrado de Gestão Acadêmica | Relatório Oficial Confidencial")
        page_str = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(792 - 36, 18, page_str)
        self.restoreState()


# ==============================================================================
# GERADOR OFICIAL DE RELATÓRIO PDF EM PAISAGEM
# ==============================================================================
def gerar_pdf_relatorio(
    df: pd.DataFrame,
    titulo: str = "Relatório Consolidado de Ausências e Substituições",
    filtros_info: dict = None,
    emitido_por: str = "Coordenação Acadêmica"
) -> BytesIO:
    """
    Gera um relatório executivo formal em PDF formato Paisagem (landscape)
    com cabeçalho institucional, sumário de KPIs, filtros aplicados e
    tabela analítica com todas as ocorrências cadastradas.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(letter),
        leftMargin=36,
        rightMargin=36,
        topMargin=32,
        bottomMargin=38
    )
    elements = []
    styles = getSampleStyleSheet()

    # Estilos customizados
    title_style = ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=15,
        leading=18,
        textColor=colors.HexColor("#1E3A8A")
    )
    subtitle_style = ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#334155")
    )
    meta_style = ParagraphStyle(
        name="DocMeta",
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#475569")
    )
    kpi_title_style = ParagraphStyle(
        name="KpiTitle",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=1,
        textColor=colors.whitesmoke
    )
    kpi_val_style = ParagraphStyle(
        name="KpiVal",
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=14,
        alignment=1,
        textColor=colors.whitesmoke
    )
    table_hdr_style = ParagraphStyle(
        name="TableHdr",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=10,
        alignment=1,
        textColor=colors.whitesmoke
    )
    cell_style = ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    )
    cell_bold_style = ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor("#0F172A")
    )

    filtros_info = filtros_info or {}

    # 1. CABEÇALHO INSTITUCIONAL
    header_table_data = [
        [
            Paragraph("🎓 <b>Docente360 — Plataforma de Gestão e Governança Acadêmica</b>", title_style),
            Paragraph(f"<b>Data/Hora:</b> {datetime.datetime.now().strftime('%d/%m/%Y às %H:%M')}", meta_style)
        ],
        [
            Paragraph(f"{titulo}", subtitle_style),
            Paragraph(f"<b>Emitido por:</b> {emitido_por}", meta_style)
        ],
        [
            Paragraph(f"<b>Período:</b> {filtros_info.get('periodo', 'Todo o histórico')} &nbsp;|&nbsp; <b>Status:</b> {filtros_info.get('status', 'Todos')}", meta_style),
            Paragraph(f"<b>Filtro Docente:</b> {filtros_info.get('professor', 'Todos')} &nbsp;|&nbsp; <b>Turma:</b> {filtros_info.get('turma', 'Todas')}", meta_style)
        ]
    ]
    t_header = Table(header_table_data, colWidths=[490, 230])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
        ('TOPPADDING', (0, 0), (-1, -1), 2),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(t_header)
    elements.append(Spacer(1, 10))

    # 2. QUADRO RESUMO DE INDICADORES (KPIS)
    total_ocorr = len(df)
    subst_count = len(df[df["Status"] == "Substituída"]) if not df.empty else 0
    vagas_count = len(df[df["Status"] == "Aula Vaga"]) if not df.empty else 0
    repost_count = len(df[df["Status"] == "Reposta"]) if not df.empty else 0
    pend_count = total_ocorr - subst_count - repost_count
    taxa_subst = (subst_count / total_ocorr * 100) if total_ocorr > 0 else 0.0

    kpi_data = [
        [
            Paragraph("TOTAL DE AUSÊNCIAS", kpi_title_style),
            Paragraph("SUBSTITUIÇÕES", kpi_title_style),
            Paragraph("AULAS VAGAS", kpi_title_style),
            Paragraph("REPOSIÇÕES CONCLUÍDAS", kpi_title_style),
            Paragraph("PENDÊNCIAS OPERACIONAIS", kpi_title_style)
        ],
        [
            Paragraph(str(total_ocorr), kpi_val_style),
            Paragraph(f"{subst_count} ({taxa_subst:.1f}%)", kpi_val_style),
            Paragraph(str(vagas_count), kpi_val_style),
            Paragraph(str(repost_count), kpi_val_style),
            Paragraph(str(pend_count), kpi_val_style)
        ]
    ]
    t_kpi = Table(kpi_data, colWidths=[144, 144, 144, 144, 144])
    t_kpi.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, 1), colors.HexColor('#1E3A8A')),  # Azul marinho
        ('BACKGROUND', (1, 0), (1, 1), colors.HexColor('#2563EB')),  # Azul royal
        ('BACKGROUND', (2, 0), (2, 1), colors.HexColor('#DC2626')),  # Vermelho
        ('BACKGROUND', (3, 0), (3, 1), colors.HexColor('#16A34A')),  # Verde
        ('BACKGROUND', (4, 0), (4, 1), colors.HexColor('#D97706')),  # Laranja
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white)
    ]))
    elements.append(t_kpi)
    elements.append(Spacer(1, 12))

    # 3. TABELA ANALÍTICA DE OCORRÊNCIAS
    if df.empty:
        elements.append(Paragraph("<i>Nenhum registro de ausência encontrado para os critérios selecionados.</i>", meta_style))
    else:
        # 8 colunas somando exatamente 720 pontos
        col_widths = [70, 105, 115, 95, 110, 75, 95, 55]
        headers_table = [
            Paragraph("Data / Horário", table_hdr_style),
            Paragraph("Docente Ausente", table_hdr_style),
            Paragraph("Disciplina & Turma", table_hdr_style),
            Paragraph("Motivo Informado", table_hdr_style),
            Paragraph("Tratativa Operacional", table_hdr_style),
            Paragraph("Status", table_hdr_style),
            Paragraph("Reposição", table_hdr_style),
            Paragraph("Atestado", table_hdr_style)
        ]

        table_rows = [headers_table]

        for _, row in df.iterrows():
            data_horario = f"<b>{row.get('Data', '')}</b><br/>{row.get('Horário', '')}"
            prof_info = f"<b>{row.get('Professor', '')}</b>"
            disc_turma = f"{row.get('Disciplina', '')}<br/><b>Turma:</b> {row.get('Turma', '')}"
            motivo = str(row.get("Motivo", "Não informado"))
            tratativa = str(row.get("Tratativa", "-"))
            status_val = str(row.get("Status", "Pendente"))

            # Cor semântica do status
            cor_status = "#475569"
            if status_val == "Reposta":
                cor_status = "#16A34A"
            elif status_val == "Substituída":
                cor_status = "#2563EB"
            elif status_val == "Aula Vaga":
                cor_status = "#DC2626"
            elif status_val == "Aguardando Homologação":
                cor_status = "#D97706"
            elif status_val == "Pendente":
                cor_status = "#CA8A04"

            status_p = f"<font color='{cor_status}'><b>{status_val}</b></font>"

            info_rep = str(row.get("InfoReposicao", "-"))
            atestado = str(row.get("Atestado", "Não"))

            table_rows.append([
                Paragraph(data_horario, cell_style),
                Paragraph(prof_info, cell_bold_style),
                Paragraph(disc_turma, cell_style),
                Paragraph(motivo, cell_style),
                Paragraph(tratativa, cell_style),
                Paragraph(status_p, cell_style),
                Paragraph(info_rep, cell_style),
                Paragraph(atestado, cell_style)
            ])

        t_ocorrencias = Table(table_rows, colWidths=col_widths, repeatRows=1)
        t_ocorrencias.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
        ]))
        elements.append(t_ocorrencias)

    # 4. BLOCO DE HOMOLOGAÇÃO / ASSINATURAS INSTITUCIONAIS
    elements.append(Spacer(1, 24))
    assinaturas_data = [
        [
            Paragraph("____________________________________________________<br/><b>Coordenação Acadêmica / Direção Pedagógica</b><br/>Homologação e Conformidade Curricular", ParagraphStyle('Ass1', parent=meta_style, alignment=1)),
            Paragraph("____________________________________________________<br/><b>Secretaria Geral e Acadêmica</b><br/>Registro e Controle Operacional de Frequência", ParagraphStyle('Ass2', parent=meta_style, alignment=1))
        ]
    ]
    t_ass = Table(assinaturas_data, colWidths=[360, 360])
    t_ass.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(KeepTogether([t_ass]))

    # Compilação do PDF com o NumberedCanvas
    doc.build(elements, canvasmaker=NumberedCanvas)
    buffer.seek(0)
    return buffer
