"""
SMS to PDF Converter for USCIS Green Card Interview
----------------------------------------------------
Parses an SMS Backup & Restore XML file, filters messages by contact,
and generates a clean, labeled PDF suitable for USCIS submission.

Supports two modes:
  - FULL MODE:   Include all messages (or up to MAX_MESSAGES)
  - SAMPLE MODE: Automatically pick a representative sample spread evenly
                 across all months in the date range, preserving natural
                 conversation flow within each sampled window.

Requirements:
    pip install reportlab

Usage:
    python sms_to_pdf.py
"""

import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from tqdm import tqdm
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT

# ─────────────────────────────────────────────
# CONFIGURE THESE BEFORE RUNNING
# ─────────────────────────────────────────────

XML_FILE = "../data/sms-20260428085010.xml"        # Path to your XML backup file
OUTPUT_PDF = "../output/sms_evidence_uscis.pdf"    # Output PDF filename
EXCLUDED_LOG = "../output/sms_excluded_log.txt"    # Audit log of dropped messages

# Sensitive values are loaded from .env next to this script.
# Required keys: YOUR_NAME, SPOUSE_NAME, SPOUSE_PHONE.
load_dotenv(Path(__file__).parent / ".env")

YOUR_NAME = os.environ["YOUR_NAME"]
SPOUSE_NAME = os.environ["SPOUSE_NAME"]
SPOUSE_PHONE = os.environ["SPOUSE_PHONE"]

# Date range filter (set to None to include all messages)
START_DATE = "2023-09-27"                  # Format: YYYY-MM-DD  (or None)
END_DATE   = "2026-04-28"                  # Format: YYYY-MM-DD  (or None)

# ── Sampling Settings ────────────────────────
# Set SAMPLE_MODE = True to automatically generate a representative sample.
# Set SAMPLE_MODE = False to include all messages (up to MAX_MESSAGES).

SAMPLE_MODE = True

# (Only used when SAMPLE_MODE = True)
# Target total number of messages across the whole date range.
# The script spreads this budget evenly across all months.
SAMPLE_TARGET = 400

# Minimum messages to include per month (even if the month has few messages).
# This ensures every month of the relationship is represented.
SAMPLE_MIN_PER_MONTH = 10

# Window size: how many consecutive messages to pull per sample point.
# e.g. 5 means "pick a spot in the month, grab 5 messages in a row"
# This preserves natural back-and-forth conversation context.
SAMPLE_WINDOW = 10

# (Only used when SAMPLE_MODE = False)
# Hard cap on total messages. Set to None for no limit.
MAX_MESSAGES = None

# ── Exclusion Settings ───────────────────────
# Path to a newline-delimited file of message bodies to exclude (exact match
# against the stripped body). Lines starting with `#` and blank lines are
# ignored. Git-ignored — see .gitignore. If the file does not exist, no
# exclusion is applied.
EXCLUDED_FILE = Path(__file__).parent / "excluded.txt"

# When a message matches the exclusion list, also drop this many time-adjacent
# messages before and after it (the "sliding window" — catches replies like
# "did you get it?" that reference the sensitive message).
EXCLUSION_BEFORE = 1
EXCLUSION_AFTER  = 1

# ─────────────────────────────────────────────


def parse_date(ms_timestamp):
    """Convert millisecond timestamp to datetime."""
    return datetime.fromtimestamp(int(ms_timestamp) / 1000)


def normalize_phone(phone):
    """Strip non-digit characters for comparison."""
    return ''.join(filter(str.isdigit, phone or ''))


def load_excluded(path):
    """Read newline-delimited exact-match patterns; skip blanks and `#` comments."""
    if not path.exists():
        return set()
    patterns = set()
    for line in path.read_text(encoding='utf-8').splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        patterns.add(stripped)
    return patterns


