#!/usr/bin/env python3
"""Build a private, offline HTML archive from completed engineering-brief reports."""

import argparse
from datetime import datetime, timezone
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import posixpath
import re
from string import Template
import tempfile
import subprocess
from urllib.parse import unquote, urlsplit

import markdown

from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

from history import archive_root, completed_reports, timestamp


PACKAGE = Path(__file__).resolve().parent.parent
TEMPLATES = PACKAGE / "templates"
METADATA = re.compile(r"^<!-- engineering-brief .* -->\n?", re.MULTILINE)
H1 = re.compile(r"^# (?!#)(.+?)\s*$", re.MULTILINE)
FOLLOWUP = re.compile(
    r"(?m)^[ \t]*(?:[-*+]\s+)?"
    r":codex-followup\[(?P<label>[^\]]+)\]"
    r"\{prompt=\"(?P<prompt>(?:\\.|[^\"\\])*)\"\}[ \t]*$"
)
COPYABLE = re.compile(r"(?m)^\*\*Copyable request:\*\*[^\n]*(?:\n|$)")
COPYABLE_DETAILS = re.compile(
    r"(?is)<details\b[^>]*>\s*<summary\b[^>]*>Copyable requests for separate topic tasks</summary>.*?</details>\s*"
)


class ReportRenderError(ValueError):
    """A renderer-owned diagnostic safe to display without report contents."""


def safe_url(value):
    parsed = urlsplit(value)
    if value.startswith("#"):
        return value if len(value) > 1 else None
    if parsed.scheme in {"http", "https"} and parsed.netloc:
        return value
    return None


class Sanitizer(HTMLParser):
    """Retain only renderer-produced Markdown markup and safe external links."""

    tags = {
        "p", "br", "hr", "strong", "em", "del", "code", "pre", "blockquote",
        "ul", "ol", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table",
        "thead", "tbody", "tr", "th", "td", "a", "details", "summary",
    }
    void = {"br", "hr"}

    def __init__(self, report_links=None, source_path=None):
        super().__init__(convert_charrefs=True)
        self.report_links = report_links or {}
        self.source_path = source_path
        self.parts = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        if tag not in self.tags:
            self.parts.append(html.escape(self.get_starttag_text()))
            return
        allowed = []
        attributes = dict(attrs)
        if tag == "a":
            value = attributes.get("href", "")
            href = safe_url(value)
            parsed = urlsplit(value)
            if not href and self.source_path and parsed.scheme in {"", "file"} and not parsed.netloc and not parsed.query:
                target = (self.source_path.parent / unquote(parsed.path)).resolve()
                href = self.report_links.get(target)
                if href and parsed.fragment:
                    href += "#" + parsed.fragment
            if href:
                allowed.append(("href", href))
            if attributes.get("title"):
                allowed.append(("title", attributes["title"]))
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            identifier = attributes.get("id")
            if identifier and re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.:-]*", identifier):
                allowed.append(("id", identifier))
        elif tag == "code":
            language = attributes.get("class")
            if language and re.fullmatch(r"language-[A-Za-z0-9_+-]+", language):
                allowed.append(("class", language))
        text = "".join(f' {key}="{html.escape(value, quote=True)}"' for key, value in allowed)
        self.parts.append(f"<{tag}{text}>")
        if tag not in self.void:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in self.tags and tag not in self.void:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag not in self.stack:
            self.parts.append(html.escape(f"</{tag}>"))
            return
        while self.stack:
            opened = self.stack.pop()
            self.parts.append(f"</{opened}>")
            if opened == tag:
                break

    def handle_data(self, data):
        self.parts.append(html.escape(data))

    def handle_comment(self, data):
        pass

    def result(self):
        while self.stack:
            self.parts.append(f"</{self.stack.pop()}>")
        return "".join(self.parts)


def discussion_html(prompt):
    prompt = re.sub(r"\\([\\\"])", r"\1", prompt)
    return (
        '<div class="discussion"><details><summary>Discussion prompt</summary><pre>'
        f"{html.escape(prompt)}</pre></details>"
        '<button type="button" class="copy-prompt" aria-label="Copy prompt" title="Copy prompt" hidden>'
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
        '<rect x="8" y="8" width="12" height="12" rx="2"></rect>'
        '<path d="M16 8V5a2 2 0 0 0-2-2H5a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h3"></path>'
        '</svg></button><span class="copy-status" role="status" aria-live="polite"></span></div>'
    )


def protect_discussions(source):
    discussions = {}

    def replace(match):
        token = f"ENGINEERING_BRIEF_DISCUSSION_{len(discussions)}_END"
        discussions[token] = discussion_html(match.group("prompt"))
        return f"\n\n{token}\n\n"

    source = FOLLOWUP.sub(replace, source)
    source = COPYABLE.sub("", source)
    source = COPYABLE_DETAILS.sub("", source)
    if ":codex-followup[" in source:
        raise ReportRenderError("unrecognized native follow-up directive; preserve the source report")
    return source, discussions


