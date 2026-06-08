# Inclusia — Editor CAA

[![Deploy](https://github.com/Leocrates99/Traduzione-CAA/actions/workflows/deploy.yml/badge.svg)](https://github.com/Leocrates99/Traduzione-CAA/actions/workflows/deploy.yml)

**App online**: <https://leocrates99.github.io/Traduzione-CAA/>

Editor web per la creazione di tavole di **Comunicazione Aumentativa e Alternativa** in italiano, basato sul **Codice di Fitzgerald** (sette colori grammaticali). Single-file HTML, nessun build step, nessun server.

I pittogrammi sono renderizzati con **OpenMoji** (CC BY-SA 4.0) per un'estetica moderna e coerente fra dispositivi. Le parole sono organizzate in un **vocabolario italiano CAA** curato, espandibile via API ARASAAC.

---

## Avvio rapido

### Online
Apri direttamente <https://leocrates99.github.io/Traduzione-CAA/>.

### Offline / locale
Scarica `index.html` (o clona il repo) e aprilo con un doppio click. Funziona offline dopo il primo caricamento (le librerie CDN e gli SVG OpenMoji vengono cachati nel browser).

---

## Funzionalità principali

| Area | Cosa fa |
|---|---|
| **Pittogrammi** | OpenMoji SVG (CDN jsDelivr) + cache `localStorage` + fallback emoji di sistema |
| **Vocabolario CAA** | 350 parole italiane curate per colore Fitzgerald, espandibile via ARASAAC |
| **Picker** | Due tab — Vocabolario CAA e tutte le emoji (868 voci, ricerca per nome) |
| **Suggerimenti** | Modal per parole senza emoji diretta (3-5 alternative + cerca + testo) |
| **Editor** | Undo/redo, debounce save, libreria tessere riutilizzabili, 6 template, ricerca progetti |
| **Esportazione** | PDF vettoriale (paginazione per nucleo), PNG con sizing, stampa A4 landscape, JSON |
| **UX** | ErrorBoundary, modal di conferma stilizzate, keyboard shortcuts (`Ctrl+Z`/`Y`/`Esc`/`Canc`) |
| **Privacy** | Salvataggio solo in `localStorage`, nessun server, backup JSON esportabile |

---

## Struttura repo

```
Traduzione-CAA/
├── index.html                          ← APP. Servito da Pages alla root.
├── README.md
├── LICENSE
├── .gitignore
├── .github/workflows/deploy.yml        ← Deploy automatico ad ogni push su main
├── build/                              ← Toolchain di generazione asset
│   ├── build_mapping.py                ← Rigenera emoji_data.js dal cheatsheet
│   ├── emoji_data.js                   ← 868 shortcode → unicode (già embedded)
│   ├── emoji_shortcodes.json
│   ├── vocab_italiano_caa.json         ← Vocabolario CAA curato (350 voci)
│   ├── arasaac_fetch.py                ← Espansione vocab via API ARASAAC
│   └── _vocab_embed.js                 ← Forma compatta per embed
└── sources/                            ← Materiali sorgente preservati
    ├── emoji-cheatsheet.zip
    └── inclusia-v1-original.html       ← Versione di partenza (pre-refactor)
```

---

## Workflow di lavoro

### Modifica al volo
1. Modifica `index.html` (è auto-contenuto, niente build)
2. `git commit -m "..." && git push`
3. GitHub Actions deploya in ~30 s su Pages

### Espandere il vocabolario CAA con ARASAAC

```bash
cd build/
python arasaac_fetch.py
```

Produce `arasaac_vocab_full.json` (~13.000 voci) e `vocab_italiano_caa_estesa.json` (merge curato + ARASAAC). Per integrarlo nell'app:

```bash
python -c "import json; d = json.load(open('vocab_italiano_caa_estesa.json', encoding='utf-8')); open('_vocab_embed.js','w',encoding='utf-8').write('const CAA_VOCAB = ' + json.dumps(d['parole'], ensure_ascii=False, separators=(',',':')) + ';')"
```

Poi sostituisci nel file `index.html` il blocco `const CAA_VOCAB = [...]` con il contenuto di `_vocab_embed.js`.

### Rigenerare il dizionario emoji

```bash
cd build/
python build_mapping.py
```

Aggiorna `emoji_data.js` e `emoji_shortcodes.json` dal cheatsheet in `sources/emoji-cheatsheet.zip`.

---

## Licenze e attribuzione

Codice: **MIT** (vedi `LICENSE`).

Asset di terze parti utilizzati:

- **OpenMoji** (CC BY-SA 4.0) — pittogrammi visualizzati nell'app. <https://openmoji.org>
- **GitHub emoji cheatsheet** (gist GitHub) — fonte dei 868 shortcode.
- **ARASAAC** (CC BY-NC-SA 4.0) — fonte opzionale per espansione vocabolario. <https://arasaac.org>
- **React 18**, **html2canvas**, **jsPDF** — librerie via CDN (rispettive licenze permissive).

Inclusia non ridistribuisce gli asset visivi ARASAAC: lo script `arasaac_fetch.py` scarica solo metadati testuali (parole, categorie, sinonimi) che vengono mappati a OpenMoji per il rendering.

---

## Privacy

Tutti i progetti sono salvati esclusivamente in `localStorage`:
- `caa_editor_data_v1` — progetti
- `caa_recent_emojis_v1` — emoji recenti
- `caa_tile_library_v1` — libreria tessere personale
- `caa_openmoji_cache_v1` — cache SVG OpenMoji

Nessun dato di progetto viene inviato a server esterni. Per la portabilità tra dispositivi usa **💾 Backup** (esporta tutto in JSON).
