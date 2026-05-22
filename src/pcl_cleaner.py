"""Pulizia delle sequenze PCL dal testo con rilevamento blocchi bold."""

import re
from typing import List, Tuple

# Marcatori bold PCL
BOLD_START = "\x1b&k1S"
BOLD_END = "\x1b&k0S"


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

    # Normalizza i fine riga
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    return text


def process_file_with_bold(raw_text: str, pcl_sequences: List[str]) -> List[Tuple[str, bool]]:
    """Processa un file PRN preservando l'informazione sui blocchi bold.

    Identifica le sezioni bold (delimitate da \\x1b&k1S ... \\x1b&k0S),
    rimuove tutte le sequenze PCL, e restituisce le righe con un flag
    che indica se la riga era in un blocco bold.

    Args:
        raw_text: Testo grezzo del file PRN.
        pcl_sequences: Lista di sequenze PCL letterali da rimuovere.

    Returns:
        Lista di tuple (testo_riga, is_bold).
    """
    # Identifica le sezioni bold
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

    # Rimuovi sequenze PCL preservando la mappa bold
    clean_chars = []
    bold_flags = []
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