def sanitize(value, report_links=None, source_path=None):
    parser = Sanitizer(report_links, source_path)
    parser.feed(value)
    parser.close()
    return parser.result()


def title_from(source, mode, report):
    match = H1.search(source)
    if match:
        return re.sub(r"[*_`\[\]]", "", match.group(1)).strip()
    return f"{mode.title()} {report['coverage_end'][:10]}"


class ReportMarkdown(Extension):
    """Enable Markdown in report note panels after fenced code has been stashed."""

    def __init__(self, discussions):
        super().__init__()
        self.discussions = discussions

    def extendMarkdown(self, md):
        discussions = self.discussions

        class Panels(Preprocessor):
            def run(self, lines):
                source, panels = protect_discussions("\n".join(lines))
                discussions.update(panels)
                return [re.sub(r"^<(details|summary)>$", r'<\1 markdown="1">', line)
                        for line in source.splitlines()]
        md.preprocessors.register(Panels(md), "report_panels", 24)


def render_markdown(source, report_links=None, source_path=None):
    discussions = {}
    renderer = markdown.Markdown(extensions=["fenced_code", "tables", "md_in_html", "sane_lists", "toc", ReportMarkdown(discussions)])
    rendered = sanitize(renderer.convert(source), report_links, source_path)
    for token, panel in discussions.items():
        rendered = rendered.replace(f"<p>{token}</p>", panel)
    if any(token in rendered for token in discussions):
        raise ReportRenderError("discussion panel could not be rendered; preserve the source report")
    return rendered, renderer.toc_tokens


def date_label(report):
    return timestamp(report["coverage_end"]).strftime("%B %-d, %Y")


def listing_date(report):
    label = date_label(report)
    if report["mode"] == "audit":
        completed = timestamp(report["completed_at"]).strftime("%-I:%M %p UTC")
        return f"{label} · completed {completed}"
    return label


def excerpt(source):
    # Reuse Markdown's fence handling so examples never become preview prose.
    parser = markdown.Markdown(extensions=["fenced_code"])
    lines = parser.preprocessors["normalize_whitespace"].run(source.splitlines())
    source = "\n".join(parser.preprocessors["fenced_code_block"].run(lines))
    cleaned = protect_discussions(source)[0]
    cleaned = METADATA.sub("", cleaned)
    paragraphs = re.split(r"\n\s*\n", cleaned)
    for paragraph in paragraphs:
        line = paragraph.strip()
        if (not line or "\x02wzxhzdk:" in line or "ENGINEERING_BRIEF_DISCUSSION_" in line or line.startswith("#") or line.startswith("**Copyable request:")
                or re.fullmatch(r"\*\*[^*]+\*\*", line)):
            continue
        line = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", line)
        line = re.sub(r"[*_`>#]", "", line)
        line = " ".join(line.split())
        if line:
            return line[:237].rstrip() + ("…" if len(line) > 237 else "")
    return "Completed report."


def relative_href(page, target):
    return posixpath.relpath(target.as_posix(), page.parent.as_posix())


def report_path(report):
    return Path(report["path"])


def output_path(report):
    return Path(report["mode"]) / (report_path(report).stem + ".html")


def navigation(page, latest):
    items = [('<a href="' + relative_href(page, Path("index.html")) + '">Archive</a>')]
    for mode in ("brief", "audit"):
        current = latest.get(mode)
        if current:
            label = "Latest brief" if mode == "brief" else "Latest source audit"
            items.append(
                f'<a href="{relative_href(page, output_path(current))}">{label}</a>'
            )
    return "".join(items)


def toc_html(tokens):
    rows = []
    def visit(entries):
        for token in entries:
            if token["level"] == 2:
                rows.append(
                    f'<li><a href="#{html.escape(token["id"], quote=True)}">'
                    f'{html.escape(token["name"])}</a></li>'
                )
            visit(token.get("children", []))

    visit(tokens)
    if not rows:
        return "<p>Read offline from this local archive.</p>"
    return "<h2>In this edition</h2><ul>" + "".join(rows) + "</ul>"


def article_sidebar(tokens, report):
    note = (
        '<p class="reading-time">Local archive · '
        f'{html.escape(report["mode"])} · {html.escape(date_label(report))}</p>'
    )
    return note + toc_html(tokens)


def pagination(page, reports, index):
    previous = reports[index - 1] if index else None
    following = reports[index + 1] if index + 1 < len(reports) else None
    left = ""
    right = ""
    if previous:
        left = (
            f'<a href="{relative_href(page, output_path(previous))}">'
            "← Earlier edition</a>"
        )
    if following:
        right = (
            f'<a href="{relative_href(page, output_path(following))}">'
            "Later edition →</a>"
        )
    if not left and not right:
        return ""
    return f'<nav class="pagination" aria-label="Edition navigation">{left}{right}</nav>'


