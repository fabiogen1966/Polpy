"""Profili di conversione per i diversi tipi di documento."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class DocumentProfile:
    """Profilo di un tipo di documento."""

    name: str
    file_pattern: str
    output_filename: str
    test_pattern: str
    consumption_pattern: str
    special_headers: List[str] = field(default_factory=list)
    pcl_cleanup_patterns: List[str] = field(default_factory=list)
    page_break_pattern: str = r'-\s*\d+\s*-\s*$'


# Profilo DMEP (ANV-213 DME-P)
PROFILE_DMEP = DocumentProfile(
    name="DMEP",
    file_pattern="DMEP_Efa_*.prn",
    output_filename="DMEP_output.pdf",
    test_pattern=r'^\s*(0[1-9]|1[0-8])\s*-\s*(?:ATP\s+Par\.\s*)?([0-9.]+)\s+(.+?)\s*$',
    consumption_pattern=r'^\s*01\s*-\s*Consumption\s*$',
    special_headers=[
        r'SPE-J-344-A-0044',
        r'ANV-213\s+DME-P\s+P/N',
    ],
    pcl_cleanup_patterns=[
        r'\x1b\(s1Q',
        r'\x1b\(s1B',
        r'\x1b\(s0B',
        r'\x1b&k1S',
        r'\x1b&k0S',
    ],
)

# Profilo MMR (ANV-243 MMR-RNAV)
PROFILE_MMR = DocumentProfile(
    name="MMR",
    file_pattern="MMR_Efa_*.prn",
    output_filename="MMR_output.pdf",
    test_pattern=r'^\s*(0[1-9]|[12]\d|30)\s*-\s*(\d+\.\d+(?:\.\d+)?)\s+(.+?)\s*$',
    consumption_pattern=r'^\s*01\s*-\s*[\d.]+\s+Equipment\s+Power\s+Supply\s+Consumption\s*$',
    special_headers=[
        r'SPE-J-343-A-0041',
        r'ANV-243\s+MMR-RNAV\s+P/N',
    ],
    pcl_cleanup_patterns=[
        r'\x1b\(s1Q',
        r'\x1b\(s1B',
        r'\x1b\(s0B',
        r'\x1b&k1S',
        r'\x1b&k0S',
        r'\x1b&dD',
        r'\x1b&d@',
    ],
)

# Tutti i profili disponibili
ALL_PROFILES = {
    "DMEP": PROFILE_DMEP,
    "MMR": PROFILE_MMR,
}
