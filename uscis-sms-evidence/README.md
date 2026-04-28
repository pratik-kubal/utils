# uscis-sms-evidence

Generates a chronological, cover-page-prefixed PDF of SMS messages between you
and one specific contact (typically a spouse), formatted for USCIS
adjustment-of-status submissions.

The script reads an SMS Backup & Restore XML export, filters by phone number
and date range, optionally samples a representative subset across the date
range, and renders a clean PDF with a USCIS-style cover page.

## Getting the XML

The script needs an XML produced by **SMS Backup & Restore** (free, by
SyncTech, on the Play Store).

1. Install **SMS Backup & Restore** on the Android phone whose messages you
   want to export.
2. Open the app → **Back Up Now**.
3. Select **SMS** (and optionally **MMS** if you want MMS in the backup —
   note that the current script only renders `<sms>` elements; MMS is
   ignored).
4. Save the backup to Google Drive or local storage.
5. Download the resulting `sms-YYYYMMDDHHMMSS.xml` file to your computer and
   place it under `../data/` (the repo's shared `data/` directory). XML files
   in `data/` are git-ignored.

> This utility is an alternative to using the smsbackuprestore.com online
> viewer / desktop app for the filter-and-export step. You still need step 1
> (the phone backup); steps 2 and 3 from that workflow are replaced by
> running this script.

## Setup

```bash
cd uscis-sms-evidence
pip install -r requirements.txt
```

Create a `.env` file next to the script with the three required values
(git-ignored):

```
YOUR_NAME=Your Full Name
SPOUSE_NAME=Spouse Full Name
SPOUSE_PHONE=+15551234567
```

The script raises `KeyError` at startup if any are missing.

## Configuration

There is no CLI — edit the constants at the top of `sms_to_pdf.py`
before running.

| Constant | Purpose |
| --- | --- |
| `XML_FILE` | Path to the SMS Backup & Restore XML (relative to CWD). |
| `OUTPUT_PDF` | Where to write the PDF. |
| `START_DATE`, `END_DATE` | Inclusive `YYYY-MM-DD` filter. End date is bumped to 23:59:59 so the final day is fully included. Set to `None` to disable. |
| `SAMPLE_MODE` | `True` = generate an evenly-spread sample. `False` = include every matching message. |
| `SAMPLE_TARGET` | (Sample mode) Approximate total messages to include. |
| `SAMPLE_MIN_PER_MONTH` | (Sample mode) Floor per month so every month is represented. |
| `SAMPLE_WINDOW` | (Sample mode) Consecutive messages per pick — preserves natural back-and-forth. |
| `MAX_MESSAGES` | (Full mode) Hard cap, or `None` for no limit. |
| `EXCLUDED_FILE` | Path to a newline-delimited list of message bodies to drop. |
| `EXCLUSION_BEFORE`, `EXCLUSION_AFTER` | How many time-adjacent messages to also drop around each exclusion match (catches replies like "did you get it?"). |

Phone matching compares the **last 10 digits** of `SPOUSE_PHONE` against the
last 10 digits of each message's `address`, so numbers stored with or without
country code still match.

## Excluding sensitive messages

Create `uscis-sms-evidence/excluded.txt` (git-ignored) with one message body per line —
exact match against the stripped body. Lines starting with `#` and blank
lines are ignored. Each match also drops `EXCLUSION_BEFORE` / `EXCLUSION_AFTER`
adjacent messages.

If the file does not exist, no exclusion is applied.

## Run

```bash
cd uscis-sms-evidence
python sms_to_pdf.py
```

`XML_FILE` and `OUTPUT_PDF` are resolved relative to the current working
directory, so run from `uscis-sms-evidence/` or use absolute paths. Output
lands at `../output/sms_evidence_uscis.pdf` by default.

## Output

- **Cover page** — title, petitioner/beneficiary names, contact number, date
  range, total messages included, generation date, and a short attestation
  statement (wording adapts to sample vs. full mode).
- **Body** — messages in chronological order, grouped by day, color-coded
  by direction (sent vs. received), with timestamps.
