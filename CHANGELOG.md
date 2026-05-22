# Changelog

## [1.0.0] - 2024-05-19

### Aggiunto
- Interfaccia grafica Tkinter con configurazione completa tramite tab
- Modalità CLI con argomenti da riga di comando
- Configurazione parametrica via file YAML (`config.yaml`)
- Pulizia sequenze PCL configurabile
- Riconoscimento automatico intestazioni, test ATP e pattern di cambio pagina
- Build eseguibile standalone con PyInstaller per distribuzione su Windows 7+
- Supporto formati pagina A4, Letter, Legal in orientamento landscape/portrait
- Script di build automatizzato (`build.bat`)

### Struttura
- Progetto ristrutturato in pacchetto Python standard
- Separazione responsabilità: config, pulizia PCL, generazione PDF, CLI, GUI
- Compatibilità Python 3.8+ per supporto Windows 7
