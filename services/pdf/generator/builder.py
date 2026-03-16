"""BRD HTML assembly from sections."""

from __future__ import annotations

import html
import os
from dataclasses import dataclass


@dataclass
class BrdContent:
    """Holds all BRD content needed for PDF generation."""

    section_title: str
    section_short_description: str
    section_current_workflow: str
    section_affected_department: str
    section_core_capabilities: str
    section_success_criteria: str
    project_title: str
    generated_date: str


_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")

_SECTION_LABELS = [
    ("section_title", "1. Title"),
    ("section_short_description", "2. Short Description"),
    ("section_current_workflow", "3. Current Workflow & Pain Points"),
    ("section_affected_department", "4. Affected Department"),
    ("section_core_capabilities", "5. Core Capabilities"),
    ("section_success_criteria", "6. Success Criteria"),
]


def _load_css() -> str:
    css_path = os.path.join(_TEMPLATE_DIR, "brd_styles.css")
    with open(css_path) as f:
        return f.read()


def _render_section(label: str, content: str) -> str:
    escaped = html.escape(content or "")
    paragraphs = "\n".join(
        f"<p>{line}</p>" if line.strip() else "<p>&nbsp;</p>"
        for line in escaped.split("\n")
    )
    return f"""<section class="brd-section">
  <h2>{html.escape(label)}</h2>
  <div class="section-content">{paragraphs}</div>
</section>"""


def build_html(content: BrdContent) -> str:
    """Build a complete HTML document from BRD content for PDF rendering."""
    css = _load_css()

    sections_html = "\n".join(
        _render_section(label, getattr(content, field))
        for field, label in _SECTION_LABELS
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>BRD — {html.escape(content.project_title)}</title>
  <style>{css}</style>
</head>
<body>
  <header class="brd-header">
    <div class="brand">
      <span class="brand-name">Commerz Real</span>
      <span class="brand-sub">Business Requirements Document</span>
    </div>
    <div class="header-meta">
      <span class="generated-date">Generated: {html.escape(content.generated_date)}</span>
    </div>
  </header>

  <main>
    <h1 class="project-title">{html.escape(content.project_title)}</h1>
    {sections_html}
  </main>

  <footer class="brd-footer">
    <span class="footer-brand">Commerz Real — ZiqReq</span>
    <span class="page-number"></span>
  </footer>
</body>
</html>"""