def apply_exclusions(messages, excluded, before, after):
    """
    Drop messages whose body exactly matches an excluded pattern, plus
    `before` time-adjacent messages before each match and `after` messages
    after. Overlapping windows merge naturally via set union. Assumes
    `messages` is already sorted chronologically.

    Returns (kept, dropped, match_count) where each entry in `dropped`
    is the original message dict augmented with a `reason` key — either
    `"match"` (exact body match) or `"radius"` (caught by the sliding
    window around a match).
    """
    if not excluded or not messages:
        return messages, [], 0

    n = len(messages)
    drop = set()
    matched_indices = set()
    for i, msg in enumerate(messages):
        if msg['body'] in excluded:
            matched_indices.add(i)
            for j in range(max(0, i - before), min(n, i + after + 1)):
                drop.add(j)

    if not drop:
        return messages, [], 0

    kept = [m for i, m in enumerate(messages) if i not in drop]
    dropped = [
        {**messages[i],
         'reason': 'match' if i in matched_indices else 'radius'}
        for i in sorted(drop)
    ]
    return kept, dropped, len(matched_indices)


def write_excluded_log(dropped, log_path, your_name, spouse_name):
    """Write dropped messages to a plain-text audit log, one per line."""
    log_path = Path(log_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Excluded SMS audit log — generated {datetime.now().isoformat(timespec='seconds')}",
        f"# {len(dropped)} messages dropped "
        f"({sum(1 for m in dropped if m['reason'] == 'match')} exact matches, "
        f"{sum(1 for m in dropped if m['reason'] == 'radius')} radius)",
        "",
    ]
    for msg in dropped:
        sender = your_name if msg['type'] == '2' else spouse_name
        ts = msg['date'].strftime("%Y-%m-%d %H:%M:%S")
        body = msg['body'].replace('\n', ' ').replace('\r', ' ')
        lines.append(f"[{ts}] [{msg['reason']:6}] {sender}: {body}")
    log_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"  Excluded log written to {log_path}")


def load_messages(xml_file, spouse_phone, start_date=None, end_date=None):
    """Parse XML and return filtered messages."""
    print(f"Parsing {xml_file} ...")
    tree = ET.parse(xml_file)
    root = tree.getroot()

    spouse_digits = normalize_phone(spouse_phone)

    start_dt = datetime.strptime(start_date, "%Y-%m-%d") if start_date else None
    end_dt   = datetime.strptime(end_date,   "%Y-%m-%d").replace(
                   hour=23, minute=59, second=59) if end_date else None

    messages = []

    sms_elements = root.findall('sms')
    for sms in tqdm(sms_elements, desc="Parsing messages", unit="msg"):
        address = sms.get('address', '')
        address_digits = normalize_phone(address)

        # Match by last 10 digits to handle country code variations
        if address_digits[-10:] != spouse_digits[-10:]:
            continue

        try:
            dt = parse_date(sms.get('date', '0'))
        except Exception:
            continue

        if start_dt and dt < start_dt:
            continue
        if end_dt and dt > end_dt:
            continue

        msg_type = sms.get('type', '1')  # 1 = received, 2 = sent
        body = sms.get('body', '').strip()

        if not body:
            continue

        messages.append({
            'date': dt,
            'type': msg_type,
            'body': body,
        })

    messages.sort(key=lambda x: x['date'])
    print(f"  Found {len(messages)} messages matching your filter.")
    return messages


