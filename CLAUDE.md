# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository purpose

A personal collection of standalone utility scripts. Each utility lives in its own top-level subdirectory with its own dependencies; there is no shared package or build system. The shared `data/` directory holds input files used by one or more utilities — `*.xml` is git-ignored, and `.gitkeep` preserves the directory.

## Utilities

### uscis-sms-evidence

Parses an SMS Backup & Restore XML export and renders a chronological, cover-page-prefixed PDF intended for USCIS adjustment-of-status submissions.

Setup and run:
```bash
cd uscis-sms-evidence
pip install -r requirements.txt
python sms_to_pdf.py
```

Configuration lives as module-level constants at the top of `uscis-sms-evidence/sms_to_pdf.py` (`XML_FILE`, `OUTPUT_PDF`, `EXCLUDED_LOG`, `START_DATE`, `END_DATE`, `MAX_MESSAGES`, plus `SAMPLE_MODE` and the `EXCLUDED_FILE`/`EXCLUSION_BEFORE`/`EXCLUSION_AFTER` exclusion knobs) — there is no CLI argument parsing. Edit the constants before running. Sensitive values (`YOUR_NAME`, `SPOUSE_NAME`, `SPOUSE_PHONE`) are loaded from `uscis-sms-evidence/.env` (git-ignored, resolved relative to the script) via `python-dotenv` and are required — the script raises `KeyError` if any are missing.

Architectural notes worth knowing before editing:
- Phone matching is intentionally lenient: `normalize_phone` strips non-digits and the comparison uses **the last 10 digits** so numbers stored with or without country codes still match. Don't tighten this without good reason.
- SMS Backup & Restore encodes direction in the `type` attribute: `'1'` = received, `'2'` = sent. `sms_to_pdf.py` branches on this string in `load_messages` and again at render time (`is_sent = msg['type'] == '2'`); preserve the string comparison (the XML stores it as a string).
- Message bodies are HTML-escaped manually before being passed to ReportLab `Paragraph` (`&`, `<`, `>`) because Paragraph interprets a mini-HTML subset. Any new fields rendered through Paragraph need the same treatment.
- Date filtering uses `START_DATE`/`END_DATE` inclusive; the end date is bumped to `23:59:59` so the final day is fully included.
- `XML_FILE` is a relative path resolved from the current working directory — run from `uscis-sms-evidence/` or pass an absolute path. Real input XMLs are expected to live in `../data/` and are git-ignored.

## Conventions

- New utilities should follow the same shape: their own subdirectory, their own `requirements.txt` (or equivalent), config-by-constants unless a CLI is genuinely warranted, and inputs read from `data/` when shareable.
