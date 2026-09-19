"""Render a project dict to JSON, DOCX or PDF. Public docs omit editor hints."""

from __future__ import annotations

import json
from io import BytesIO
from typing import Any

from schema import PRODUCT_EN, PRODUCT_ZH, steps_for

GOLD = "C7A35A"
INK = "1B1408"
MUTED = "6B5A3A"
PAPER = "F7F1E6"
LINE = "E6D7B8"
QUOTE_KEYS = {
    "oneLiner",
    "tomorrowHook",
    "sellPoint",
    "feelPrimary",
    "identityPlay",
    "bpUnlike",
    "bpShine",
    "controlPoint",
    "needPrimary",
}


def _lang(node: dict, lang: str) -> str:
    if not isinstance(node, dict):
        return str(node or "")
    return node.get(lang) or node.get("zh") or node.get("en") or ""


def _option_label(field: dict, value: str, lang: str, extras: list | None = None) -> str:
    for opt in list(field.get("options") or []) + list(extras or []):
        if opt.get("id") == value:
            return _lang(opt, lang)
    return value


def _display(field: dict, value: Any, lang: str, custom: dict | None = None) -> str:
    if value is None or value == "" or value == []:
        return ""
    extras = (custom or {}).get(field.get("key") or "") or []
    kind = field.get("kind")
    if kind in ("radio", "select") and isinstance(value, str):
        return _option_label(field, value, lang, extras)
    if kind == "check" and isinstance(value, list):
        return "、".join(_option_label(field, v, lang, extras) for v in value)
    return str(value).strip()


def _type_label(data: dict, lang: str) -> str:
    if data.get("docType") == "business":
        return "商业计划书" if lang == "zh" else "Investor plan"
    return "游戏框架策划案" if lang == "zh" else "Game framework brief"


def iter_sections(data: dict, scope: str, step_id: str | None, sub_id: str | None, lang: str):
    doc_type = data.get("docType") or "game"
    steps = steps_for(doc_type)
    custom = data.get("__customOptions") or {}
    if scope == "step":
        steps = [s for s in steps if s["id"] == step_id]
    elif scope == "sub":
        steps = [s for s in steps if s["id"] == step_id]
    for step in steps:
        if scope == "sub" and step.get("subs"):
            for sub in step["subs"]:
                if sub["id"] != sub_id:
                    continue
                yield _pack_block(sub["no"], _lang(sub["title"], lang), sub.get("fields") or [], data, custom, lang, level=2)
            return
        yield _pack_block(step["no"], _lang(step["title"], lang), step.get("fields") or [], data, custom, lang, level=1)
        if scope != "step":
            for sub in step.get("subs") or []:
                yield _pack_block(sub["no"], _lang(sub["title"], lang), sub.get("fields") or [], data, custom, lang, level=2)


def _pack_block(no: str, title: str, fields: list, data: dict, custom: dict, lang: str, level: int) -> dict:
    rows = []
    for f in fields:
        value = _display(f, data.get(f["key"]), lang, custom)
        if not value:
            continue
        rows.append(
            {
                "key": f["key"],
                "kind": f.get("kind") or "text",
                "label": _lang(f["label"], lang),
                "value": value,
            }
        )
    return {"no": no, "title": title, "level": level, "rows": rows}


def to_json_bytes(project: dict) -> bytes:
    return json.dumps(project, ensure_ascii=False, indent=2).encode("utf-8")


def _split_rows(rows: list[dict]) -> tuple[list[dict], list[dict]]:
    compact, narrative = [], []
    for row in rows:
        if row["kind"] in ("radio", "select", "check", "number", "range") and row["key"] not in QUOTE_KEYS:
            compact.append(row)
        else:
            narrative.append(row)
    return compact, narrative


def _shade_cell(cell, fill: str) -> None:
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn

    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def _set_run_font(run, size, bold=False, color=None, italic=False) -> None:
    from docx.shared import Pt, RGBColor
    from docx.oxml.ns import qn

    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size)
    run.font.name = "Calibri"
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        from docx.oxml import OxmlElement

        rfonts = OxmlElement("w:rFonts")
        rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), "Calibri")
    rfonts.set(qn("w:hAnsi"), "Calibri")
    rfonts.set(qn("w:eastAsia"), "微软雅黑")
    if color:
        run.font.color.rgb = RGBColor(int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16))