def sample_messages(messages, target, min_per_month, window_size):
    """
    Select a representative sample spread evenly across all months.

    Strategy:
    - Group messages by (year, month)
    - Allocate a message budget to each month proportionally,
      with a guaranteed minimum per month
    - Within each month, pick evenly spaced windows of consecutive
      messages so natural conversation context is preserved
    - Deduplicate and re-sort at the end
    """
    if not messages:
        return messages

    by_month = defaultdict(list)
    for msg in messages:
        key = (msg['date'].year, msg['date'].month)
        by_month[key].append(msg)

    months = sorted(by_month.keys())
    num_months = len(months)
    base_per_month = max(min_per_month, target // num_months)

    sampled = []
    total_original = len(messages)

    for month_key in months:
        month_msgs = by_month[month_key]
        n = len(month_msgs)
        alloc = min(n, base_per_month)

        if alloc >= n:
            sampled.extend(month_msgs)
            continue

        # Pick evenly spaced windows across the month
        num_windows = max(1, alloc // window_size)
        selected_indices = set()

        for w in range(num_windows):
            if num_windows > 1:
                start = int(w * (n - window_size) / (num_windows - 1))
            else:
                start = n // 2
            start = max(0, min(start, n - window_size))
            for i in range(start, min(start + window_size, n)):
                selected_indices.add(i)
                if len(selected_indices) >= alloc:
                    break
            if len(selected_indices) >= alloc:
                break

        sampled.extend(month_msgs[i] for i in sorted(selected_indices))

    sampled.sort(key=lambda x: x['date'])

    year_str = f"{months[0][0]}/{months[0][1]:02d}"
    year_end = f"{months[-1][0]}/{months[-1][1]:02d}"
    print(f"  Sampled {len(sampled)} messages from {total_original} total "
          f"({year_str} to {year_end}, {num_months} months covered)")
    return sampled


def build_pdf(messages, output_pdf, your_name, spouse_name, spouse_phone,
              start_date, end_date, max_messages, sample_mode):
    """Generate a clean USCIS-formatted PDF."""

    if not sample_mode and max_messages:
        messages = messages[:max_messages]

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'Title', parent=styles['Title'],
        fontSize=16, spaceAfter=6, textColor=colors.HexColor('#1a1a2e')
    )
    subtitle_style = ParagraphStyle(
        'Subtitle', parent=styles['Normal'],
        fontSize=11, spaceAfter=4, textColor=colors.HexColor('#333333'),
        alignment=TA_CENTER
    )
    meta_style = ParagraphStyle(
        'Meta', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#555555'),
        alignment=TA_CENTER, spaceAfter=4
    )
    date_header_style = ParagraphStyle(
        'DateHeader', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#888888'),
        alignment=TA_CENTER, spaceAfter=2, spaceBefore=10
    )
    sent_label_style = ParagraphStyle(
        'SentLabel', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#2563eb'),
        alignment=TA_RIGHT
    )
    recv_label_style = ParagraphStyle(
        'RecvLabel', parent=styles['Normal'],
        fontSize=8, textColor=colors.HexColor('#16a34a'),
        alignment=TA_LEFT
    )
    sent_msg_style = ParagraphStyle(
        'SentMsg', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#1e3a5f'),
        alignment=TA_RIGHT, spaceAfter=6
    )
    recv_msg_style = ParagraphStyle(
        'RecvMsg', parent=styles['Normal'],
        fontSize=10, textColor=colors.HexColor('#1a3d2b'),
        alignment=TA_LEFT, spaceAfter=6
    )
    note_style = ParagraphStyle(
        'Note', parent=styles['Normal'],
        fontSize=9, textColor=colors.HexColor('#666666'),
        alignment=TA_CENTER, spaceAfter=4
    )

    story = []

    # ── Cover Page ──────────────────────────────────────────
    story.append(Spacer(1, 0.8 * inch))
    story.append(Paragraph("SMS MESSAGE EVIDENCE", title_style))
    story.append(Paragraph("Submitted in Support of Adjustment of Status", subtitle_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 0.3 * inch))

    cover_data = [
        ["Petitioner / Applicant:", spouse_name],
        ["Spouse / Beneficiary:", your_name],
        ["Contact Number:", spouse_phone],
        ["Date Range:",
         f"{start_date or 'All'} to {end_date or 'Present'}"],
        ["Total Messages Included:", str(len(messages))],
        ["Document Generated:", datetime.now().strftime("%B %d, %Y")],
    ]

    cover_table = Table(cover_data, colWidths=[2.2 * inch, 4 * inch])
    cover_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#333333')),
        ('TEXTCOLOR', (1, 0), (1, -1), colors.HexColor('#111111')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1),
         [colors.HexColor('#f9f9f9'), colors.white]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(cover_table)
    story.append(Spacer(1, 0.4 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cccccc')))
    story.append(Spacer(1, 0.3 * inch))

    story.append(Paragraph(
        ("This document contains a representative sample of SMS text message "
         "communications between the petitioner and their spouse, selected to "
         "reflect the full duration of the relationship. "
         if sample_mode else
         "This document contains ALL of the SMS text message communications between the "
         "petitioner and their spouse. ") +
        "Messages are presented in chronological order and have not been altered.",
        note_style
    ))

    story.append(PageBreak())

    # ── Messages ─────────────────────────────────────────────
    current_day = None

    for msg in tqdm(messages, desc="Rendering PDF", unit="msg"):
        day_str = msg['date'].strftime("%A, %B %d, %Y")

        if day_str != current_day:
            current_day = day_str
            story.append(Spacer(1, 0.15 * inch))
            story.append(HRFlowable(
                width="80%", thickness=0.5,
                color=colors.HexColor('#dddddd'), hAlign='CENTER'
            ))
            story.append(Paragraph(day_str, date_header_style))

        time_str = msg['date'].strftime("%-I:%M %p")
        is_sent = msg['type'] == '2'
        body = msg['body'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

        if is_sent:
            story.append(Paragraph(f"{your_name}  ·  {time_str}", sent_label_style))
            story.append(Paragraph(body, sent_msg_style))
        else:
            story.append(Paragraph(f"{spouse_name}  ·  {time_str}", recv_label_style))
            story.append(Paragraph(body, recv_msg_style))

    print(f"Building PDF: {output_pdf} ...")
    doc.build(story)
    print(f"Done! PDF saved to: {output_pdf}")
    print(f"Total messages included: {len(messages)}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    msgs = load_messages(XML_FILE, SPOUSE_PHONE, START_DATE, END_DATE)

    excluded = load_excluded(EXCLUDED_FILE)
    if excluded:
        msgs, dropped, matched = apply_exclusions(
            msgs, excluded, EXCLUSION_BEFORE, EXCLUSION_AFTER
        )
        print(f"  Excluded {len(dropped)} messages "
              f"({matched} exact matches × radius {EXCLUSION_BEFORE}/{EXCLUSION_AFTER})")
        if dropped:
            write_excluded_log(dropped, EXCLUDED_LOG, YOUR_NAME, SPOUSE_NAME)
    else:
        print(f"  No exclusion file at {EXCLUDED_FILE} — skipping exclusion step.")

    if not msgs:
        print("\n⚠️  No messages found. Check:")
        print(f"   1. SPOUSE_PHONE matches the number in the XML")
        print(f"   2. The date range overlaps with your messages")
        print(f"   3. XML_FILE path is correct")
        print("\nTip: Open your XML file and search for your wife's number to see")
        print("     exactly how it's stored (e.g. with or without country code).")
    else:
        if SAMPLE_MODE:
            print(f"\nSample mode ON — targeting ~{SAMPLE_TARGET} messages "
                  f"(min {SAMPLE_MIN_PER_MONTH}/month, window {SAMPLE_WINDOW})")
            msgs = sample_messages(msgs, SAMPLE_TARGET, SAMPLE_MIN_PER_MONTH, SAMPLE_WINDOW)
        else:
            print(f"\nFull mode — including all {len(msgs)} messages"
                  + (f" (capped at {MAX_MESSAGES})" if MAX_MESSAGES else ""))

        build_pdf(
            msgs,
            OUTPUT_PDF,
            YOUR_NAME,
            SPOUSE_NAME,
            SPOUSE_PHONE,
            START_DATE,
            END_DATE,
            MAX_MESSAGES,
            SAMPLE_MODE,
        )