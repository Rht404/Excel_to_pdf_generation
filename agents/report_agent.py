# # # report_agent.py
# # from pathlib import Path
# # from typing import Dict, List, Any
# # import re
# # from datetime import datetime

# # from reportlab.lib.pagesizes import A4
# # from reportlab.platypus import (
# #     SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
# # )
# # from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# # from reportlab.lib import colors
# # from reportlab.platypus import KeepTogether

# # # paths
# # BASE_DIR = Path(__file__).resolve().parent.parent
# # OUTPUTS_DIR = BASE_DIR / "outputs"
# # OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# # # styles
# # def _styles():
# #     s = getSampleStyleSheet()
# #     s.add(ParagraphStyle(
# #         "H1", parent=s["Heading1"],
# #         fontName="Helvetica-Bold", fontSize=20,
# #         leading=24, alignment=1, textColor=colors.darkblue,
# #         spaceAfter=8
# #     ))
# #     s.add(ParagraphStyle(
# #         "H2", parent=s["Heading2"],
# #         fontName="Helvetica-Bold", fontSize=14,
# #         leading=18, textColor=colors.darkred,
# #         spaceBefore=8, spaceAfter=4
# #     ))
# #     s.add(ParagraphStyle(
# #         "Body", parent=s["BodyText"],
# #         fontSize=10, leading=14,
# #         textColor=colors.black, spaceAfter=3
# #     ))
# #     s.add(ParagraphStyle(
# #         "Caption", parent=s["BodyText"],
# #         fontSize=9, leading=12,
# #         textColor=colors.grey, spaceAfter=4, alignment=0, italic=True
# #     ))
# #     return s

# # # helpers
# # def _scaled_img(path: str, max_w=380, max_h=180) -> Image:
# #     try:
# #         im = Image(path)
# #         w, h = im.wrap(0, 0)
# #         if w > max_w:
# #             h = h * (max_w / w); w = max_w
# #         if h > max_h:
# #             w = w * (max_h / h); h = max_h
# #         im._restrictSize(w, h)
# #         return im
# #     except Exception:
# #         return Paragraph(f"[Image missing: {path}]", getSampleStyleSheet()["BodyText"])

# # def _bullets_from_text(text: str) -> List[str]:
# #     lines = (text or "").splitlines()
# #     out = []
# #     for ln in lines:
# #         ln = ln.strip()
# #         if not ln:
# #             continue
# #         out.append(re.sub(r'^[\*\-\u2022]\s*', '', ln))
# #     return out

# # def _normalize_bullet(ln: str) -> str:
# #     ln = ln.strip()
# #     ln = re.sub(r'\*+\s*$', '', ln)
# #     ln = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', ln)
# #     ln = re.sub(r'`([^`]+)`', r'<font face="Courier">\1</font>', ln)
# #     return ln

# # class ReportAgent:
# #     def generate_pdf(
# #         self,
# #         summary: Dict[str, Dict[str, Any]],
# #         insights: Dict[str, str],
# #         charts: Dict[str, List[Dict[str, str]]],
# #         exec_summary_text: str,
# #         business_insights: Dict[str, str],
# #     ) -> str:
# #         styles = _styles()
# #         pdf_path = OUTPUTS_DIR / "report.pdf"

# #         doc = SimpleDocTemplate(
# #             str(pdf_path),
# #             pagesize=A4,
# #             leftMargin=45, rightMargin=45, topMargin=36, bottomMargin=36,
# #             title="CrewAI Insights Report",
# #         )

# #         elements: List[Any] = []

# #         # Cover Page
# #         meta = summary.get("metadata", {})
# #         elements.append(Paragraph("CrewAI Insights Report", styles["H1"]))
# #         elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Body"]))
# #         if meta.get("file_name"):
# #             elements.append(Paragraph(f"Dataset: {meta['file_name']}", styles["Body"]))
# #         elements.append(Spacer(1, 10))