def _add_quote(doc, text: str) -> None:
    from docx.shared import Cm, Pt, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    table = doc.add_table(rows=1, cols=2)
    table.autofit = True
    bar, body = table.rows[0].cells
    bar.text = ""
    _shade_cell(bar, GOLD)
    bar.width = Cm(0.28)
    body.text = ""
    _shade_cell(body, PAPER)
    p = body.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    _set_run_font(run, 12, italic=True, color=INK)
    p.paragraph_format.space_after = Pt(8)


def _add_kv_table(doc, rows: list[dict], lang: str) -> None:
    from docx.shared import Cm, Pt
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    table = doc.add_table(rows=1 + len(rows), cols=2)
    table.style = "Table Grid"
    table.autofit = True
    headers = ("项目", "内容") if lang == "zh" else ("Item", "Value")
    for i, label in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        _shade_cell(cell, INK)
        p = cell.paragraphs[0]
        run = p.add_run(label)
        _set_run_font(run, 10, bold=True, color="F4E4C1")
    for r_i, row in enumerate(rows):
        fill = PAPER if r_i % 2 == 0 else "FFFFFF"
        left, right = table.rows[r_i + 1].cells
        left.text = ""
        right.text = ""
        _shade_cell(left, fill)
        _shade_cell(right, fill)
        lp = left.paragraphs[0]
        lr = lp.add_run(row["label"])
        _set_run_font(lr, 10, bold=True, color=INK)
        rp = right.paragraphs[0]
        rr = rp.add_run(row["value"])
        _set_run_font(rr, 10, color=INK)
    table.columns[0].width = Cm(4.4)
    table.columns[1].width = Cm(12.0)
    for row in table.rows:
        for cell in row.cells:
            tc = cell._tc
            tc_pr = tc.get_or_add_tcPr()
            tc_mar = OxmlElement("w:tcMar")
            for edge, val in (("top", "60"), ("bottom", "60"), ("left", "80"), ("right", "80")):
                node = OxmlElement(f"w:{edge}")
                node.set(qn("w:w"), val)
                node.set(qn("w:type"), "dxa")
                tc_mar.append(node)
            tc_pr.append(tc_mar)


