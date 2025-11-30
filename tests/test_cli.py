from pathlib import Path

import pytest

pytest.importorskip("markdown_it")
pytest.importorskip("weasyprint")

from markdown_it import MarkdownIt

from recipes_pdfs.cli import convert_markdown_to_pdf, ensure_heading, walk_vault


def test_ensure_heading_injects_title_when_missing():
    content = "This is a note without a heading."
    result = ensure_heading(content, "My Note")

    assert result.startswith("# My Note\n\n")


def test_ensure_heading_preserves_existing_h1():
    content = "# Existing Title\n\nBody text."
    result = ensure_heading(content, "My Note")

    assert result == content


def test_walk_vault_ignores_special_directories(tmp_path: Path):
    vault = tmp_path / "vault"
    (vault / "_pdf_build").mkdir(parents=True)
    (vault / ".obsidian").mkdir(parents=True)
    nested = vault / "notes"
    nested.mkdir(parents=True)

    note = nested / "note.md"
    note.write_text("content", encoding="utf-8")
    (nested / "ignore.txt").write_text("skip", encoding="utf-8")

    results = list(walk_vault(vault))

    assert results == [(note, Path("notes/note.pdf"))]


def test_convert_markdown_to_pdf_writes_file(tmp_path: Path):
    markdown_file = tmp_path / "note.md"
    markdown_file.write_text("Content without heading", encoding="utf-8")
    output_file = tmp_path / "output.pdf"

    parser = MarkdownIt("commonmark")
    convert_markdown_to_pdf(markdown_file, output_file, parser)

    assert output_file.exists()
    assert output_file.stat().st_size > 0