# #         # Executive Summary
# #         elements.append(Paragraph("Executive Summary", styles["H2"]))
# #         exec_bullets = _bullets_from_text(exec_summary_text)
# #         if exec_bullets:
# #             for b in exec_bullets:
# #                 elements.append(Paragraph(_normalize_bullet(b), styles["Body"]))
# #         else:
# #             elements.append(Paragraph("No executive summary generated.", styles["Body"]))
# #         elements.append(Spacer(1, 12))

# #         sheets = summary.get("sheets", summary)

# #         for idx, (sheet, info) in enumerate(sheets.items()):
# #             if idx > 0:
# #                 elements.append(Spacer(1, 12))

# #             # Header
# #             elements.append(Paragraph(f"Sheet: <b>{sheet}</b>", styles["H2"]))

# #             # Dataset Profile
# #             rows, cols = info.get("shape", (0, 0))
# #             n_num = len(info.get("numeric_cols", []))
# #             n_cat = len(info.get("categorical_cols", []))
# #             n_dt  = len(info.get("datetime_cols", []))
# #             elements.append(Paragraph(
# #                 f"Profile: <b>{rows}×{cols}</b>; numeric=<b>{n_num}</b>, "
# #                 f"categorical=<b>{n_cat}</b>, datetime=<b>{n_dt}</b>.",
# #                 styles["Body"]
# #             ))

# #             miss = info.get("missing_by_col", {})
# #             if miss:
# #                 topmiss = sorted(miss.items(), key=lambda x: x[1], reverse=True)[:5]
# #                 miss_txt = ", ".join(f"{c}: <b>{pct:.1f}%</b>" for c, pct in topmiss)
# #                 elements.append(Paragraph(f"Top missing %: {miss_txt}", styles["Body"]))

# #             # Descriptive Statistics
# #             elements.append(Paragraph("Descriptive Statistics", styles["H2"]))
# #             num_desc = info.get("numeric_describe", {})
# #             if num_desc:
# #                 table_data = [["Metric"] + list(num_desc.keys())]
# #                 stats = ["count", "mean", "std", "min", "max"]
# #                 for stat in stats:
# #                     row = [stat]
# #                     for col in num_desc.keys():
# #                         val = num_desc[col].get(stat)
# #                         row.append(val if val is not None else "")
# #                     table_data.append(row)
# #                 t = Table(table_data, repeatRows=1)
# #                 t.hAlign = "LEFT"
# #                 t.setStyle(TableStyle([
# #                     ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
# #                     ("GRID", (0,0), (-1,-1), 0.25, colors.black),
# #                     ("FONTSIZE", (0,0), (-1,-1), 9),
# #                 ]))
# #                 elements.append(t)

# #             top_cats = info.get("top_categories", {})
# #             if top_cats:
# #                 for col, vals in top_cats.items():
# #                     txt = ", ".join([f"{v[0]} ({v[1]})" for v in vals])
# #                     elements.append(Paragraph(f"Top categories for {col}: {txt}", styles["Body"]))

# #             # Correlation Matrix
# #             corr = info.get("corr", {})
# #             if corr:
# #                 corr_table = [[""] + list(corr.keys())]
# #                 for row_key, row_vals in corr.items():
# #                     row = [row_key] + [row_vals.get(c, "") for c in corr.keys()]
# #                     corr_table.append(row)

# #                 t = Table(corr_table, repeatRows=1)
# #                 t.hAlign = "LEFT"
# #                 t.setStyle(TableStyle([
# #                     ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
# #                     ("GRID", (0,0), (-1,-1), 0.25, colors.black),
# #                     ("FONTSIZE", (0,0), (-1,-1), 8),
# #                 ]))

# #                 elements.append(KeepTogether([
# #                     Paragraph("Correlation Matrix:", styles["Body"]),
# #                     t,
# #                     Spacer(1, 12)
# #                 ]))

# #             # Analytical Insights
# #             elements.append(Paragraph("Analytical Insights", styles["H2"]))
# #             insight_text = insights.get(sheet) or ""
# #             insight_bullets = _bullets_from_text(insight_text) if insight_text else []
# #             if insight_bullets:
# #                 for raw in insight_bullets:
# #                     elements.append(Paragraph(_normalize_bullet(raw), styles["Body"]))
# #             else:
# #                 elements.append(Paragraph("No insights generated.", styles["Body"]))
# #             elements.append(PageBreak())

