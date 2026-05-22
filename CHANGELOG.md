# Changelog

## [1.2.0] - 2026-05-22

### Corretto
- Pattern test MMR: supporto numerazione paragrafi multi-livello (es. 10.4.3.4.3)
- Formattazione prime 2 righe: Courier-Bold 10.5 allineato a sinistra (non più centrato)
- Formattazione blocco certificato (file B): Courier-Bold 13 sottolineato centrato

### Migliorato
- Rilevamento formattazione PCL: distinzione tra bold font (`\x1b(s1B`), bold block (`\x1b&k1S`) e underline (`\x1b&dD`)
- `pcl_cleaner.py` restituisce tuple a 3 elementi `(riga, is_bold, is_underline)`
- Sottolineatura disegnata con `canvas.line()` nel PDF

## [1.1.0] - 2026-05-22

### Aggiunto
- Supporto profilo MMR (ANV-243 MMR-RNAV) con pattern specifici
- Selezione profilo nella GUI (DMEP, MMR, Tutti)
- Modulo `src/profiles.py` con definizione profili documento
- Script standalone: `converti_dmep_pdf.py`, `converti_mmr_pdf.py`, `converti_all_pdf.py`
- Pattern cambio pagina `- N -` (comune a DMEP e MMR)
- Pulizia sequenze PCL underline (`\x1b&dD`, `\x1b&d@`) per file MMR

### Modificato
- GUI semplificata: tab Conversione con radio button per profilo
- `pdf_generator.py` accetta parametro `profile` opzionale
- Output PDF separati per profilo (`DMEP_output.pdf`, `MMR_output.pdf`)

## [1.0.0] - 2026-05-19

### Aggiunto
- Interfaccia grafica Tkinter con configurazione completa tramite tab
- Modalità CLI con argomenti da riga di comando
- Configurazione parametrica via file YAML (`config.yaml`)
- Pulizia sequenze PCL configurabile
- Riconoscimento automatico intestazioni, test ATP e pattern di cambio pagina
- Build eseguibile standalone con PyInstaller per distribuzione su Windows 7+
- Supporto formati pagina A4, Letter, Legal in orientamento landscape/portrait
- Script di build automatizzato (`build.bat`)
- Compatibilità Python 3.8+ per supporto Windows 7
