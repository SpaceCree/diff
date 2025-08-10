import re
import html
from typing import Tuple, List

try:
    from docx import Document  # type: ignore
except Exception:  # pragma: no cover
    Document = None  # lazy fallback if not installed


def load_text_from_file(file_path: str) -> str:
    """Load text content from .txt or .docx file as a single string."""
    lower = file_path.lower()
    if lower.endswith(".txt"):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    if lower.endswith(".docx"):
        if Document is None:
            raise RuntimeError("python-docx is required to read .docx files. Install via pip install python-docx")
        doc = Document(file_path)
        return "\n".join(p.text for p in doc.paragraphs)
    raise ValueError("Unsupported file type. Please use .txt or .docx")


def tokenize_text(text: str) -> List[str]:
    """Split text into tokens preserving words, whitespace, and punctuation."""
    return re.findall(r"\w+|\s+|[^\w\s]", text, flags=re.UNICODE)


def _wrap_html(token: str, css_class: str) -> str:
    safe = html.escape(token)
    return f'<span class="{css_class}">{safe}</span>'


def build_dual_highlighted_html(text_a: str, text_b: str) -> Tuple[str, str]:
    """Return two HTML strings: A with deletions highlighted, B with insertions highlighted.

    Uses token-level ndiff to mark differences in red while preserving whitespace.
    """
    import difflib

    tokens_a = tokenize_text(text_a)
    tokens_b = tokenize_text(text_b)

    diff = difflib.ndiff(tokens_a, tokens_b)

    html_a_parts: List[str] = []
    html_b_parts: List[str] = []

    for op in diff:
        tag = op[:2]
        token = op[2:]
        if tag == "  ":
            safe = html.escape(token)
            html_a_parts.append(safe)
            html_b_parts.append(safe)
        elif tag == "- ":
            html_a_parts.append(_wrap_html(token, "diff diff-del"))
            # In B we omit deletions
        elif tag == "+ ":
            html_b_parts.append(_wrap_html(token, "diff diff-ins"))
            # In A we omit insertions
        # ignore '? ' helper lines

    return "".join(html_a_parts), "".join(html_b_parts)


def generate_html_report(name_a: str, name_b: str, html_a: str, html_b: str) -> str:
    """Wrap two highlighted HTML blocks into a full HTML report page."""
    return f"""
<!DOCTYPE html>
<html lang=\"ru\">
<head>
<meta charset=\"utf-8\" />
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
<title>Сравнение документов</title>
<style>
  :root {{
    --border: #e5e7eb;
    --bg: #ffffff;
    --text: #111827;
    --muted: #6b7280;
    --red: #b91c1c;
    --pink: #fee2e2;
  }}
  body {{
    margin: 0; padding: 24px; background: var(--bg); color: var(--text);
    font: 14px/1.6 -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Noto Sans', Ubuntu, Cantarell, 'Helvetica Neue', Arial, 'Apple Color Emoji', 'Segoe UI Emoji';
  }}
  h1 {{ font-size: 20px; margin: 0 0 16px; }}
  .meta {{ color: var(--muted); margin-bottom: 16px; }}
  .grid {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px;
  }}
  .panel {{
    border: 1px solid var(--border); border-radius: 8px; overflow: hidden; background: white;
    display: flex; flex-direction: column; min-height: 60vh;
  }}
  .panel-header {{
    font-weight: 600; padding: 10px 12px; border-bottom: 1px solid var(--border); background: #f9fafb;
  }}
  .panel-body {{
    padding: 12px; white-space: pre-wrap; word-break: break-word; overflow: auto;
  }}
  .diff {{ color: var(--red); background: var(--pink); }}
  .diff-del {{ text-decoration: line-through; }}
  .legend {{ margin-top: 16px; font-size: 13px; color: var(--muted); }}
  @media (max-width: 900px) {{ .grid {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
  <h1>Отчет сравнения</h1>
  <div class=\"meta\">Различия подсвечены красным цветом.</div>
  <div class=\"grid\">
    <section class=\"panel\">
      <div class=\"panel-header\">{html.escape(name_a)}</div>
      <div class=\"panel-body\">{html_a}</div>
    </section>
    <section class=\"panel\">
      <div class=\"panel-header\">{html.escape(name_b)}</div>
      <div class=\"panel-body\">{html_b}</div>
    </section>
  </div>
  <div class=\"legend\">
    Удаления выделены как <span class=\"diff diff-del\">красный зачеркнутый</span>,
    добавления — как <span class=\"diff diff-ins\">красный фон</span>.
  </div>
</body>
</html>
"""