# #             # Visualizations 
# #             pic_entries = charts.get(sheet, [])
# #             if pic_entries:
# #                 elements.append(Paragraph("Visualizations", styles["H2"]))
# #                 elements.append(Spacer(1, 10))
# #                 row = []
# #                 for idx, entry in enumerate(pic_entries):
# #                     img = _scaled_img(entry.get("path", ""))
# #                     row.append(img)

# #                     if len(row) == 2 or idx == len(pic_entries) - 1:
# #                         if len(row) < 2:
# #                             row.append(Spacer(1, 1))
# #                         t = Table([row], colWidths=[260, 260])
# #                         t.setStyle(TableStyle([
# #                             ("VALIGN", (0, 0), (-1, -1), "TOP"),
# #                             ("LEFTPADDING", (0, 0), (-1, -1), 0),
# #                             ("RIGHTPADDING", (0, 0)
                             





# # report_agent.py
# from pathlib import Path
# from typing import Dict, List, Any
# import re
# from datetime import datetime

# from reportlab.lib.pagesizes import A4
# from reportlab.platypus import (
#     SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
# )
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib import colors
# from reportlab.platypus import KeepTogether

# # paths
# BASE_DIR = Path(__file__).resolve().parent.parent
# OUTPUTS_DIR = BASE_DIR / "outputs"
# OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# # styles
# def _styles():
#     s = getSampleStyleSheet()
#     s.add(ParagraphStyle(
#         "H1", parent=s["Heading1"],
#         fontName="Helvetica-Bold", fontSize=20,
#         leading=24, alignment=1, textColor=colors.darkblue,
#         spaceAfter=8
#     ))
#     s.add(ParagraphStyle(
#         "H2", parent=s["Heading2"],
#         fontName="Helvetica-Bold", fontSize=14,
#         leading=18, textColor=colors.darkred,
#         spaceBefore=8, spaceAfter=4
#     ))
#     s.add(ParagraphStyle(
#         "Body", parent=s["BodyText"],
#         fontSize=10, leading=14,
#         textColor=colors.black, spaceAfter=3
#     ))
#     s.add(ParagraphStyle(
#         "Caption", parent=s["BodyText"],
#         fontSize=9, leading=12,
#         textColor=colors.grey, spaceAfter=4, alignment=0, italic=True
#     ))
#     return s

# # helpers
# def _scaled_img(path: str, max_w=380, max_h=180) -> Image:
#     try:
#         im = Image(path)
#         w, h = im.wrap(0, 0)
#         if w > max_w:
#             h = h * (max_w / w); w = max_w
#         if h > max_h:
#             w = w * (max_h / h); h = max_h
#         im._restrictSize(w, h)
#         return im
#     except Exception:
#         return Paragraph(f"[Image missing: {path}]", getSampleStyleSheet()["BodyText"])

# def _bullets_from_text(text: str) -> List[str]:
#     lines = (text or "").splitlines()
#     out = []
#     for ln in lines:
#         ln = ln.strip()
#         if not ln:
#             continue
#         out.append(re.sub(r'^[\*\-\u2022]\s*', '', ln))
#     return out

# def _normalize_bullet(ln: str) -> str:
#     ln = ln.strip()
#     ln = re.sub(r'\*+\s*$', '', ln)
#     ln = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', ln)
#     ln = re.sub(r'`([^`]+)`', r'<font face="Courier">\1</font>', ln)
#     return ln

# class ReportAgent:
#     def generate_pdf(
#         self,
#         summary: Dict[str, Dict[str, Any]],
#         insights: Dict[str, str],
#         charts: Dict[str, List[Dict[str, str]]],
#         exec_summary_text: str,
#         business_insights: Dict[str, str],
#     ) -> str:
#         styles = _styles()
#         pdf_path = OUTPUTS_DIR / "report.pdf"

#         doc = SimpleDocTemplate(
#             str(pdf_path),
#             pagesize=A4,
#             leftMargin=45, rightMargin=45, topMargin=36, bottomMargin=36,
#             title="LangGraph Insights Report",
#         )

