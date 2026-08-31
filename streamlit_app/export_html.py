from __future__ import annotations

from pathlib import Path

from cases import CASES, REVIEW_WINDOW
from engine import evaluate_case
from ui import CSS, case_html, header_html, queue_html, spec_html

STANDALONE_CSS = """
html, body {
  background: var(--bg);
  color: var(--ink);
  margin: 0;
  font-family: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
}
.shell { max-width: 72rem; margin: 0 auto; padding: 0 1.25rem 3rem; }
.page { display: none; }
.page.on { display: block; }
.notice {
  background: var(--ok-soft); color: var(--ok);
  text-align: center; font-size: 0.8rem; padding: 0.55rem 1rem;
  letter-spacing: 0.04em;
}
"""

NAV = """
<script>
function showPage() {
  var hash = (location.hash || "#queue").slice(1);
  var id = "page-queue";
  if (hash === "spec") id = "page-spec";
  else if (hash.indexOf("case/") === 0) id = "page-case-" + hash.slice(5);
  document.querySelectorAll(".page").forEach(function (p) { p.classList.remove("on"); });
  var el = document.getElementById(id) || document.getElementById("page-queue");
  el.classList.add("on");
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", showPage);
window.addEventListener("DOMContentLoaded", showPage);
showPage();
</script>
"""


def _rewrite(html: str) -> str:
    return (
        html.replace('href="?page=queue"', 'href="#queue"')
        .replace('href="?page=spec"', 'href="#spec"')
        .replace('href="?page=case&id=', 'href="#case/')
    )


def build_html() -> str:
    pages = [
        f'<div class="page on" id="page-queue">{header_html("queue", REVIEW_WINDOW["label"])}{queue_html(CASES, {})}</div>',
        f'<div class="page" id="page-spec">{header_html("spec", REVIEW_WINDOW["label"])}{spec_html(CASES)}</div>',
    ]
    for c in CASES:
        result = evaluate_case(c)
        pages.append(
            f'<div class="page" id="page-case-{c["id"]}">{header_html("case", REVIEW_WINDOW["label"])}{case_html(c, result, False)}</div>'
        )
    body = _rewrite("\n".join(pages))
    disclaimer = REVIEW_WINDOW.get(
        "disclaimer",
        "All cases are synthetic. Not real patients or PHI.",
    )
    css = CSS.replace("<style>", "<style>\n" + STANDALONE_CSS)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Aegis — synthetic BSI adjudication</title>
{css}
</head>
<body>
<p class="notice">{disclaimer}</p>
<div class="shell">
{body}
</div>
{NAV}
</body>
</html>
"""


def write_html(path: Path | None = None) -> Path:
    dest = path or (Path(__file__).resolve().parent.parent / "Aegis-synthetic-workbench.html")
    dest.write_text(build_html(), encoding="utf-8")
    return dest


if __name__ == "__main__":
    out = write_html()
    print(out, out.stat().st_size)
