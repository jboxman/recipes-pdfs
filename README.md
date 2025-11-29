# Obsidian markdown to PDF exporter

Export an entire [Obsidian](https://obsidian.md) vault of Markdown notes to PDF, preserving the folder structure and using each note’s filename as the top-level heading.

This project is intended as a starting point for implementing the exporter using Codex / AI-assisted coding.

---

## Overview

This tool will:

- Walk an Obsidian vault directory recursively
    
- Find all `*.md` files
    
- Convert each Markdown file to a PDF
    
- Preserve the vault’s directory structure under a dedicated build/output folder
    
- Use the Markdown file’s **filename as the H1 heading** when an explicit H1 is not present
    
- Generate PDFs optimized for **on-screen viewing**, not for print
    

The result is a tree of PDFs that mirrors the vault, suitable for syncing to cloud storage (for example, Google Drive) for convenient read-only access on other devices.

---

## Requirements and constraints

- **Input**
    
    - Root directory is an existing Obsidian vault
        
    - Notes are plain Markdown (`*.md`) with Obsidian-style syntax
        
- **Output**
    
    - PDFs generated into a `_pdf_build/` directory **inside** the vault
        
    - Directory structure under `_pdf_build/` mirrors the vault’s directory structure
        
    - File `some/folder/Note.md` becomes `_pdf_build/some/folder/Note.pdf`
        
- **Rendering**
    
    - Preserve Markdown structure and formatting:
        
        - Headings (`#`, `##`, …)
            
        - Lists (ordered, unordered)
            
        - Blockquotes
            
        - Code blocks and inline code
            
        - Tables
            
        - Task lists (`- [ ]` / `- [x]`)
            
        - Emphasis (bold, italics, strikethrough)
            
    - Images should be rendered and scaled to fit the page width
        
    - PDFs are intended for **electronic viewing** (laptop, tablet, phone), not print:
        
        - Reasonable default page size (for example, A4 or US Letter)
            
        - Focus on readability and clean layout
            
- **Obsidian specifics**
    
    - Obsidian treats the **note title (filename)** as the conceptual H1
        
    - Many notes do **not** start with `# Title` in the body
        
    - For this exporter:
        
        - If the content does not start with a level-1 heading, **inject an H1 using the filename** (without extension)
            
        - If the note already starts with an H1, do **not** add an extra title
            
- **Performance**
    
    - Should be able to process medium-sized vaults (hundreds to a few thousand notes)
        
    - A simple progress log on the command line is sufficient
        

---

## Example behavior

Given a vault:

`MyVault/   .obsidian/   000 Inbox.md   Projects/     Trading Journal.md     Ideas.md   References/     Wyckoff/       Accumulation.md`

The tool will create:

`MyVault/   _pdf_build/     000 Inbox.pdf     Projects/       Trading Journal.pdf       Ideas.pdf     References/       Wyckoff/         Accumulation.pdf`

Notes:

- The `.obsidian/` configuration folder is ignored
    
- Any existing `_pdf_build/` folder is used as the output root and not scanned for input Markdown
    

---

## Heading handling (filename as H1)

### When to inject a title

- If the note starts with a level-1 heading (`# Something`), **do not** inject a heading
    
- Otherwise, inject an H1 at the top of the document using the filename (without extension)
    

Example:

- Filename: `Trading Journal.md`
    
- Original content:
    
    `## Week of 2025-01-13  - [ ] Review trades - [x] Update risk plan`
    
- Transformed content for PDF rendering:
    
    `# Trading Journal  ## Week of 2025-01-13  - [ ] Review trades - [x] Update risk plan`
    

This transformation should happen _logically_ in the exporter (it does not change the original file on disk).

---

## Ignoring files and folders

The exporter should skip:

- The `_pdf_build/` folder itself (to avoid reprocessing generated PDFs)
    
- Obsidian internal configuration folders (such as `.obsidian/`)
    
- Hidden files and folders that start with `.`, unless explicitly requested
    
- Non-Markdown files (`*.md` is the only input)
    

A simple rule set:

- Only process files that:
    
    - Have a `.md` extension
        
    - Are not inside `_pdf_build/`
        
    - Are not inside `.obsidian/` (or other excluded technical folders)
        

---

## Expected command line interface

A minimal CLI might look like:

`md2pdf-export \   --vault-dir /path/to/MyVault \   --output-dir _pdf_build \   [--page-size A4|Letter] \   [--theme default] \   [--force] \   [--verbose]`

Suggested behavior:

- `--vault-dir`
    
    - Required
        
    - Path to the Obsidian vault root
        
- `--output-dir`
    
    - Optional
        
    - Default: `_pdf_build` (relative to the vault root)
        
- `--page-size`
    
    - Optional
        
    - Default can be `A4` or `Letter`
        
- `--theme`
    
    - Optional
        
    - Select between one or more CSS themes for the PDF styling
        
- `--force`
    
    - Optional
        
    - If present, regenerate all PDFs even if they already exist
        
- `--verbose`
    
    - Optional
        
    - Print each file as it is processed, plus basic statistics at the end
        

Exit codes:

- `0` on success
    
- Non-zero on error (for example, invalid path, permission issues, rendering failures)
    

---

## Implementation sketch for Codex

Implementation details are left intentionally open for Codex to complete, but the general steps are:

1. **Parse arguments**
    
    - Read `--vault-dir` and validate that it exists and is a directory
        
    - Determine `output_dir` inside that vault (default `_pdf_build`)
        
2. **Walk the vault**
    
    - Recursively walk `vault_dir`
        
    - For each file:
        
        - Skip if in `_pdf_build/` or `.obsidian/`
            
        - Skip if extension is not `.md`
            
    - Compute the relative path from `vault_dir`
        
    - Derive the output PDF path under `output_dir` with `.pdf` extension
        
3. **Read and transform Markdown**
    
    - Read the Markdown file in UTF-8
        
    - Check whether the content begins with an H1
        
    - If not, compute the title from the filename (strip extension) and inject `# Title` at the top
        
    - Optionally strip or process front matter if present
        
4. **Render to PDF**
    
    - Convert Markdown to HTML, including support for:
        
        - Headings, lists, emphasis, code, tables, task lists, images
            
    - Apply a CSS stylesheet optimized for screen reading:
        
        - Comfortable font size and line spacing
            
        - Clean default fonts
            
        - Proper spacing for headings and lists
            
    - Use an HTML→PDF engine (for example, WeasyPrint or similar library) to generate the PDF
        
    - Ensure relative image paths are resolved against the Markdown file’s directory
        
5. **Write output**
    
    - Create parent directories under `output_dir` as needed
        
    - Write the PDF to the target path
        
    - Optionally print progress
        

---

## Styling considerations for screen viewing

A default CSS theme might include:

- Sans-serif body font
    
- Slightly larger base font size (for example, 11–12 pt)
    
- Comfortable line height (for example, 1.4–1.6)
    
- Distinct hierarchy for headings
    
- Syntax highlighting for code blocks
    
- Task list checkboxes styled clearly
    
- Images constrained to the page width
    

These details can be refined later as part of the implementation and theming work.

---

## Future enhancements

Once the basic exporter works, potential improvements include:

- **Incremental builds**
    
    - Only re-export notes that have changed since the last run (based on modification timestamps or a simple cache file)
        
- **Multiple themes**
    
    - Different CSS themes (light, dark, print-friendly)
        
- **Per-folder or per-tag export**
    
    - Optional filters to export only a subset of the vault
        
- **Per-note metadata**
    
    - Use YAML front matter to control title, author, or PDF metadata
        
- **Integration with sync tools**
    
    - Scripts or documentation for integrating with `rclone` or other tools to sync `_pdf_build/` to Google Drive or other cloud storage
        

---

## Goals for the initial Codex implementation

For the first pass of Codex-generated code, the goal is:

1. Implement a CLI that:
    
    - Accepts `--vault-dir` and optionally `--output-dir`
        
    - Recursively finds `*.md` files under the vault
        
    - Skips `_pdf_build/` and `.obsidian/`
        
2. Inject the filename as H1 when needed
    
3. Convert Markdown to HTML with reasonable formatting
    
4. Produce PDFs into a mirrored directory structure under `_pdf_build/`
    
5. Log progress to the console
    

Subsequent iterations can refine PDF layout, theming, performance, and configurability.