def load_templates():
    page = TEMPLATES / "page.html"
    style = TEMPLATES / "style.css"
    if not page.is_file() or page.is_symlink() or not style.is_file() or style.is_symlink():
        raise ValueError("missing or unsafe page template/style")
    return Template(page.read_text(encoding="utf-8")), style.read_text(encoding="utf-8")


def page_html(template, styles, title, navigation_html, content, sidebar):
    return template.substitute(
        title=html.escape(title), styles=styles, navigation=navigation_html,
        content=content, sidebar=sidebar,
    )


def atomic_write(target, content):
    if target.is_symlink():
        raise ValueError(f"preserve symlinked output: {target}")
    target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    descriptor, temporary = tempfile.mkstemp(prefix=".render-", dir=target.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as output:
            output.write(content)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, target)
    finally:
        Path(temporary).unlink(missing_ok=True)


def output_directory(archive):
    site = archive / "site"
    if site.is_symlink() or (site.exists() and not site.is_dir()):
        raise ValueError("preserve unsafe site output path")
    for mode in ("brief", "audit"):
        folder = site / mode
        if folder.is_symlink() or (folder.exists() and not folder.is_dir()):
            raise ValueError(f"preserve unsafe {mode} site directory")
    return site


def build(archive):
    now = datetime.now(timezone.utc)
    reports = {mode: completed_reports(archive, mode, now) for mode in ("brief", "audit")}
    if not reports["brief"] and not reports["audit"]:
        raise ValueError("no completed reports available for rendering")
    template, styles = load_templates()
    rendered = []
    for mode, rows in reports.items():
        for index, report in enumerate(rows):
            source = report_path(report).read_text(encoding="utf-8")
            source = METADATA.sub("", source, count=1)
            title = title_from(source, mode, report)
            page = output_path(report)
            report_links = {
                report_path(item).resolve(): relative_href(page, output_path(item))
                for values in reports.values() for item in values
            }
            try:
                body, tokens = render_markdown(
                    source if H1.search(source) else f"# {title}\n\n{source}",
                    report_links, report_path(report),
                )
            except ValueError as error:
                # Name the report relative to the archive, never by its absolute path.
                reason = (str(error) if isinstance(error, ReportRenderError)
                          else "invalid report markup; preserve the source report")
                raise ValueError(f"{mode}/{report_path(report).name}: {reason}") from error
            content = (
                f'<p class="metadata">{html.escape(date_label(report))} · '
                f'{html.escape(mode)}</p>{body}{pagination(page, rows, index)}'
            )
            rendered.append((page, page_html(
                template, styles, title, navigation(page, {kind: values[-1] if values else None for kind, values in reports.items()}),
                content, article_sidebar(tokens, report),
            )))
    index_entries = {"brief": [], "audit": []}
    for mode in ("brief", "audit"):
        for report in reversed(reports[mode]):
            source = METADATA.sub("", report_path(report).read_text(encoding="utf-8"), count=1)
            title = title_from(source, mode, report)
            target = output_path(report)
            index_entries[mode].append(
                '<article class="archive-item"><p class="metadata">'
                f'{html.escape(listing_date(report))} · {html.escape(mode)}</p><h2>'
                f'<a href="{target.as_posix()}">{html.escape(title)}</a></h2><p>'
                f'{html.escape(excerpt(source))}</p></article>'
            )
    index_page = Path("index.html")
    index_content = (
        "<h1>Engineering Brief Archive</h1><section><h2>Briefs</h2>"
        + ("".join(index_entries["brief"]) or "<p>No completed briefs yet.</p>")
        + "</section><section><h2>Source audits</h2>"
        + ("".join(index_entries["audit"]) or "<p>No completed source audits yet.</p>")
        + "</section>"
    )
    index_sidebar = (
        "<h2>About</h2><p>Private local reading copies of completed briefs and "
        "source audits.</p>"
    )
    rendered.append((index_page, page_html(
        template, styles, "Engineering Brief Archive", navigation(index_page, {kind: values[-1] if values else None for kind, values in reports.items()}),
        index_content, index_sidebar,
    )))
    site = output_directory(archive)
    site.mkdir(mode=0o700, exist_ok=True)
    for relative, content in rendered:
        atomic_write(site / relative, content)
    latest = {
        mode: str(site / output_path(rows[-1])) if rows else None
        for mode, rows in reports.items()
    }
    return {"index": str(site / "index.html"), "latest": latest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    try:
        result = build(archive_root())
    except (OSError, ValueError, KeyError, TypeError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"render: {error}\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
