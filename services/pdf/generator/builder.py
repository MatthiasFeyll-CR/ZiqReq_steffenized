"""Requirements document HTML assembly — type-specific templates."""

from __future__ import annotations

import html
import json
import os
from dataclasses import dataclass, field


@dataclass
class RequirementsDocumentContent:
    """Holds all content needed for PDF generation."""

    project_type: str  # "software" or "non_software"
    title: str
    short_description: str
    structure: list[dict] = field(default_factory=list)
    generated_date: str = ""


_TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


def _load_css() -> str:
    css_path = os.path.join(_TEMPLATE_DIR, "requirements_styles.css")
    with open(css_path) as f:
        return f.read()


def _render_bullet_list(text) -> str:
    """Render a text block or list as an HTML bullet list."""
    if not text:
        return ""
    if isinstance(text, list):
        lines = [str(item).strip() for item in text if str(item).strip()]
    else:
        lines = [line.strip().lstrip("- ").lstrip("* ") for line in str(text).strip().split("\n") if line.strip()]
    if not lines:
        return ""
    items = "\n".join(f"<li>{html.escape(line)}</li>" for line in lines)
    return f"<ul>{items}</ul>"


def _render_epic(epic: dict) -> str:
    """Render an epic section with user stories table."""
    title = html.escape(epic.get("title", ""))
    description = html.escape(epic.get("description", ""))
    desc_html = "\n".join(
        f"<p>{line}</p>" if line.strip() else "<p>&nbsp;</p>"
        for line in description.split("\n")
    )

    children = epic.get("children", [])
    rows = ""
    for story in children:
        sid = html.escape(story.get("id", "")[:8])
        stitle = html.escape(story.get("title", ""))
        sdesc = html.escape(story.get("description", ""))
        ac = _render_bullet_list(story.get("acceptance_criteria", ""))
        priority = story.get("priority", "Medium")
        priority_class = priority.lower() if priority else "medium"
        rows += f"""      <tr>
        <td class="col-id">{sid}</td>
        <td>{stitle}</td>
        <td>{sdesc}</td>
        <td>{ac}</td>
        <td><span class="priority-badge priority-{html.escape(priority_class)}">{html.escape(priority)}</span></td>
      </tr>\n"""

    table = ""
    if rows:
        table = f"""  <table class="requirements-table user-stories-table">
    <thead>
      <tr><th class="col-id">ID</th><th>Title</th><th>Description</th><th>Acceptance Criteria</th><th>Priority</th></tr>
    </thead>
    <tbody>
{rows}    </tbody>
  </table>"""

    return f"""<section class="epic-section">
  <h2>Epic: {title}</h2>
  <div class="section-description">{desc_html}</div>
{table}
</section>"""


def _render_milestone(milestone: dict) -> str:
    """Render a milestone section with work packages table."""
    title = html.escape(milestone.get("title", ""))
    description = html.escape(milestone.get("description", ""))
    desc_html = "\n".join(
        f"<p>{line}</p>" if line.strip() else "<p>&nbsp;</p>"
        for line in description.split("\n")
    )

    children = milestone.get("children", [])
    rows = ""
    for pkg in children:
        pid = html.escape(pkg.get("id", "")[:8])
        ptitle = html.escape(pkg.get("title", ""))
        pdesc = html.escape(pkg.get("description", ""))
        deliverables = _render_bullet_list(pkg.get("deliverables", ""))
        dependencies = _render_bullet_list(pkg.get("dependencies", ""))
        rows += f"""      <tr>
        <td class="col-id">{pid}</td>
        <td>{ptitle}</td>
        <td>{pdesc}</td>
        <td>{deliverables}</td>
        <td>{dependencies}</td>
      </tr>\n"""

    table = ""
    if rows:
        table = f"""  <table class="requirements-table work-packages-table">
    <thead>
      <tr><th class="col-id">ID</th><th>Title</th><th>Description</th><th>Deliverables</th><th>Dependencies</th></tr>
    </thead>
    <tbody>
{rows}    </tbody>
  </table>"""

    return f"""<section class="milestone-section">
  <h2>Milestone: {title}</h2>
  <div class="section-description">{desc_html}</div>
{table}
</section>"""


def _render_attachments_section(attachment_names: list[str]) -> str:
    """Render an Attachments appendix listing attached file names."""
    if not attachment_names:
        return ""
    items = "\n".join(f"<li>{html.escape(name)}</li>" for name in attachment_names)
    return f"""<section class="attachments-section">
  <h2>Appendix: Attachments</h2>
  <p>The following files are appended to this document:</p>
  <ol>{items}</ol>
</section>"""


def build_html(
    content: RequirementsDocumentContent,
    attachment_names: list[str] | None = None,
) -> str:
    """Build a complete HTML document from requirements content for PDF rendering."""
    css = _load_css()

    if content.project_type == "software":
        sections_html = "\n".join(_render_epic(epic) for epic in content.structure)
        doc_type = "Software Requirements Document"
    else:
        sections_html = "\n".join(_render_milestone(ms) for ms in content.structure)
        doc_type = "Project Requirements Document"

    attachments_html = _render_attachments_section(attachment_names or [])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{html.escape(doc_type)} — {html.escape(content.title)}</title>
  <style>{css}</style>
</head>
<body>
  <header class="requirements-header">
    <div class="brand">
      <span class="brand-name">Commerz Real</span>
      <span class="brand-sub">{html.escape(doc_type)}</span>
    </div>
    <div class="header-meta">
      <span class="generated-date">Generated: {html.escape(content.generated_date)}</span>
    </div>
  </header>

  <main>
    <h1 class="project-title">{html.escape(content.title)}</h1>
    <p class="short-description">{html.escape(content.short_description)}</p>
    {sections_html}
    {attachments_html}
  </main>

  <footer class="requirements-footer">
    <span class="footer-brand">Commerz Real — ZiqReq</span>
    <span class="page-number"></span>
  </footer>
</body>
</html>"""


def parse_structure_json(structure_json: str) -> list[dict]:
    """Parse a JSON string into a structure list, returning empty list on failure."""
    if not structure_json:
        return []
    try:
        parsed = json.loads(structure_json)
        return parsed if isinstance(parsed, list) else []
    except (json.JSONDecodeError, TypeError):
        return []
