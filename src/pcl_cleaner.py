"""Pulizia delle sequenze PCL dal testo con rilevamento formattazione."""

import re
from typing import List, Tuple

# Marcatori PCL
BOLD_FONT_START = "\x1b(s1B"    # Bold font on
BOLD_FONT_END = "\x1b(s0B"      # Bold font off
BOLD_BLOCK_START = "\x1b&k1S"   # Bold block start (titoli test)
BOLD_BLOCK_END = "\x1b&k0S"     # Bold block end
UNDERLINE_START = "\x1b&dD"     # Underline on
UNDERLINE_END = "\x1b&d@"       # Underline off


def clean_pcl(text: str, patterns: List[str]) -> str:
    """Rimuove le sequenze di escape PCL dal testo.

    Args:
        text: Testo grezzo contenente sequenze PCL.
        patterns: Lista di pattern regex da rimuovere.

    Returns:
        Testo ripulito dalle sequenze PCL.
    """
    for pattern in patterns:
        text = re.sub(pattern, "", text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def process_file_with_bold(raw_text: str, pcl_sequences: List[str]) -> List[Tuple[str, bool, bool]]:
    """Processa un file PRN preservando l'informazione sulla formattazione.

    Rileva:
    - Bold font (\\x1b(s1B ... \\x1b(s0B): intestazione file (prime 2 righe)
    - Bold block (\\x1b&k1S ... \\x1b&k0S): titoli test e intestazioni speciali
    - Underline (\\x1b&dD ... \\x1b&d@): blocco certificato nel file B

    Args:
        raw_text: Testo grezzo del file PRN.
        pcl_sequences: Lista di sequenze PCL letterali da rimuovere.

    Returns:
        Lista di tuple (testo_riga, is_bold, is_underline).
    """
    # Identifica le sezioni con bold font (\x1b(s1B ... \x1b(s0B)
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

    # Identifica le sezioni con bold block (\x1b&k1S ... \x1b&k0S)
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

    # Identifica le sezioni underline (\x1b&dD ... \x1b&d@)
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

    # Rimuovi sequenze PCL preservando la mappa di formattazione
    clean_chars = []
    bold_flags = []
    underline_flags = []
    i = 0
    while i < len(raw_text):
        matched = False
        for p in pcl_sequences:
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

    clean_text = "".join(clean_chars)
    clean_text = clean_text.replace('\r\n', '\n').replace('\r', '\n')

    # Ricostruisci i flag per riga
    lines = clean_text.split('\n')
    result = []
    char_idx = 0
    for line in lines:
        line_len = len(line)
        if line_len > 0:
            line_non_space = sum(1 for c in line if c.strip())
            if line_non_space > 0:
                line_bold_chars = sum(1 for j in range(char_idx, char_idx + line_len)
                                     if j < len(bold_flags) and bold_flags[j]
                                     and clean_chars[j].strip())
                line_underline_chars = sum(1 for j in range(char_idx, char_idx + line_len)
                                          if j < len(underline_flags) and underline_flags[j]
                                          and clean_chars[j].strip())
                is_bold_line = line_bold_chars > line_non_space * 0.5
                is_underline_line = line_underline_chars > line_non_space * 0.5
            else:
                is_bold_line = False
                is_underline_line = False
        else:
            is_bold_line = False
            is_underline_line = False
        result.append((line, is_bold_line, is_underline_line))
        char_idx += line_len + 1  # +1 per il \n

    return result