#         elements: List[Any] = []

#         # Cover Page
#         meta = summary.get("metadata", {})
#         elements.append(Paragraph("LangGraph Insights Report", styles["H1"]))
#         elements.append(Paragraph(f"Date: {datetime.now().strftime('%Y-%m-%d')}", styles["Body"]))
#         if meta.get("file_name"):
#             elements.append(Paragraph(f"Dataset: {meta['file_name']}", styles["Body"]))
#         elements.append(Spacer(1, 10))

#         # Executive Summary
#         elements.append(Paragraph("Executive Summary", styles["H2"]))
#         exec_bullets = _bullets_from_text(exec_summary_text)
#         if exec_bullets:
#             for b in exec_bullets:
#                 elements.append(Paragraph(_normalize_bullet(b), styles["Body"]))
#         else:
#             elements.append(Paragraph("No executive summary generated.", styles["Body"]))
#         elements.append(Spacer(1, 12))

#         sheets = summary.get("sheets", summary)
#         total_sheets = len(sheets)

#         for idx, (sheet, info) in enumerate(sheets.items()):
#             if idx > 0:
#                 elements.append(Spacer(1, 12))

#             # Header
#             elements.append(Paragraph(f"Sheet: <b>{sheet}</b>", styles["H2"]))

#             # Dataset Profile
#             rows, cols = info.get("shape", (0, 0))
#             n_num = len(info.get("numeric_cols", []))
#             n_cat = len(info.get("categorical_cols", []))
#             n_dt  = len(info.get("datetime_cols", []))
#             elements.append(Paragraph(
#                 f"Profile: <b>{rows}×{cols}</b>; numeric=<b>{n_num}</b>, "
#                 f"categorical=<b>{n_cat}</b>, datetime=<b>{n_dt}</b>.",
#                 styles["Body"]
#             ))

#             miss = info.get("missing_by_col", {})
#             if miss:
#                 topmiss = sorted(miss.items(), key=lambda x: x[1], reverse=True)[:5]
#                 miss_txt = ", ".join(f"{c}: <b>{pct:.1f}%</b>" for c, pct in topmiss)
#                 elements.append(Paragraph(f"Top missing %: {miss_txt}", styles["Body"]))

#             # Descriptive Statistics
#             elements.append(Paragraph("Descriptive Statistics", styles["H2"]))
#             num_desc = info.get("numeric_describe", {})
#             if num_desc:
#                 table_data = [["Metric"] + list(num_desc.keys())]
#                 stats = ["count", "mean", "std", "min", "max"]
#                 for stat in stats:
#                     row = [stat]
#                     for col in num_desc.keys():
#                         val = num_desc[col].get(stat)
#                         row.append(val if val is not None else "")
#                     table_data.append(row)
#                 t = Table(table_data, repeatRows=1)
#                 t.hAlign = "LEFT"
#                 t.setStyle(TableStyle([
#                     ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
#                     ("GRID", (0,0), (-1,-1), 0.25, colors.black),
#                     ("FONTSIZE", (0,0), (-1,-1), 9),
#                 ]))
#                 elements.append(t)

#             top_cats = info.get("top_categories", {})
#             if top_cats:
#                 for col, vals in top_cats.items():
#                     txt = ", ".join([f"{v[0]} ({v[1]})" for v in vals])
#                     elements.append(Paragraph(f"Top categories for {col}: {txt}", styles["Body"]))

#             # Correlation Matrix
#             corr = info.get("corr", {})
#             if corr:
#                 corr_table = [[""] + list(corr.keys())]
#                 for row_key, row_vals in corr.items():
#                     row = [row_key] + [row_vals.get(c, "") for c in corr.keys()]
#                     corr_table.append(row)

#                 t = Table(corr_table, repeatRows=1)
#                 t.hAlign = "LEFT"
#                 t.setStyle(TableStyle([
#                     ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
#                     ("GRID", (0,0), (-1,-1), 0.25, colors.black),
#                     ("FONTSIZE", (0,0), (-1,-1), 8),
#                 ]))

