"""
Gera o CV em PDF (A4) dinamicamente, puxando texto do banco (settings/projects)
e as imagens reais dos dashboards (não as capturas dos sites).
"""
import io
import os

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import database as db

NAVY = HexColor("#16324F")
BLUE = HexColor("#35688C")
INK = HexColor("#1C1B18")
MUTED = HexColor("#5B584F")
DIM = HexColor("#928E82")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

DASHBOARD_IMAGES = [
    ("gallery/dash-faturamento.jpg", "Faturamento por Loja"),
    ("gallery/dash-manutencao.jpg", "GTM — Controle de Frota"),
    ("gallery/dash-controle.jpg", "CEGM — Controle de Consumo"),
    ("gallery/telaadm.png", "Sistema Administrativo"),
    ("gallery/contratos.png", "SagaCap Contratos — BI"),
]

EXPERIENCE = [
    ("Centro América", "Atual",
     "Estruturo e automatizo planilhas que sustentam os processos do setor, "
     "do controle diário à tomada de decisão. Elimino tarefas manuais repetitivas "
     "e mantenho os controles administrativos usados diariamente."),
    ("CTR Contabilidade", "Anterior",
     "Rotina fiscal: apuração de impostos dos regimes Simples Nacional e Lucro Presumido, "
     "emissão de notas fiscais e controle de obrigações."),
    ("Instituto Mais Visão", "Anterior",
     "Atuação administrativa e automação de planilhas: controle de estoque, "
     "fluxo de caixa e rotinas do setor."),
]

EDUCATION = [
    "Bacharel em Administração",
    "MBA em Administração e Contabilidade Tributária",
    "Ciências Contábeis — 6º semestre",
    "Pós-graduação em Licitações e Contratos — em andamento",
    "Pós-graduação em Administração Pública — em andamento",
]

SITE_URL = "https://yagohenrick.up.railway.app/"


def _styles():
    ss = getSampleStyleSheet()
    styles = {
        "name": ParagraphStyle("name", parent=ss["Title"], fontName="Helvetica-Bold",
                                fontSize=24, textColor=INK, spaceAfter=2, alignment=TA_LEFT),
        "role": ParagraphStyle("role", parent=ss["Normal"], fontName="Helvetica-Bold",
                                fontSize=12.5, textColor=NAVY, spaceAfter=6),
        "contact": ParagraphStyle("contact", parent=ss["Normal"], fontName="Helvetica",
                                   fontSize=9.5, textColor=MUTED, spaceAfter=0),
        "h2": ParagraphStyle("h2", parent=ss["Normal"], fontName="Helvetica-Bold",
                              fontSize=12, textColor=NAVY, spaceBefore=16, spaceAfter=8,
                              letterSpacing=0.5),
        "body": ParagraphStyle("body", parent=ss["Normal"], fontName="Helvetica",
                                fontSize=9.7, textColor=INK, leading=14, spaceAfter=6),
        "job_title": ParagraphStyle("job_title", parent=ss["Normal"], fontName="Helvetica-Bold",
                                     fontSize=10.5, textColor=INK, spaceAfter=1),
        "job_date": ParagraphStyle("job_date", parent=ss["Normal"], fontName="Helvetica-Oblique",
                                    fontSize=8.5, textColor=DIM, spaceAfter=3),
        "bullet": ParagraphStyle("bullet", parent=ss["Normal"], fontName="Helvetica",
                                  fontSize=9.3, textColor=INK, leading=13, leftIndent=10, spaceAfter=8),
        "caption": ParagraphStyle("caption", parent=ss["Normal"], fontName="Helvetica",
                                   fontSize=7.8, textColor=MUTED, alignment=1, spaceBefore=3),
        "skill": ParagraphStyle("skill", parent=ss["Normal"], fontName="Helvetica",
                                 fontSize=9, textColor=INK, leading=14),
    }
    return styles


def generate_cv_pdf() -> bytes:
    settings = db.get_settings()
    projects = db.get_projects()

    # Junta as tags de todos os projetos, sem repetir, mantendo a ordem de aparição
    skills = []
    for p in projects:
        for tag in p["tags"].split(","):
            tag = tag.strip()
            if tag and tag not in skills:
                skills.append(tag)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        topMargin=18 * mm, bottomMargin=16 * mm, leftMargin=18 * mm, rightMargin=18 * mm,
        title="Yago Henrick Alves Gomes — CV",
    )
    s = _styles()
    story = []

    # ---- Cabeçalho ----
    story.append(Paragraph("Yago Henrick Alves Gomes", s["name"]))
    story.append(Paragraph(settings.get("hero_role", {}).get("pt", ""), s["role"]))
    contact_line = (
        f'{settings.get("contact_email", {}).get("pt", "")} &nbsp;|&nbsp; '
        f'{settings.get("linkedin_url", {}).get("pt", "")} &nbsp;|&nbsp; '
        f'{SITE_URL}'
    )
    story.append(Paragraph(contact_line, s["contact"]))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.2, color=NAVY, spaceAfter=4))

    # ---- Resumo ----
    story.append(Paragraph("RESUMO", s["h2"]))
    for key in ["about_p1", "about_p2", "about_p3"]:
        text = settings.get(key, {}).get("pt", "")
        if text:
            story.append(Paragraph(text, s["body"]))

    # ---- Experiência ----
    story.append(Paragraph("EXPERIÊNCIA", s["h2"]))
    for title, date, desc in EXPERIENCE:
        block = [
            Paragraph(f"{title} <font color='#928E82'>— {date}</font>", s["job_title"]),
            Paragraph(desc, s["bullet"]),
        ]
        story.append(KeepTogether(block))

    # ---- Formação ----
    story.append(Paragraph("FORMAÇÃO", s["h2"]))
    for edu in EDUCATION:
        story.append(Paragraph(f"•  {edu}", s["bullet"]))

    # ---- Competências ----
    story.append(Paragraph("COMPETÊNCIAS", s["h2"]))
    story.append(Paragraph("  •  ".join(skills), s["skill"]))

    # ---- Dashboards e Sistemas (apenas imagens de dashboard, sem prints de sites) ----
    story.append(Paragraph("DASHBOARDS E SISTEMAS", s["h2"]))
    img_cell_w = 55 * mm
    img_cell_h = 34 * mm
    row, rows = [], []
    for rel_path, caption in DASHBOARD_IMAGES:
        full_path = os.path.join(STATIC_DIR, rel_path)
        if not os.path.exists(full_path):
            continue
        img = Image(full_path, width=img_cell_w, height=img_cell_h)
        cell = [img, Paragraph(caption, s["caption"])]
        row.append(cell)
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        while len(row) < 3:
            row.append([Spacer(1, 1), Spacer(1, 1)])
        rows.append(row)

    if rows:
        table_data = [[Table([[c[0]], [c[1]]], colWidths=[img_cell_w]) for c in r] for r in rows]
        img_table = Table(table_data, colWidths=[img_cell_w + 4] * 3, hAlign="LEFT")
        img_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))
        story.append(img_table)

    doc.build(story)
    return buf.getvalue()
