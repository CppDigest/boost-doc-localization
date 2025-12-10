# Markdown in Weblate

This document explains how Weblate handles Markdown files using its built-in `Markdown` format and the underlying Translate Toolkit converters.

## How it works (concrete flow)
- Format registration: `MarkdownFormat` in `weblate/formats/convert.py` (monolingual, autoload `*.md`/`*.markdown`, checks: `md-text`, `safe-html`, `strict-same`).
- Loading a source file:
  1) Weblate wraps the Markdown bytes with `NamedBytesIO`.
  2) `translate.storage.markdown.MarkdownFile` parses it via `mistletoe`.
  3) It emits translation units: one per paragraph; YAML front matter becomes a header unit; inline markup (links, HTML spans, autolinks) is replaced with placeholders `{1}`, `{2}`, … so URLs/ids stay intact.
  4) Weblate converts that parsed store to a PO-like store (`convert_to_po`), merging with an existing template if present.
- Saving a translated file:
  1) `translate.convert.po2md.MarkdownTranslator` reads the template Markdown (source language) and the translated PO-like store.
  2) For each source string, it substitutes the translated target (or fuzzy if allowed) while expanding placeholders back to their original link/HTML content.
  3) It writes translated Markdown, respecting `max_line_length` (default 80; set 0 to disable reflow).

## Key behaviors
- One unit per paragraph: encourages natural segmentation and reuse; long paragraphs can be split upstream if needed.
- Placeholder protection: link targets, HTML spans, autolinks become placeholders; only visible text is translatable.
- Front matter preserved: YAML front matter is a header unit; it is kept as-is unless translated by editing that header unit.
- Whitespace normalization: source text is normalized for PO; output may be reflowed unless `max_line_length` is 0.
- Checks: `md-text` (Markdown-aware), `safe-html`, `strict-same` help catch broken markup.

## Practical tips
- Keep URLs/ids untouched; translate link text and optional titles.
- Avoid heavy embedded HTML; if present, ensure tags are balanced so placeholders round-trip.
- If exact wrapping matters (e.g., docs with deliberate line breaks), set `max_line_length` to 0 in format options or adjust downstream.
- For very large Markdown with mixed HTML/shortcodes, consider a PO-first pipeline (po4a/pandoc) and reconvert in CI.
- Front matter: if you need specific keys translated, ensure they are plain text; otherwise they remain as-is.

## Files to know
- `weblate/formats/convert.py` — `MarkdownFormat` wiring of load/save.
- `translate/storage/markdown.py` — Markdown parsing, unit creation, placeholders, front matter handling.
- `translate/convert/po2md.py` — Merging translations back to Markdown, reflow handling.

## Relevant code
- `weblate/formats/convert.py` — defines `MarkdownFormat` and wires load/save to Translate Toolkit.
- `translate/storage/markdown.py` — parses Markdown with `mistletoe`, creates units, handles placeholders and link/title translation, preserves front matter.
- `translate/convert/po2md.py` — merges translations from the PO-like store back into Markdown using `MarkdownTranslator`.