#                 elements.append(KeepTogether([
#                     Paragraph("Correlation Matrix:", styles["Body"]),
#                     t,
#                     Spacer(1, 12)
#                 ]))

#             # Analytical Insights
#             elements.append(Paragraph("Analytical Insights", styles["H2"]))
#             insight_text = insights.get(sheet) or ""
#             insight_bullets = _bullets_from_text(insight_text) if insight_text else []
#             if insight_bullets:
#                 for raw in insight_bullets:
#                     elements.append(Paragraph(_normalize_bullet(raw), styles["Body"]))
#             else:
#                 elements.append(Paragraph("No insights generated.", styles["Body"]))
#             elements.append(PageBreak())

#             # Visualizations
#             pic_entries = charts.get(sheet, [])
#             if pic_entries:
#                 elements.append(Paragraph("Visualizations", styles["H2"]))
#                 elements.append(Spacer(1, 10))

#                 row_imgs: List[Any] = []
#                 row_caps: List[Any] = []
#                 for i, entry in enumerate(pic_entries):
#                     img = _scaled_img(entry.get("path", ""))
#                     cap = Paragraph(entry.get("description", ""), styles["Caption"])
#                     row_imgs.append(img)
#                     row_caps.append(cap)

#                     if len(row_imgs) == 2 or i == len(pic_entries) - 1:
#                         if len(row_imgs) < 2:
#                             row_imgs.append(Spacer(1, 1))
#                             row_caps.append(Spacer(1, 1))

#                         img_table = Table([row_imgs, row_caps], colWidths=[260, 260])
#                         img_table.setStyle(TableStyle([
#                             ("VALIGN", (0, 0), (-1, -1), "TOP"),
#                             ("LEFTPADDING", (0, 0), (-1, -1), 0),
#                             ("RIGHTPADDING", (0, 0), (-1, -1), 10),
#                             ("TOPPADDING", (0, 0), (-1, -1), 4),
#                             ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
#                         ]))
#                         elements.append(img_table)
#                         row_imgs = []
#                         row_caps = []
#             else:
#                 elements.append(Paragraph("Visualizations", styles["H2"]))
#                 elements.append(Paragraph("No charts generated for this sheet.", styles["Body"]))

#             elements.append(Spacer(1, 8))

#             # Business Insights
#             elements.append(Paragraph("Business Insights", styles["H2"]))
#             biz_text = business_insights.get(sheet) or ""
#             biz_bullets = _bullets_from_text(biz_text) if biz_text else []
#             if biz_bullets:
#                 for raw in biz_bullets:
#                     elements.append(Paragraph(_normalize_bullet(raw), styles["Body"]))
#             else:
#                 elements.append(Paragraph("No business insights generated.", styles["Body"]))

#             if idx < total_sheets - 1:
#                 elements.append(PageBreak())

#         doc.build(elements)
#         return str(pdf_path)





# report_agent.py
from pathlib import Path
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image,
    Table, TableStyle, PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

OUTPUTS_DIR = Path(__file__).resolve().parent.parent / "outputs"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


