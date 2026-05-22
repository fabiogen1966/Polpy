"""Pulizia delle sequenze PCL dal testo."""

import re
from typing import List


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
