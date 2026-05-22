#!/usr/bin/env python
# coding: utf-8
"""
Conversione PCL/PRN → PDF per file MMR (ANV-243 MMR-RNAV).
Eseguire nella stessa directory che contiene i file MMR_Efa_*.prn.
Il PDF viene generato nella stessa directory.
"""

from pathlib import Path
import re
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.units import mm

# =====================================================
# CONFIGURAZIONE
# =====================================================
WORK_DIR = Path(".")
FILE_PATTERN = "MMR_Efa_*.prn"
OUTPUT_PDF = "MMR_output.pdf"

# =====================================================
# MARCATORI PCL
# =====================================================
BOLD_FONT_START = "\x1b(s1B"
BOLD_FONT_END = "\x1b(s0B"
BOLD_BLOCK_START = "\x1b&k1S"
BOLD_BLOCK_END = "\x1b&k0S"
UNDERLINE_START = "\x1b&dD"
UNDERLINE_END = "\x1b&d@"

PCL_SEQUENCES = ['\x1b(s1Q', '\x1b(s1B', '\x1b(s0B', '\x1b&k1S', '\x1b&k0S', '\x1b&dD', '\x1b&d@']


def process_file(raw_text):
    """Processa un file PRN e restituisce righe con flag bold e underline."""
    bold_font_ranges = []
    pos = 0
    while True:
        start = raw_text.find(BOLD_FONT_START, pos)
        if start == -1:
            break
        end = raw_text.find(BOLD_FONT_END, start)
        if end == -1:
            end = len(raw_text)
        bold_font_ranges.append((start, end + len(BOLD_FONT_END)))
        pos = end + len(BOLD_FONT_END)

    bold_block_ranges = []
    pos = 0
    while True:
        start = raw_text.find(BOLD_BLOCK_START, pos)
        if start == -1:
            break
        end = raw_text.find(BOLD_BLOCK_END, start)
        if end == -1:
            end = len(raw_text)
        bold_block_ranges.append((start, end + len(BOLD_BLOCK_END)))
        pos = end + len(BOLD_BLOCK_END)

    underline_ranges = []
    pos = 0
    while True:
        start = raw_text.find(UNDERLINE_START, pos)
        if start == -1:
            break
        end = raw_text.find(UNDERLINE_END, start)
        if end == -1:
            end = len(raw_text)
        underline_ranges.append((start, end + len(UNDERLINE_END)))
        pos = end + len(UNDERLINE_END)

    clean_chars = []
    bold_flags = []
    underline_flags = []
    i = 0
    while i < len(raw_text):
        matched = False
        for p in PCL_SEQUENCES:
            if raw_text[i:i+len(p)] == p:
                i += len(p)
                matched = True
                break
        if matched:
            continue
        is_bold = (any(start <= i < end for start, end in bold_font_ranges) or
                   any(start <= i < end for start, end in bold_block_ranges))
        is_underline = any(start <= i < end for start, end in underline_ranges)
        clean_chars.append(raw_text[i])
        bold_flags.append(is_bold)
        underline_flags.append(is_underline)
        i += 1

    clean_text = "".join(clean_chars).replace('\r\n', '\n').replace('\r', '\n')

    lines = clean_text.split('\n')
    result = []
    char_idx = 0
    for line in lines:
        line_len = len(line)
        if line_len > 0:
            line_non_space = sum(1 for c in line if c.strip())
            if line_non_space > 0:
                line_bold = sum(1 for j in range(char_idx, char_idx + line_len)
                                if j < len(bold_flags) and bold_flags[j] and clean_chars[j].strip())
                line_ul = sum(1 for j in range(char_idx, char_idx + line_len)
                              if j < len(underline_flags) and underline_flags[j] and clean_chars[j].strip())
                is_bold_line = line_bold > line_non_space * 0.5
                is_ul_line = line_ul > line_non_space * 0.5
            else:
                is_bold_line = False
                is_ul_line = False
        else:
            is_bold_line = False
            is_ul_line = False
        result.append((line, is_bold_line, is_ul_line))
        char_idx += line_len + 1
    return result


def draw_underlined_text(c, x, y, text, font_name, font_size):
    """Disegna testo centrato con sottolineatura."""
    c.setFont(font_name, font_size)
    c.drawCentredString(x, y, text)
    text_width = c.stringWidth(text, font_name, font_size)
    c.setLineWidth(0.5)
    c.line(x - text_width / 2, y - 2, x + text_width / 2, y - 2)


# =====================================================
# LETTURA FILES
# =====================================================
files = sorted(WORK_DIR.glob(FILE_PATTERN))
if not files:
    print(f"Nessun file '{FILE_PATTERN}' trovato nella directory corrente.")
    exit(1)
print(f"Trovati {len(files)} file MMR da elaborare...")

# =====================================================
# CREAZIONE PDF
# =====================================================
PAGE_W, PAGE_H = landscape(A4)
c = canvas.Canvas(OUTPUT_PDF, pagesize=landscape(A4))

normal_font = ("Courier", 10.5)
title_font = ("Courier-Bold", 13)
line_height = 11.5
left_margin = 10 * mm
top_margin = PAGE_H - 20 * mm
bottom_limit = 10 * mm

page_pattern = re.compile(r'-\s*\d+\s*-\s*$')
test_pattern = re.compile(
    r'^\s*(0[1-9]|[12]\d|30)\s*-\s*(\d+\.\d+(?:\.\d+)?)\s+(.+?)\s*$', re.IGNORECASE)
consumption_pattern = re.compile(
    r'^\s*01\s*-\s*[\d.]+\s+Equipment\s+Power\s+Supply\s+Consumption\s*$', re.IGNORECASE)
special_headers = [
    re.compile(r'SPE-J-343-A-0041', re.IGNORECASE),
    re.compile(r'ANV-243\s+MMR-RNAV\s+P/N', re.IGNORECASE),
]

# =====================================================
# ELABORAZIONE
# =====================================================
first = True
for file in files:
    raw = file.read_text(errors="ignore")
    processed_lines = process_file(raw)

    if not any(line.strip() for line, _, _ in processed_lines):
        continue
    if not first:
        c.showPage()
    first = False
    y = top_margin

    for idx, (line, is_bold, is_underline) in enumerate(processed_lines):
        stripped = line.strip()

        if any(p.search(stripped) for p in special_headers):
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, stripped)
            y -= (line_height + 2)
        elif consumption_pattern.match(stripped):
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, stripped)
            y -= (line_height + 2)
        elif test_pattern.match(stripped):
            tm = test_pattern.match(stripped)
            test_no, par, desc = tm.groups()
            formatted = f"{test_no} - {par} {desc}"
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, formatted)
            y -= (line_height + 2)
        elif is_bold and is_underline and stripped:
            draw_underlined_text(c, PAGE_W / 2, y, stripped, title_font[0], title_font[1])
            y -= (line_height + 2)
        elif is_bold and stripped:
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, stripped)
            y -= (line_height + 2)
        else:
            c.setFont(*normal_font)
            c.drawString(left_margin, y, line.rstrip())
            y -= line_height

        if page_pattern.search(stripped):
            remaining = any(l.strip() for l, _, _ in processed_lines[idx + 1:])
            if remaining:
                c.showPage()
                y = top_margin
            continue
        if y < bottom_limit:
            remaining = any(l.strip() for l, _, _ in processed_lines[idx + 1:])
            if remaining:
                c.showPage()
                y = top_margin

c.save()
print(f"PDF creato: {OUTPUT_PDF}")
