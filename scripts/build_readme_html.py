"""Turns README.md into README.html (the Help page).

    python scripts/build_readme_html.py

Only supports the bits of Markdown the README uses. No code blocks.
"""

import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "README.md"
OUT = ROOT / "README.html"

STOP_AT = re.compile(r"^##\s+For developers\s*$", re.I)
BLOCK_START = re.compile(r"^(#{1,6}\s|>|\||---\s*$|-\s|\d+\.\s)")
# code, image, link, bold, italic
INLINE = re.compile(
    r"`([^`]+)`|!\[([^\]]*)\]\(([^)\s]+)\)|\[([^\]]+)\]\(([^)\s]+)\)"
    r"|\*\*(.+?)\*\*|\*((?:\*\*.+?\*\*|[^*])+)\*"
)

esc = html.escape


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text.lower().strip())
    return re.sub(r"\s", "-", text).replace("_", "")


def inline(text):
    out = []
    while text:
        m = INLINE.search(text)
        if not m:
            out.append(esc(text))
            break
        out.append(esc(text[: m.start()]))
        code, alt, src, label, href, bold, italic = m.groups()
        if code is not None:
            out.append(f"<code>{esc(code)}</code>")
        elif src is not None:
            out.append(image(alt, src))
        elif href is not None:
            out.append(link(label, href))
        elif bold is not None:
            out.append(f"<strong>{inline(bold)}</strong>")
        else:
            out.append(f"<em>{inline(italic)}</em>")
        text = text[m.end():]
    return "".join(out)


def link(label, href):
    if href.startswith("#"):
        return f'<a href="{esc(href)}">{inline(label)}</a>'
    if re.match(r"^https?://", href, re.I):
        return f'<a href="{esc(href)}" target="_blank" rel="noopener noreferrer">{inline(label)}</a>'
    return inline(label)  # anything else, just show the text


def image(alt, src):
    # local images inside the extension only
    if re.match(r"^[a-z][a-z0-9+.-]*:", src, re.I) or src.startswith(("/", "\\")) or ".." in src:
        return ""
    return f'<img src="{esc(src)}" alt="{esc(alt)}" loading="lazy">'


def split_row(row):
    return [c.strip() for c in row.strip().strip("|").split("|")]


def render(md):
    lines = md.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    out, i = [], 0
    seen = {}  # duplicate headings get -1, -2 like on GitHub
    while i < len(lines):
        line = lines[i]
        if STOP_AT.match(line):
            break
        if not line.strip():
            i += 1
        elif re.match(r"^---\s*$", line):
            out.append("<hr>")
            i += 1
        elif m := re.match(r"^(#{1,6})\s+(.*)$", line):
            n = len(m[1])
            slug = slugify(m[2])
            count = seen.get(slug, 0)
            seen[slug] = count + 1
            if count:
                slug = f"{slug}-{count}"
            out.append(f'<h{n} id="{esc(slug)}">{inline(m[2])}</h{n}>')
            i += 1
        elif line.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.append(f"<blockquote><p>{inline(' '.join(buf).strip())}</p></blockquote>")
        elif line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{3,}", lines[i + 1]):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(lines[i])
                i += 1
            head = "".join(f"<th>{inline(c)}</th>" for c in split_row(rows[0]))
            body = "".join(
                "<tr>" + "".join(f"<td>{inline(c)}</td>" for c in split_row(r)) + "</tr>" for r in rows[2:]
            )
            out.append(f'<div class="table"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
        elif m := re.match(r"^(-|\d+\.)\s+", line):
            ordered = m[1] != "-"
            item = re.compile(r"^\d+\.\s+(.*)$" if ordered else r"^-\s+(.*)$")
            items = []
            while i < len(lines) and (m := item.match(lines[i])):
                items.append(f"<li>{inline(m[1])}</li>")
                i += 1
            tag = "ol" if ordered else "ul"
            out.append(f"<{tag}>{''.join(items)}</{tag}>")
        else:
            buf = [line.strip()]
            i += 1
            while (
                i < len(lines)
                and lines[i].strip()
                and not BLOCK_START.match(lines[i])
                and not STOP_AT.match(lines[i])
            ):
                buf.append(lines[i].strip())
                i += 1
            out.append(f"<p>{inline(' '.join(buf))}</p>")
    while out and out[-1] == "<hr>":
        out.pop()
    return "\n".join(out)


STYLE = """
:root {
  --bg: #ffffff; --fg: #1f2328; --muted: #59636e; --line: #d1d9e0;
  --soft: #f6f8fa; --link: #0b57d0; --brand: #c8003c;
  color-scheme: light dark;
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1f1f1f; --fg: #e3e3e3; --muted: #a8a8a8; --line: #3c3c3c;
    --soft: #2a2a2a; --link: #a8c7fa; --brand: #ff6b8f;
  }
}
body { margin: 0; background: var(--bg); color: var(--fg); font: 16px/1.6 system-ui, "Segoe UI", sans-serif; }
main { max-width: 760px; margin: 0 auto; padding: 32px 16px 64px; }
.brand { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.brand img { width: 48px; height: 48px; border: 0; border-radius: 0; }
h1, h2, h3 { line-height: 1.25; margin: 1.6em 0 0.5em; }
h1 { font-size: 2em; margin: 0; color: var(--brand); }
h2 { font-size: 1.4em; }
h3 { font-size: 1.1em; }
p, ul, ol, blockquote, .table { margin: 0 0 1em; }
li + li { margin-top: 0.25em; }
a { color: var(--link); }
code { font: 0.9em ui-monospace, Consolas, monospace; background: var(--soft); padding: 0.1em 0.35em; border-radius: 4px; }
hr { border: 0; border-top: 1px solid var(--line); margin: 2em 0; }
blockquote { padding: 0.6em 1em; border-left: 4px solid var(--brand); background: var(--soft); border-radius: 0 6px 6px 0; }
blockquote p { margin: 0; }
img { display: block; max-width: 100%; height: auto; border: 1px solid var(--line); border-radius: 8px; }
.table { overflow-x: auto; }
table { border-collapse: collapse; width: 100%; }
th, td { text-align: left; vertical-align: top; padding: 0.5em 0.75em; border: 1px solid var(--line); }
th { background: var(--soft); }
""".strip()


def main():
    body = render(SRC.read_text(encoding="utf-8"))
    # logo next to the title
    body = re.sub(
        r"^<h1 ([^>]*)>(.*?)</h1>",
        r'<div class="brand"><img src="icons/icon-128.png" alt=""><h1 \1>\2</h1></div>',
        body,
        count=1,
    )
    page = f"""<!doctype html>
<!-- Generated from README.md by scripts/build_readme_html.py. Don't edit. -->
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Air Business XSLT Polyfill – Help</title>
<link rel="icon" href="icons/icon-32.png">
<style>
{STYLE}
</style>
</head>
<body>
<main>
{body}
</main>
</body>
</html>
"""
    OUT.write_text(page, encoding="utf-8", newline="\n")
    print(f"Wrote {OUT.name}")


if __name__ == "__main__":
    main()