def to_docx_bytes(project: dict, scope: str, step_id: str | None, sub_id: str | None, lang: str) -> bytes:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Cm, Pt, RGBColor
    from docx.oxml.ns import qn

    data = project.get("data") or project
    name = data.get("projectName") or PRODUCT_ZH
    doc = Document()
    section = doc.sections[0]
    section.top_margin = Cm(2.0)
    section.bottom_margin = Cm(2.0)
    section.left_margin = Cm(2.0)
    section.right_margin = Cm(2.0)
    section.page_width = Cm(21.0)
    section.page_height = Cm(29.7)

    style = doc.styles["Normal"]
    style.font.name = "Calibri"
    style.font.size = Pt(11)
    style.element.rPr.rFonts.set(qn("w:eastAsia"), "微软雅黑")

    kicker = doc.add_paragraph()
    kr = kicker.add_run(_type_label(data, lang).upper())
    _set_run_font(kr, 10, bold=True, color=GOLD)
    kicker.paragraph_format.space_after = Pt(2)

    title = doc.add_paragraph()
    tr = title.add_run(name)
    _set_run_font(tr, 26, bold=True, color=INK)
    title.paragraph_format.space_after = Pt(8)

    if data.get("oneLiner"):
        _add_quote(doc, str(data["oneLiner"]))

    brand = doc.add_paragraph()
    br = brand.add_run(PRODUCT_ZH if lang == "zh" else PRODUCT_EN)
    _set_run_font(br, 9, color=MUTED)
    brand.paragraph_format.space_after = Pt(16)

    for block in iter_sections(data, scope, step_id, sub_id, lang):
        if not block["rows"]:
            continue
        heading = doc.add_heading(level=1 if block["level"] == 1 else 2)
        heading.clear()
        run = heading.add_run(f"{block['no']}  {block['title']}")
        _set_run_font(run, 16 if block["level"] == 1 else 13, bold=True, color=INK)
        heading.paragraph_format.space_before = Pt(16)
        heading.paragraph_format.space_after = Pt(8)

        compact, narrative = _split_rows(block["rows"])
        if compact:
            _add_kv_table(doc, compact, lang)
            spacer = doc.add_paragraph()
            spacer.paragraph_format.space_after = Pt(6)

        for row in narrative:
            h3 = doc.add_heading(level=3)
            h3.clear()
            hr = h3.add_run(row["label"])
            _set_run_font(hr, 12, bold=True, color="8A5A12")
            h3.paragraph_format.space_before = Pt(8)
            h3.paragraph_format.space_after = Pt(4)
            if row["key"] in QUOTE_KEYS:
                _add_quote(doc, row["value"])
            else:
                p = doc.add_paragraph()
                vr = p.add_run(row["value"])
                _set_run_font(vr, 11, color=INK)
                p.paragraph_format.space_after = Pt(8)
                p.paragraph_format.line_spacing = 1.25

    buf = BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _pdf_font() -> tuple[str, str]:
    from pathlib import Path

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = (
        "/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansSC-Regular.ttf",
        "C:/Windows/Fonts/msyh.ttf",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    )
    for path in candidates:
        if not Path(path).exists():
            continue
        try:
            pdfmetrics.registerFont(TTFont("BriefBody", path))
            return "BriefBody", "BriefBody"
        except Exception:
            continue
    return "Helvetica", "Helvetica-Bold"


