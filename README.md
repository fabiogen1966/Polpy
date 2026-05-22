# Polpy

Convertitore di file PCL/PRN in un unico documento PDF con interfaccia grafica Tkinter.

Polpy legge file `.prn` (output di stampa in formato PCL), rimuove le sequenze di escape, riconosce intestazioni e struttura del documento, e genera un PDF formattato.

## Funzionalità

- Interfaccia grafica con configurazione completa tramite tab
- Modalità CLI per automazione e scripting
- Configurazione parametrica via YAML
- Riconoscimento automatico di intestazioni, test e struttura documento
- Pulizia sequenze di escape PCL configurabile
- Supporto orientamento landscape/portrait e formati A4, Letter, Legal
- Build eseguibile standalone per distribuzione senza Python installato

## Download e utilizzo rapido (utente finale)

1. Scarica la cartella `dist/Polpy/` dal repository
2. Copia la cartella su qualsiasi PC Windows (7, 10, 11)
3. Metti i file `.prn` nella sottocartella `input/`
4. Doppio click su `Polpy.exe`
5. Dalla GUI configura i parametri e premi "Converti in PDF"
6. Il PDF viene generato nella cartella `output/`

> Non serve installare Python né altre dipendenze. L'exe è autocontenuto.

## Requisiti

- Python 3.8+ (testato con 3.8.10 e 3.13.5)
- Dipendenze: `reportlab`, `PyYAML`
- Piattaforma: Windows 7+ (compatibile Win7, Win10, Win11)

## Installazione

```bash
# Clona il repository
git clone https://github.com/GENSOFT/Polpy.git
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

L'interfaccia grafica permette di configurare tutti i parametri tramite tab dedicate:
- **File e Cartelle** — selezione input/output con browser, anteprima file trovati
- **Pagina** — orientamento, formato, margini
- **Font** — font normale e titoli, altezza riga
- **Pattern** — sequenze PCL da rimuovere, intestazioni speciali, pattern cambio pagina

### Modalità CLI

```bash
# Usa la modalità a riga di comando
python -m src --cli

# Con un file di configurazione personalizzato
python -m src --cli --config mio_config.yaml

# Specifica cartella di input e nome output
python -m src --cli --input ./miei_file --output report.pdf

# Specifica cartella di output
python -m src --cli --output-folder ./risultati
```

### Come comando installato

```bash
# CLI
polpy --help
polpy --input input --output report.pdf

# GUI
polpy-gui
```

## Build eseguibile (distribuzione standalone)

Per creare un `.exe` distribuibile su macchine senza Python installato (es. Windows 7):

### Prerequisiti di build

- Python 3.8.10 installato (scaricabile da [python.org](https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe))
- Il percorso di Python 3.8 deve essere configurato in `build.bat`

### Procedura

```bash
# Lancia lo script di build
build.bat
```

Lo script automaticamente:
1. Crea un virtual environment con Python 3.8
2. Installa le dipendenze + PyInstaller
3. Genera l'eseguibile in `dist\Polpy\`

### Risultato

```
dist\Polpy\
├── Polpy.exe        ← eseguibile (doppio click)
├── config.yaml      ← configurazione modificabile dall'utente
├── input\           ← cartella per i file .prn
├── output\          ← cartella di destinazione PDF
└── (DLL e librerie)
```

Per il deploy: copiare l'intera cartella `dist\Polpy\` sulla macchina target.

## Configurazione

Tutti i parametri sono configurabili tramite il file `config.yaml`:

| Parametro | Descrizione | Default |
|-----------|-------------|---------|
| `input_folder` | Cartella con i file PRN | `input` |
| `output_folder` | Cartella di destinazione del PDF | `output` |
| `output_filename` | Nome del file PDF generato | `output_finale.pdf` |
| `page.orientation` | Orientamento pagina (`landscape`/`portrait`) | `landscape` |
| `page.size` | Formato pagina (`A4`, `Letter`, `Legal`) | `A4` |
| `page.left_margin_mm` | Margine sinistro in mm | `10` |
| `page.top_margin_mm` | Margine superiore in mm | `20` |
| `page.bottom_margin_mm` | Margine inferiore in mm | `10` |
| `fonts.normal.name` | Font per il testo normale | `Courier` |
| `fonts.normal.size` | Dimensione font normale | `10.5` |
| `fonts.title.name` | Font per i titoli | `Courier-Bold` |
| `fonts.title.size` | Dimensione font titoli | `13` |
| `line_height` | Altezza riga in punti | `11.5` |
| `file_pattern` | Glob pattern per i file di input | `*.prn` |
| `pcl_cleanup_patterns` | Sequenze PCL da rimuovere | vedi config.yaml |
| `page_break_pattern` | Regex per il cambio pagina | `(pag\|pagina\|page)\s*\d+` |
| `special_headers` | Pattern per intestazioni speciali | vedi config.yaml |

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
├── LICENSE
├── .gitignore
├── input/                 # File PRN di input (esempio)
│   ├── DMEP_Efa_01.prn
│   └── ...
├── output/                # PDF generati
├── scripts/               # Script legacy/utility
│   └── converti_pcl_pdf.py
└── src/                   # Codice sorgente
    ├── __init__.py        # Versione del pacchetto
    ├── __main__.py        # Entry point (GUI default, --cli per CLI)
    ├── cli.py             # Interfaccia a riga di comando
    ├── config_loader.py   # Caricamento configurazione YAML
    ├── gui.py             # Interfaccia grafica Tkinter
    ├── pcl_cleaner.py     # Pulizia sequenze PCL
    └── pdf_generator.py   # Generazione del PDF
```

## Sviluppo

```bash
# Installa dipendenze di sviluppo
pip install -e ".[dev]"

# Linting
ruff check src/

# Test
pytest
```

## Licenza

MIT — vedi [LICENSE](LICENSE).
