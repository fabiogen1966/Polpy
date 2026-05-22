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
# PULIZIA PCL
# =====================================================

def clean_pcl(text):
    patterns = [
        r'\x1b\(s1Q',
        r'\x1b\(s1B',
        r'\x1b\(s0B',
        r'\x1b&k1S',
        r'\x1b&k0S',
    ]
    for p in patterns:
        text = re.sub(p, '', text)
    return text.replace('\r\n', '\n').replace('\r', '\n')

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
    text = clean_pcl(raw)
    lines = text.split("\n")

    if not any(l.strip() for l in lines):
        continue

    if not first:
        c.showPage()

    first = False
    y = top_margin

    for idx, line in enumerate(lines):
        stripped = line.strip()

        # Intestazioni speciali
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
        else:
            tm = test_pattern.match(stripped)
            if tm:
                test_no, par, desc = tm.groups()
                formatted = f"{test_no} - ATP Par. {par} {desc}"
                c.setFont(*title_font)
                c.drawCentredString(PAGE_W / 2, y, formatted)
                y -= (line_height + 2)
            else:
                c.setFont(*normal_font)
                c.drawString(left_margin, y, line.rstrip())
                y -= line_height

        # Cambio pagina logico
        if page_pattern.search(stripped):
            remaining = any(l.strip() for l in lines[idx + 1:])
            if remaining:
                c.showPage()
                y = top_margin
            continue

        # Overflow fisico
        if y < bottom_limit:
            remaining = any(l.strip() for l in lines[idx + 1:])
            if remaining:
                c.showPage()
                y = top_margin

# =====================================================
# SALVATAGGIO PDF
# =====================================================
c.save()
print(f"PDF creato: {OUTPUT_PDF}")