def to_pdf_bytes(project: dict, scope: str, step_id: str | None, sub_id: str | None, lang: str) -> bytes:
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        HRFlowable,
        KeepTogether,
        Paragraph,
        SimpleDocTemplate,
        Spacer,
        Table,
        TableStyle,
    )

    font_name, font_bold = _pdf_font()
    data = project.get("data") or project
    name = data.get("projectName") or PRODUCT_ZH
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=16 * mm,
        rightMargin=16 * mm,
        topMargin=14 * mm,
        bottomMargin=16 * mm,
        title=name,
        author=PRODUCT_EN,
    )
    base = getSampleStyleSheet()
    kicker_s = ParagraphStyle("Kicker", parent=base["Normal"], fontName=font_bold, fontSize=9, textColor=colors.HexColor("#C7A35A"), leading=12, spaceAfter=2)
    title_s = ParagraphStyle("TitleX", parent=base["Title"], fontName=font_bold, fontSize=22, textColor=colors.HexColor("#1B1408"), leading=28, alignment=TA_LEFT, spaceAfter=8)
    h1_s = ParagraphStyle("H1X", parent=base["Heading1"], fontName=font_bold, fontSize=15, textColor=colors.HexColor("#1B1408"), leading=20, spaceBefore=14, spaceAfter=6)
    h2_s = ParagraphStyle("H2X", parent=base["Heading2"], fontName=font_bold, fontSize=13, textColor=colors.HexColor("#1B1408"), leading=18, spaceBefore=10, spaceAfter=4)
    h3_s = ParagraphStyle("H3X", parent=base["Heading3"], fontName=font_bold, fontSize=11, textColor=colors.HexColor("#8A5A12"), leading=15, spaceBefore=8, spaceAfter=3)
    body_s = ParagraphStyle("BodyX", parent=base["Normal"], fontName=font_name, fontSize=10, leading=15, textColor=colors.HexColor("#1B1408"), spaceAfter=8)
    quote_s = ParagraphStyle("QuoteX", parent=base["Normal"], fontName=font_name, fontSize=11, leading=16, textColor=colors.HexColor("#1B1408"), leftIndent=6, spaceAfter=0)
    cell_s = ParagraphStyle("CellX", parent=base["Normal"], fontName=font_name, fontSize=9, leading=13, textColor=colors.HexColor("#1B1408"))
    cell_b = ParagraphStyle("CellB", parent=cell_s, fontName=font_bold)
    head_s = ParagraphStyle("HeadX", parent=base["Normal"], fontName=font_bold, fontSize=9, leading=13, textColor=colors.HexColor("#F4E4C1"))
    brand_s = ParagraphStyle("BrandX", parent=base["Normal"], fontName=font_name, fontSize=8, textColor=colors.HexColor("#6B5A3A"), spaceAfter=10)

    def esc(text: str) -> str:
        return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>")

    story: list = [
        Paragraph(esc(_type_label(data, lang)), kicker_s),
        Paragraph(esc(name), title_s),
    ]
    if data.get("oneLiner"):
        quote = Table(
            [[Paragraph(esc(str(data["oneLiner"])), quote_s)]],
            colWidths=[178 * mm],
        )
        quote.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F1E6")),
                    ("BOX", (0, 0), (-1, -1), 0, colors.HexColor("#F7F1E6")),
                    ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#C7A35A")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        story.append(quote)
        story.append(Spacer(1, 6))
    story.append(Paragraph(esc(PRODUCT_ZH if lang == "zh" else PRODUCT_EN), brand_s))
    story.append(HRFlowable(width="100%", color=colors.HexColor("#C7A35A"), thickness=1.2, spaceAfter=8))

    def kv_table(rows: list[dict]) -> Table:
        head_l = "项目" if lang == "zh" else "Item"
        head_r = "内容" if lang == "zh" else "Value"
        grid = [[Paragraph(esc(head_l), head_s), Paragraph(esc(head_r), head_s)]]
        for row in rows:
            grid.append([Paragraph(esc(row["label"]), cell_b), Paragraph(esc(row["value"]), cell_s)])
        table = Table(grid, colWidths=[42 * mm, 136 * mm])
        cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B1408")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#F4E4C1")),
            ("FONTNAME", (0, 0), (-1, 0), font_bold),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("GRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#E6D7B8")),
        ]
        for i in range(1, len(grid)):
            if i % 2 == 1:
                cmds.append(("BACKGROUND", (0, i), (-1, i), colors.HexColor("#F7F1E6")))
        table.setStyle(TableStyle(cmds))
        return table

    for block in iter_sections(data, scope, step_id, sub_id, lang):
        if not block["rows"]:
            continue
        heading = Paragraph(esc(f"{block['no']}  {block['title']}"), h1_s if block["level"] == 1 else h2_s)
        compact, narrative = _split_rows(block["rows"])
        chunk = [heading]
        if compact:
            chunk.append(kv_table(compact))
            chunk.append(Spacer(1, 6))
        for row in narrative:
            chunk.append(Paragraph(esc(row["label"]), h3_s))
            if row["key"] in QUOTE_KEYS:
                q = Table([[Paragraph(esc(row["value"]), quote_s)]], colWidths=[178 * mm])
                q.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F7F1E6")),
                            ("LINEBEFORE", (0, 0), (0, -1), 3, colors.HexColor("#C7A35A")),
                            ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                            ("TOPPADDING", (0, 0), (-1, -1), 6),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                        ]
                    )
                )
                chunk.append(q)
                chunk.append(Spacer(1, 4))
            else:
                chunk.append(Paragraph(esc(row["value"]), body_s))
        story.append(KeepTogether(chunk[:3] if len(chunk) > 3 else chunk))
        for extra in chunk[3:]:
            story.append(extra)

    def footer(canvas, doc_):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#C7A35A"))
        canvas.setLineWidth(0.6)
        canvas.line(16 * mm, 10 * mm, A4[0] - 16 * mm, 10 * mm)
        canvas.setFont(font_name, 8)
        canvas.setFillColor(colors.HexColor("#6B5A3A"))
        label = PRODUCT_ZH if lang == "zh" else PRODUCT_EN
        canvas.drawString(16 * mm, 6 * mm, label)
        canvas.drawRightString(A4[0] - 16 * mm, 6 * mm, str(doc_.page))
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    return buf.getvalue()
