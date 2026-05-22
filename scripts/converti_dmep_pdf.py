#!/usr/bin/env python
# coding: utf-8
"""
Conversione PCL/PRN → PDF per file DMEP (ANV-213 DME-P).
Eseguire nella stessa directory che contiene i file DMEP_Efa_*.prn.
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
FILE_PATTERN = "DMEP_Efa_*.prn"
OUTPUT_PDF = "DMEP_output.pdf"

# =====================================================
# PULIZIA PCL (preserva marcatori bold per il file B)
# =====================================================

# Marcatore per testo bold/centrato (blocco titolo nel file B)
BOLD_START = "\x1b&k1S"
BOLD_END = "\x1b&k0S"
UNDERLINE_START = "\x1b&dD"
UNDERLINE_END = "\x1b&d@"


def process_file(raw_text):
    """Processa un file PRN e restituisce una lista di righe con flag bold.

    Returns:
        Lista di tuple (testo_riga, is_bold)
    """
    # Identifica le sezioni bold nel testo raw
    # Il blocco bold è delimitato da \x1b&k1S ... \x1b&k0S
    bold_ranges = []
    pos = 0
    while True:
        start = raw_text.find(BOLD_START, pos)
        if start == -1:
            break
        end = raw_text.find(BOLD_END, start)
        if end == -1:
            end = len(raw_text)
        bold_ranges.append((start, end + len(BOLD_END)))
        pos = end + len(BOLD_END)

    # Rimuovi tutte le sequenze PCL
    patterns = [
        r'\x1b\(s1Q',
        r'\x1b\(s1B',
        r'\x1b\(s0B',
        r'\x1b&k1S',
        r'\x1b&k0S',
        r'\x1b&dD',
        r'\x1b&d@',
    ]

    # Mappa posizioni originali -> posizioni pulite
    # Per ogni carattere nel testo originale, calcola se era in un blocco bold
    clean_chars = []
    bold_flags = []
    i = 0
    while i < len(raw_text):
        # Controlla se siamo all'inizio di una sequenza PCL da rimuovere
        matched = False
        for p in ['\x1b(s1Q', '\x1b(s1B', '\x1b(s0B', '\x1b&k1S', '\x1b&k0S', '\x1b&dD', '\x1b&d@']:
            if raw_text[i:i+len(p)] == p:
                i += len(p)
                matched = True
                break
        if matched:
            continue

        # Determina se il carattere corrente è in un blocco bold
        is_bold = any(start <= i < end for start, end in bold_ranges)
        clean_chars.append(raw_text[i])
        bold_flags.append(is_bold)
        i += 1

    clean_text = "".join(clean_chars)
    clean_text = clean_text.replace('\r\n', '\n').replace('\r', '\n')

    # Ricostruisci i flag bold per riga
    lines = clean_text.split('\n')
    result = []
    char_idx = 0
    for line in lines:
        line_len = len(line)
        if line_len > 0:
            # Una riga è bold se la maggior parte dei suoi caratteri non-spazio sono bold
            line_bold_chars = sum(1 for j in range(char_idx, char_idx + line_len)
                                 if j < len(bold_flags) and bold_flags[j]
                                 and clean_chars[j].strip())
            line_non_space = sum(1 for c in line if c.strip())
            is_bold_line = line_non_space > 0 and line_bold_chars > line_non_space * 0.5
        else:
            is_bold_line = False
        result.append((line, is_bold_line))
        char_idx += line_len + 1  # +1 per il \n

    return result


# =====================================================
# LETTURA FILES
# =====================================================

files = sorted(WORK_DIR.glob(FILE_PATTERN))

if not files:
    print(f"Nessun file '{FILE_PATTERN}' trovato nella directory corrente.")
    exit(1)

print(f"Trovati {len(files)} file DMEP da elaborare...")

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

# =====================================================
# REGEX
# =====================================================

# Cambio pagina: "- N -" a fine riga
page_pattern = re.compile(r'-\s*\d+\s*-\s*$')

# Test DMEP: "NN - ATP Par. X.X descrizione" (01-18)
test_pattern = re.compile(
    r'^\s*(0[1-9]|1[0-8])\s*-\s*(?:ATP\s+Par\.\s*)?([0-9.]+)\s+(.+?)\s*$',
    re.IGNORECASE
)

# Consumption DMEP
consumption_pattern = re.compile(
    r'^\s*01\s*-\s*Consumption\s*$',
    re.IGNORECASE
)

# Intestazioni speciali DMEP
special_headers = [
    re.compile(r'SPE-J-344-A-0044', re.IGNORECASE),
    re.compile(r'ANV-213\s+DME-P\s+P/N', re.IGNORECASE),
]

# =====================================================
# ELABORAZIONE FILES
# =====================================================

first = True

for file in files:
    raw = file.read_text(errors="ignore")
    processed_lines = process_file(raw)

    if not any(line.strip() for line, _ in processed_lines):
        continue

    if not first:
        c.showPage()

    first = False
    y = top_margin

    for idx, (line, is_bold) in enumerate(processed_lines):
        stripped = line.strip()

        # Intestazioni speciali (dal pattern)
        if any(p.search(stripped) for p in special_headers):
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, stripped)
            y -= (line_height + 2)

        # Consumption
        elif consumption_pattern.match(stripped):
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, stripped)
            y -= (line_height + 2)

        # Test
        elif test_pattern.match(stripped):
            tm = test_pattern.match(stripped)
            test_no, par, desc = tm.groups()
            formatted = f"{test_no} - ATP Par. {par} {desc}"
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, formatted)
            y -= (line_height + 2)

        # Testo bold (dal file B - blocco titolo certificato)
        elif is_bold and stripped:
            c.setFont(*title_font)
            c.drawCentredString(PAGE_W / 2, y, stripped)
            y -= (line_height + 2)

        # Testo normale
        else:
            c.setFont(*normal_font)
            c.drawString(left_margin, y, line.rstrip())
            y -= line_height

        # Cambio pagina logico
        if page_pattern.search(stripped):
            remaining = any(l.strip() for l, _ in processed_lines[idx + 1:])
            if remaining:
                c.showPage()
                y = top_margin
            continue

        # Overflow fisico
        if y < bottom_limit:
            remaining = any(l.strip() for l, _ in processed_lines[idx + 1:])
            if remaining:
                c.showPage()
                y = top_margin

# =====================================================
# SALVATAGGIO PDF
# =====================================================
c.save()
print(f"PDF creato: {OUTPUT_PDF}")
