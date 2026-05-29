# Inclusia — Editor CAA

Editor per la creazione di tavole CAA (Comunicazione Aumentativa e Alternativa) basato sul **Codice di Fitzgerald** (colori grammaticali). Applicazione web standalone in singolo file HTML, nessun build step richiesto.

I pittogrammi sono renderizzati con **OpenMoji** (CC BY-SA 4.0) per un'estetica moderna e coerente fra tutti i sistemi operativi; le parole CAA sono organizzate in un **vocabolario italiano curato** (ispirato ad ARASAAC, espandibile via API).

## Struttura cartella

```
inclusia-project/
├── inclusia.html                       ← APP. Aprilo nel browser per usare l'editor.
├── README.md                           ← Questo file.
├── build/                              ← Toolchain di generazione asset.
│   ├── build_mapping.py                ← Rigenera emoji_data.js dal cheatsheet GitHub.
│   ├── emoji_data.js                   ← 868 shortcode → unicode (già embedded).
│   ├── emoji_shortcodes.json           ← Indice shortcode per categoria.
│   ├── vocab_italiano_caa.json         ← Vocabolario CAA curato (350 voci, già embedded).
│   ├── arasaac_fetch.py                ← Scarica vocabolario completo da API ARASAAC (~13k voci).
│   └── _vocab_embed.js                 ← Forma compatta del vocab per embed (artefatto).
└── sources/                            ← Materiali sorgente, da preservare.
    ├── emoji-cheatsheet.zip            ← Archivio gist GitHub.
    ├── emoji-cheatsheet-extracted/     ← Cheatsheet estratto.
    └── inclusia-v1-original.html       ← Versione di partenza (pre-refactor).
```

## Avvio

Apri `inclusia.html` con un doppio click. La prima volta scarica:
- React, html2canvas, jsPDF (CDN unpkg/cdnjs, ~1.5 MB)
- SVG OpenMoji on-demand (CDN jsDelivr, ~3-5 KB per emoji, cached in `localStorage`)

Dopo la prima sessione tutto funziona offline; la cache OpenMoji rimane fino allo svuotamento dei dati del browser.

## Rigenerare il dizionario emoji

```bash
cd build/
python build_mapping.py
```

Produce `emoji_data.js` (da copiare manualmente in `inclusia.html` dentro la costante `EMOJI_DATA`) e `emoji_shortcodes.json`.

## Espandere il vocabolario CAA con ARASAAC

Il vocabolario curato include ~350 parole italiane comuni con mappatura emoji + 3-5 alternative. Per espandere fino a ~13 000 voci scaricando dalla API ARASAAC:

```bash
cd build/
python arasaac_fetch.py
```

Produce:
- `arasaac_vocab_full.json` — tutto il vocabolario italiano ARASAAC con mappatura emoji euristica
- `vocab_italiano_caa_estesa.json` — merge fra curato + ARASAAC

Per integrarlo, rigenera l'embed e sostituiscilo dentro `inclusia.html`:

```python
import json
d = json.load(open('vocab_italiano_caa_estesa.json', encoding='utf-8'))
open('_vocab_embed.js', 'w', encoding='utf-8').write(
    'const CAA_VOCAB = ' + json.dumps(d['parole'], ensure_ascii=False, separators=(',',':')) + ';'
)
```

Poi sostituisci nel file `inclusia.html` il blocco `const CAA_VOCAB = [...]` con il contenuto di `_vocab_embed.js`.

## Funzionalità implementate

### Pittogrammi
- **OpenMoji SVG** come rendering primario (estetica flat, coerente, CC BY-SA 4.0)
- Fallback automatico a **emoji di sistema** se OpenMoji non ha il glifo
- **Cache localStorage** persistente: scarichi una volta, riusi sempre

### Vocabolario CAA
- **350 parole italiane curate** organizzate per colore Fitzgerald
- Ogni parola ha emoji diretta + 3-5 alternative "vicine" semanticamente
- **Suggerimenti automatici** per parole senza emoji equivalente (~15% del vocabolario)
- Categorie semantiche: famiglia, animali, cibo, luoghi, oggetti, vestiti, trasporti, natura, corpo, ecc.

### Editor
- **Codice di Fitzgerald** con 7 colori per categorie grammaticali
- **Modalità testo** per parole prive di pittogramma (es. "XIII secolo")
- **Undo/Redo** con history stack (max 50), `Ctrl+Z` / `Ctrl+Y`
- **Salvataggio automatico** debounce 300 ms in `localStorage`
- **Libreria tessere** personale per riutilizzo (max 30 tessere)
- **Template progetto** (Vuoto, Frase singola, Racconto, 2×4, 4×4, Settimana)
- **Ricerca progetti** per titolo o nucleo

### Picker emoji
- **Due tab**: "📋 Vocabolario CAA" (default) + "😀 Tutte le emoji" (868 voci)
- Tab Vocabolario: parole raggruppate per colore Fitzgerald, ricerca per parola/categoria
- Tab Emoji: tab Recenti, categorie sticky, ricerca per nome shortcode
- **Modal Suggerimenti**: si apre quando la parola CAA non ha emoji diretta, propone 3-5 alternative + "cerca altre" + "usa come testo"

### Esportazione
- **PDF vettoriale** con paginazione per nucleo (no spezzature)
- **PNG** con ridimensionamento automatico (soglia ~6 megapixel)
- **Stampa** A4 landscape
- **Import / Export JSON** (singolo progetto o backup completo)

### Robustezza
- **ErrorBoundary** + modal di conferma stilizzate
- **Accessibilità di base** (`aria-label`, navigazione da tastiera, focus visibile)
- **ID crittografici** con `crypto.randomUUID()` + fallback

## Licenze e attribuzione

- **OpenMoji** (CC BY-SA 4.0) — pittogrammi visualizzati in app. https://openmoji.org
- **GitHub emoji cheatsheet** (citato da gist GitHub) — fonte dei 868 shortcode.
- **ARASAAC** (CC BY-NC-SA 4.0) — eventuale espansione vocabolario tramite `arasaac_fetch.py`. https://arasaac.org

Inclusia non ridistribuisce assets ARASAAC: il suo script di fetch scarica solo metadati testuali (parole, categorie, sinonimi) che vengono mappati a OpenMoji per il rendering.

## Dati e privacy

Tutti i progetti sono salvati esclusivamente nel `localStorage` del browser (chiave `caa_editor_data_v1`). La cache OpenMoji è in `caa_openmoji_cache_v1`. Nessun dato di progetto viene inviato a server esterni. Per la portabilità tra dispositivi usa il pulsante **💾 Backup** (esporta tutto in JSON).
