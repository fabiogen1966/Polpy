# Polpy

Convertitore di file PCL/PRN in PDF con interfaccia grafica Tkinter.

Polpy legge file `.prn` (output di stampa in formato PCL), rimuove le sequenze di escape, riconosce intestazioni e struttura del documento, e genera PDF formattati. Supporta più profili documento con rilevamento automatico.

## Profili supportati

| Profilo | Equipaggiamento | File pattern | Output |
|---------|----------------|--------------|--------|
| **DMEP** | ANV-213 DME-P | `DMEP_Efa_*.prn` | `DMEP_output.pdf` |
| **MMR** | ANV-243 MMR-RNAV | `MMR_Efa_*.prn` | `MMR_output.pdf` |

## Funzionalità

- Interfaccia grafica con selezione profilo (DMEP, MMR, o entrambi)
- Modalità CLI per automazione e scripting
- Configurazione parametrica (pagina, font, margini)
- Riconoscimento automatico di intestazioni, test e struttura documento
- Pulizia sequenze di escape PCL per profilo
- Supporto orientamento landscape/portrait e formati A4, Letter, Legal
- Eseguibile standalone per distribuzione senza Python installato

## Download e utilizzo rapido (utente finale)

1. Vai alla pagina [Releases](https://github.com/fabiogen1966/Polpy/releases/latest)
2. Scarica `Polpy.exe`
3. Metti l'exe in una cartella a piacere
4. Crea accanto all'exe le cartelle `input/` e `output/`
5. Metti i file `.prn` nella cartella `input/`
6. Doppio click su `Polpy.exe`
7. Seleziona il tipo di documento (DMEP, MMR, o Tutti)
8. Premi "Converti in PDF"
9. I PDF vengono generati nella cartella `output/`

> Non serve installare Python né altre dipendenze. L'exe è autocontenuto e compatibile con Windows 7, 10, 11.

## Requisiti (solo per sviluppo)

- Python 3.8+ (testato con 3.8.10 e 3.13.5)
- Dipendenze: `reportlab`, `PyYAML`
- Piattaforma: Windows 7+

## Installazione (sviluppatori)

```bash
# Clona il repository
git clone https://github.com/fabiogen1966/Polpy.git
cd Polpy

# Crea un virtual environment
python -m venv .venv
.venv\Scripts\activate

# Installa le dipendenze
pip install -r requirements.txt

# Oppure installa come pacchetto (include i comandi CLI e GUI)
pip install -e .
```

## Utilizzo

### Interfaccia grafica (default)

```bash
python -m src
```

La GUI presenta:
- **Tab Conversione** — selezione cartelle, scelta profilo (DMEP/MMR/Tutti), anteprima file, pulsante conversione
- **Tab Pagina** — orientamento, formato, margini
- **Tab Font** — font normale e titoli, altezza riga

### Modalità CLI

```bash
python -m src --cli
python -m src --cli --input ./miei_file --output-folder ./risultati
```

### Script standalone (da eseguire nella directory dei file .prn)

```bash
cd <cartella con i .prn>

# Solo DMEP
python <percorso>/scripts/converti_dmep_pdf.py

# Solo MMR
python <percorso>/scripts/converti_mmr_pdf.py

# Entrambi
python <percorso>/scripts/converti_all_pdf.py
```

### Come comando installato

```bash
polpy --help
polpy-gui
```

## Build eseguibile (distribuzione standalone)

Per ricreare l'exe distribuibile su macchine senza Python:

### Prerequisiti di build

- Python 3.8.10 installato (scaricabile da [python.org](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe))
- Il percorso di Python 3.8 deve essere configurato in `build.bat`

### Procedura

```bash
build.bat
```

Lo script automaticamente:
1. Crea un virtual environment con Python 3.8
2. Installa le dipendenze + PyInstaller
3. Genera l'eseguibile standalone `dist/Polpy.exe`

## Configurazione

I parametri di pagina e font sono configurabili dalla GUI o tramite `config.yaml`:

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `page.orientation` | Orientamento pagina | `landscape` |
| `page.size` | Formato pagina (`A4`, `Letter`, `Legal`) | `A4` |
| `page.left_margin_mm` | Margine sinistro in mm | `10` |
| `page.top_margin_mm` | Margine superiore in mm | `20` |
| `page.bottom_margin_mm` | Margine inferiore in mm | `10` |
| `fonts.normal.name` | Font per il testo normale | `Courier` |
| `fonts.normal.size` | Dimensione font normale | `10.5` |
| `fonts.title.name` | Font per i titoli | `Courier-Bold` |
| `fonts.title.size` | Dimensione font titoli | `13` |
| `line_height` | Altezza riga in punti | `11.5` |

I pattern di riconoscimento (test, intestazioni, sequenze PCL) sono definiti nei profili in `src/profiles.py`.

## Struttura del progetto

```
Polpy/
├── config.yaml            # Configurazione parametrica
├── pyproject.toml         # Metadata e build del pacchetto
├── requirements.txt       # Dipendenze runtime
├── requirements-build.txt # Dipendenze per la build exe
├── build.bat              # Script di build automatizzato
├── polpy_app.py           # Entry point per PyInstaller
├── polpy.spec             # Configurazione PyInstaller
├── README.md
├── CHANGELOG.md
├── LICENSE
├── .gitignore
├── .gitattributes
├── dist/
│   └── Polpy.exe          # Eseguibile standalone
├── input/                 # Cartella per i file PRN di input
├── output/                # Cartella di destinazione PDF
├── scripts/               # Script standalone
│   ├── converti_dmep_pdf.py   # Solo DMEP
│   ├── converti_mmr_pdf.py    # Solo MMR
│   └── converti_all_pdf.py    # Entrambi
└── src/                   # Codice sorgente
    ├── __init__.py        # Versione del pacchetto
    ├── __main__.py        # Entry point (GUI default, --cli per CLI)
    ├── cli.py             # Interfaccia a riga di comando
    ├── config_loader.py   # Caricamento configurazione YAML
    ├── gui.py             # Interfaccia grafica Tkinter
    ├── pcl_cleaner.py     # Pulizia sequenze PCL
    ├── pdf_generator.py   # Generazione del PDF
    └── profiles.py        # Profili documento (DMEP, MMR)
```

## Sviluppo

```bash
pip install -e ".[dev]"
ruff check src/
pytest
```

## Licenza

MIT — vedi [LICENSE](LICENSE).
