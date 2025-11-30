import os
from pathlib import Path
from typing import Iterable, Tuple

import click
from markdown_it import MarkdownIt
from markdown_it.extensions.footnote import footnote_plugin
from markdown_it.extensions.tasklists import tasklists_plugin
from weasyprint import CSS, HTML


DEFAULT_CSS = """
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    font-size: 12pt;
    line-height: 1.5;
    color: #1f2933;
    margin: 2rem;
}

h1, h2, h3, h4, h5, h6 {
    margin: 1.4rem 0 0.6rem;
    line-height: 1.25;
}

p {
    margin: 0.6rem 0;
}

ul, ol {
    margin: 0.6rem 0 0.6rem 1.25rem;
}

code, pre {
    font-family: "SFMono-Regular", Menlo, Consolas, monospace;
    background: #f3f4f6;
}

pre {
    padding: 0.75rem;
    overflow: auto;
    border-radius: 4px;
}

table {
    border-collapse: collapse;
    width: 100%;
    margin: 0.75rem 0;
}

table th, table td {
    border: 1px solid #e5e7eb;
    padding: 0.5rem;
    text-align: left;
}

blockquote {
    border-left: 4px solid #d1d5db;
    padding-left: 0.75rem;
    color: #4b5563;
    margin-left: 0;
}

.task-list-item input[type="checkbox"] {
    margin-right: 0.5rem;
}
"""


def ensure_heading(markdown_text: str, title: str) -> str:
    lines = markdown_text.lstrip("\ufeff").splitlines()
    for line in lines:
        if not line.strip():
            continue
        if line.startswith("# "):
            return markdown_text
        break
    return f"# {title}\n\n" + markdown_text


def walk_vault(vault_dir: Path) -> Iterable[Tuple[Path, Path]]:
    for root, dirnames, filenames in os.walk(vault_dir):
        dirnames[:] = [d for d in dirnames if d not in {".obsidian", "_pdf_build"}]
        for filename in filenames:
            if not filename.lower().endswith(".md"):
                continue
            input_path = Path(root, filename)
            relative = input_path.relative_to(vault_dir)
            yield input_path, relative.with_suffix(".pdf")


def convert_markdown_to_pdf(markdown_path: Path, output_path: Path, md_parser: MarkdownIt) -> None:
    markdown_text = markdown_path.read_text(encoding="utf-8")
    title = markdown_path.stem
    prepared_markdown = ensure_heading(markdown_text, title)
    html_content = md_parser.render(prepared_markdown)
    wrapped_html = f"<html><head></head><body>{html_content}</body></html>"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=wrapped_html, base_url=str(markdown_path.parent)).write_pdf(
        str(output_path), stylesheets=[CSS(string=DEFAULT_CSS)]
    )


@click.command()
@click.option(
    "vault_dir",
    "--vault-dir",
    type=click.Path(file_okay=False, dir_okay=True, exists=True, path_type=Path),
    required=True,
    help="Path to the Obsidian vault root",
)
@click.option(
    "output_dir",
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, exists=False, path_type=Path),
    default=None,
    help="Directory to write PDFs (defaults to <vault_dir>/_pdf_build)",
)
@click.option("verbose", "--verbose", is_flag=True, help="Print progress details")
def main(vault_dir: Path, output_dir: Path | None, verbose: bool) -> None:
    destination_root = output_dir or vault_dir / "_pdf_build"
    md_parser = MarkdownIt("commonmark", {"typographer": True}).use(tasklists_plugin).use(footnote_plugin)

    if verbose:
        click.echo(f"Scanning vault at {vault_dir}")
        click.echo(f"Writing PDFs to {destination_root}")

    for input_path, relative_pdf_path in walk_vault(vault_dir):
        output_path = destination_root / relative_pdf_path
        convert_markdown_to_pdf(input_path, output_path, md_parser)
        if verbose:
            click.echo(f"Exported {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