class ReportAgent:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._register_styles()

    def _register_styles(self):
        def _add(name, **kw):
            if name not in self.styles:
                self.styles.add(ParagraphStyle(name=name, **kw))

        _add("CoverTitle",    parent=self.styles["Title"],
             fontSize=26, textColor=colors.HexColor("#1a237e"),
             spaceAfter=10, alignment=TA_CENTER)
        _add("CoverSub",      parent=self.styles["Normal"],
             fontSize=12, textColor=colors.HexColor("#455a64"),
             spaceAfter=5, alignment=TA_CENTER)
        _add("SectionHead",   parent=self.styles["Heading1"],
             fontSize=14, textColor=colors.HexColor("#1a237e"),
             spaceBefore=12, spaceAfter=4)
        _add("SubHead",       parent=self.styles["Heading2"],
             fontSize=11, textColor=colors.HexColor("#37474f"),
             spaceBefore=8, spaceAfter=3)
        _add("BodyText2",     parent=self.styles["Normal"],
             fontSize=9, leading=14, spaceAfter=3, alignment=TA_JUSTIFY)
        _add("BulletItem",    parent=self.styles["Normal"],
             fontSize=9, leading=14, leftIndent=12, spaceAfter=3)
        _add("InsightBullet", parent=self.styles["Normal"],
             fontSize=9, leading=15, leftIndent=10, spaceAfter=4)
        _add("TableHeader",   parent=self.styles["Normal"],
             fontSize=8, textColor=colors.white,
             alignment=TA_CENTER, fontName="Helvetica-Bold")
        _add("TableCell",     parent=self.styles["Normal"],
             fontSize=8, leading=11)
        _add("Muted",         parent=self.styles["Normal"],
             fontSize=8, textColor=colors.HexColor("#78909c"),
             spaceAfter=2)
        _add("EmptySheet",    parent=self.styles["Normal"],
             fontSize=9, textColor=colors.HexColor("#999999"),
             leftIndent=12, spaceAfter=4)
        _add("ChapterLabel",  parent=self.styles["Normal"],
             fontSize=10, textColor=colors.HexColor("#1a237e"),
             fontName="Helvetica-Bold", spaceBefore=6, spaceAfter=2)

    # ── helpers ──────────────────────────────────────────────────────────
    @staticmethod
    def _safe_text(val) -> str:
        if val is None:
            return ""
        return (str(val)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace("**", "")      # strip markdown bold leaking in
                .replace("##", "")      # strip markdown headers
                .strip())

    def _para(self, text: str, style="BodyText2") -> Paragraph:
        return Paragraph(self._safe_text(text), self.styles[style])

    def _bullet(self, text: str) -> Paragraph:
        clean = self._safe_text(text).lstrip("-•* ").strip()
        return Paragraph(f"• {clean}", self.styles["BulletItem"])

    def _insight_bullet(self, text: str) -> Paragraph:
        """Bold the heading before the first colon."""
        clean = self._safe_text(text).lstrip("-•* ").strip()
        if ":" in clean:
            head, rest = clean.split(":", 1)
            return Paragraph(
                f"• <b>{head.strip()}</b>: {rest.strip()}",
                self.styles["InsightBullet"],
            )
        return Paragraph(f"• {clean}", self.styles["InsightBullet"])

    def _heading(self, text: str, level=1) -> Paragraph:
        style = "SectionHead" if level == 1 else "SubHead"
        return Paragraph(self._safe_text(text), self.styles[style])

    def _hr(self, thick=False):
        return HRFlowable(
            width="100%",
            thickness=1.0 if thick else 0.5,
            color=colors.HexColor("#1a237e" if thick else "#cfd8dc"),
            spaceAfter=6,
        )

    @staticmethod
    def _is_empty_sheet(info: dict) -> bool:
        rows, cols = info.get("shape", (0, 0))
        return rows == 0 or cols == 0

    def _sheet_badge(self, sheet: str, info: dict) -> list:
        """Small one-line sheet summary shown before each sub-section."""
        rows, cols = info.get("shape", (0, 0))
        n  = len(info.get("numeric_cols", []))
        c  = len(info.get("categorical_cols", []))
        dt = len(info.get("datetime_cols", []))
        dq = info.get("data_quality_notes", {})
        miss = dq.get("overall_missing_pct", 0)
        dups = dq.get("duplicate_rows", 0)
        label = (
            f"{rows:,} rows × {cols} cols  |  "
            f"{n} numeric, {c} categorical, {dt} datetime  |  "
            f"Missing: {miss}%  |  Duplicates: {dups}"
        )
        return [
            self._heading(f"Sheet: {sheet}", 2),
            self._para(label, "Muted"),
        ]

    # ── cover ─────────────────────────────────────────────────────────────
    def _build_cover(self, metadata: dict) -> list:
        fname       = metadata.get("file_name", "Unknown File")
        sheet_count = metadata.get("sheet_count", "?")
        file_type   = metadata.get("file_type", "")
        now         = datetime.now().strftime("%B %d, %Y  %I:%M %p")
        return [
            Spacer(1, 2 * cm),
            self._para("📊 Automated Data Insights Report", "CoverTitle"),
            self._hr(thick=True),
            Spacer(1, 0.4 * cm),
            self._para(f"File: {fname}", "CoverSub"),
            self._para(f"Type: {file_type.upper().lstrip('.')}", "CoverSub"),
            self._para(f"Sheets analysed: {sheet_count}", "CoverSub"),
            self._para(f"Generated: {now}", "CoverSub"),
            Spacer(1, 1 * cm),
            PageBreak(),
        ]

    # ── executive summary ─────────────────────────────────────────────────
    def _build_exec_summary(self, exec_summary: str) -> list:
        if not exec_summary or not exec_summary.strip():
            return []
        elems = [self._heading("Executive Summary"), self._hr()]
        for line in exec_summary.splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith(("-", "•", "*")):
                elems.append(self._insight_bullet(line))
            else:
                elems.append(self._para(line))
        elems.append(Spacer(1, 0.3 * cm))
        return elems

    # ── dataset overview ──────────────────────────────────────────────────
    def _build_overview(self, summary: dict) -> list:
        sheets = summary.get("sheets") or summary
        elems  = [self._heading("Dataset Overview"), self._hr()]

        for sheet, info in sheets.items():
            # skip empty sheets
            if self._is_empty_sheet(info):
                elems += [
                    self._heading(f"Sheet: {sheet}", 2),
                    self._para("⚠ This sheet is empty — no data to display.",
                               "EmptySheet"),
                    Spacer(1, 0.2 * cm),
                ]
                continue

            rows, cols = info.get("shape", (0, 0))
            num   = info.get("numeric_cols", [])
            cat   = info.get("categorical_cols", [])
            dt    = info.get("datetime_cols", [])
            dq    = info.get("data_quality_notes", {})
            miss  = dq.get("overall_missing_pct", 0)
            dups  = dq.get("duplicate_rows", 0)

            # top missing columns (>0%)
            miss_by_col = {
                k: v for k, v in info.get("missing_by_col", {}).items()
                if v > 0
            }
            top_miss = sorted(miss_by_col.items(),
                              key=lambda x: x[1], reverse=True)[:5]
            miss_str = (
                ", ".join(f"{c}: {v}%" for c, v in top_miss)
                if top_miss else "None"
            )

            # outlier summary
            out_cols = [
                f"{c} ({d['count']})"
                for c, d in info.get("outliers", {}).items()
                if d.get("count", 0) > 0
            ]
            out_str = ", ".join(out_cols) if out_cols else "None detected"

            elems.append(self._heading(f"Sheet: {sheet}", 2))

            data = [
                [Paragraph("Metric",  self.styles["TableHeader"]),
                 Paragraph("Value",   self.styles["TableHeader"])],
                ["Rows",              f"{rows:,}"],
                ["Columns",           str(cols)],
                ["Numeric cols",      ", ".join(num)  or "—"],
                ["Categorical cols",  ", ".join(cat)  or "—"],
                ["Datetime cols",     ", ".join(dt)   or "—"],
                ["Overall missing",   f"{miss}%"],
                ["Duplicate rows",    str(dups)],
                ["Top missing cols",  miss_str],
                ["Outlier cols",      out_str],
            ]

            t = Table(data, colWidths=[4.5 * cm, 11.5 * cm])
            t.setStyle(TableStyle([
                ("BACKGROUND",    (0, 0), (-1, 0),
                 colors.HexColor("#1a237e")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1),
                 [colors.white, colors.HexColor("#f5f5f5")]),
                ("GRID",          (0, 0), (-1, -1),
                 0.4, colors.HexColor("#cfd8dc")),
                ("FONTSIZE",      (0, 0), (-1, -1), 8),
                ("VALIGN",        (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING",   (0, 0), (-1, -1), 6),
                ("TOPPADDING",    (0, 0), (-1, -1), 4),
            ]))
            elems += [t, Spacer(1, 0.3 * cm)]

        return elems

    # ── analytical insights ───────────────────────────────────────────────
    def _build_insights(self, insights: dict, summary: dict) -> list:
        if not insights:
            return []
        sheets = summary.get("sheets") or summary
        elems  = [PageBreak(), self._heading("Analytical Insights"), self._hr()]

        for sheet, text in insights.items():
            info = sheets.get(sheet, {})

            # skip empty sheets
            if self._is_empty_sheet(info):
                continue

            elems += self._sheet_badge(sheet, info)

            lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
            if not lines:
                elems.append(self._para("No insights generated.", "Muted"))
            else:
                for line in lines:
                    if line.startswith(("-", "•", "*")):
                        elems.append(self._insight_bullet(line))
                    else:
                        # skip lines that are just theme headings repeated
                        if any(line.lower().startswith(kw) for kw in
                               ["distribution", "missing data", "correlation",
                                "category", "time trend", "outlier"]):
                            continue
                        elems.append(self._para(line))

            elems.append(Spacer(1, 0.3 * cm))

        return elems

    # ── business insights ─────────────────────────────────────────────────
    def _build_business_insights(self,
                                  business_insights: dict,
                                  summary: dict) -> list:
        if not business_insights:
            return []
        sheets = summary.get("sheets") or summary
        elems  = [PageBreak(),
                  self._heading("Business Insights"), self._hr()]

        for sheet, text in business_insights.items():
            info = sheets.get(sheet, {})

            # skip empty sheets
            if self._is_empty_sheet(info):
                continue

            elems += self._sheet_badge(sheet, info)

            lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
            if not lines:
                elems.append(self._para("No business insights generated.",
                                        "Muted"))
            else:
                for line in lines:
                    # skip redundant header lines like "Business Insights:"
                    if line.lower().rstrip(":") in (
                        "business insights", "insights", "sheet insights"
                    ):
                        continue
                    if line.startswith(("-", "•", "*")):
                        elems.append(self._insight_bullet(line))
                    elif line.lower().startswith("insight "):
                        # "Insight 1: ..." style — treat as bullet
                        elems.append(self._insight_bullet("- " + line))
                    else:
                        elems.append(self._para(line))

            elems.append(Spacer(1, 0.3 * cm))

        return elems

    # ── visualizations ────────────────────────────────────────────────────
    def _build_charts(self, charts: dict, summary: dict) -> list:
        if not charts:
            return []
        sheets = summary.get("sheets") or summary
        elems  = [PageBreak(),
                  self._heading("Visualizations"), self._hr()]

        for sheet, entries in charts.items():
            info = sheets.get(sheet, {})

            # skip empty sheets
            if self._is_empty_sheet(info):
                continue

            valid = [
                e for e in (entries or [])
                if e.get("path") and Path(e["path"]).exists()
            ]

            if not valid:
                continue

            elems.append(self._heading(f"Sheet: {sheet}", 2))

            for entry in valid:
                path = entry.get("path", "")
                desc = entry.get("description", "")
                try:
                    img = Image(path, width=14 * cm, height=9 * cm,
                                kind="proportional")
                    elems += [
                        img,
                        self._para(desc, "Muted"),
                        Spacer(1, 0.5 * cm),
                    ]
                except Exception:
                    elems.append(
                        self._para(f"[Chart unavailable: {desc}]", "Muted")
                    )

        return elems

    # ── top-level ─────────────────────────────────────────────────────────
    def generate_pdf(
        self,
        summary:           dict,
        insights:          dict,
        charts:            dict,
        executive_summary: str = "",
        business_insights: dict | None = None,
    ) -> str:
        business_insights = business_insights or {}
        metadata = summary.get("metadata", {})
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = Path(metadata.get("file_name", "report")).stem
        out  = OUTPUTS_DIR / f"report_{name}_{ts}.pdf"

        doc = SimpleDocTemplate(
            str(out), pagesize=A4,
            leftMargin=2 * cm, rightMargin=2 * cm,
            topMargin=2 * cm,  bottomMargin=2 * cm,
        )

        story = []
        story += self._build_cover(metadata)
        story += self._build_exec_summary(executive_summary)
        story += self._build_overview(summary)
        story += self._build_insights(insights, summary)
        story += self._build_business_insights(business_insights, summary)
        story += self._build_charts(charts, summary)

        doc.build(story)
        return str(out)