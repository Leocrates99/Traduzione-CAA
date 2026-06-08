#!/usr/bin/env python3
"""
ARASAAC FETCHER — espande il vocabolario CAA italiano scaricando dalla API ARASAAC.

USO:
    python arasaac_fetch.py

PRODUCE:
    arasaac_vocab_full.json        ← tutto il vocabolario italiano ARASAAC
    vocab_italiano_caa_estesa.json ← merge del vocabolario curato + ARASAAC

LICENZE:
    ARASAAC API: contenuti CC BY-NC-SA 4.0 (Gov. de Aragón). Riusare a fini educativi.
    Vedi: https://arasaac.org/condiciones-de-uso

IMPORTANTE: questo script non scarica i pittogrammi PNG di ARASAAC, solo metadati
(parole, categorie, sinonimi). Il rendering nelle tessere usa OpenMoji/Unicode.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

# Percorsi relativi
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHORTCODES_JSON = os.path.join(BASE_DIR, "emoji_shortcodes.json")
EMOJI_DATA_JS = os.path.join(BASE_DIR, "emoji_data.js")
CURATED_VOCAB = os.path.join(BASE_DIR, "vocab_italiano_caa.json")
ARASAAC_OUT = os.path.join(BASE_DIR, "arasaac_vocab_full.json")
MERGED_OUT = os.path.join(BASE_DIR, "vocab_italiano_caa_estesa.json")

# Endpoint API ARASAAC (v1 — stabile dal 2018)
ARASAAC_URL = "https://api.arasaac.org/v1/pictograms/all/it"

# Mapping numerico ARASAAC "type" → colore Fitzgerald
# (riferimento: ARASAAC categorizza per type 0..N, mappiamo al nostro schema)
ARASAAC_TYPE_TO_FITZ = {
    0: "verde",    # accion / verbo
    1: "giallo",   # nombre / sostantivo
    2: "blu",      # adjetivo
    3: "blu",      # adverbio (mappato a blu nel Fitzgerald esteso)
    4: "viola",    # tiempo
    5: "rosa",     # relacional / connettivo
    6: "giallo",   # social / interjeccion (default a sostantivo)
    7: "grigio",   # otro (articolo/pronome)
}

# Lookup shortcode emoji → unicode estratto da emoji_data.js
def load_emoji_shortcode_map():
    """Estrae da emoji_data.js il dict shortcode → emoji unicode."""
    if not os.path.exists(EMOJI_DATA_JS):
        print(f"  AVVISO: {EMOJI_DATA_JS} non trovato. Lancia prima build_mapping.py.")
        return {}
    import re
    with open(EMOJI_DATA_JS, encoding="utf-8") as f:
        txt = f.read()
    # Estrae tutti i {c: "shortcode", e: "emoji"}
    pairs = re.findall(r'\{c:\s*"([^"]+)",\s*e:\s*"([^"]+)"\}', txt)
    return dict(pairs)

def fetch_arasaac():
    """Scarica il JSON completo da ARASAAC API."""
    print(f"→ Richiesta a {ARASAAC_URL} ...")
    req = urllib.request.Request(
        ARASAAC_URL,
        headers={"User-Agent": "Inclusia/1.0 (Educational use; CAA editor)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read().decode("utf-8")
        data = json.loads(raw)
        print(f"  OK: ricevuti {len(data)} pittogrammi (~{len(raw)//1024} KB)")
        return data
    except urllib.error.HTTPError as e:
        print(f"  ERRORE HTTP {e.code}: {e.reason}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"  ERRORE rete: {e.reason}. Sei offline?")
        sys.exit(1)

def normalize_keyword(kw):
    """Pulisce la keyword italiana ARASAAC."""
    if not kw: return ""
    return kw.strip().lower().replace("  ", " ")

def guess_emoji_for_keyword(keyword, shortcode_map):
    """
    Cerca emoji corrispondenti alla keyword ARASAAC.
    Strategia:
    1. match esatto su shortcode (es. "cat" → 🐱)
    2. substring match (es. "fish_cake" se cerchi "pesce" non è ideale)
    3. niente (None)
    Ritorna (emoji, shortcode) o (None, None).
    """
    if not keyword: return None, None
    kw = keyword.lower().strip().replace(" ", "_")

    # 1. Match esatto
    if kw in shortcode_map:
        return shortcode_map[kw], kw

    # 2. Mappature italiano → shortcode inglese (estendere a piacere)
    IT_TO_EN = {
        "cane":"dog","gatto":"cat","casa":"house","scuola":"school",
        "libro":"book","libri":"books","quaderno":"notebook",
        "mela":"apple","pane":"bread","pizza":"pizza","pasta":"spaghetti",
        "sole":"sunny","luna":"moon","stella":"star","stelle":"stars",
        "mare":"ocean","fuoco":"fire","albero":"deciduous_tree",
        "fiore":"cherry_blossom","cuore":"heart",
        "macchina":"car","autobus":"bus","treno":"train2","aereo":"airplane",
        "uomo":"man","donna":"woman","bambino":"boy","bambina":"girl",
        "felice":"blush","triste":"cry","arrabbiato":"rage","stanco":"sleeping",
        "mangiare":"fork_and_knife","dormire":"sleeping","correre":"runner",
        "camminare":"walking","giocare":"video_game","studiare":"books",
        "leggere":"book","scrivere":"memo","cantare":"microphone","ballare":"dancer",
        "telefono":"iphone","computer":"computer","televisione":"tv",
        "ospedale":"hospital","chiesa":"church","banca":"bank",
    }
    if kw in IT_TO_EN and IT_TO_EN[kw] in shortcode_map:
        sc = IT_TO_EN[kw]
        return shortcode_map[sc], sc

    return None, None

def arasaac_to_vocab_entry(item, shortcode_map):
    """Trasforma un'entry ARASAAC nel nostro schema vocab."""
    # ARASAAC item ha: _id, keywords (list di {keyword, locale, type, hasLocution, plural, idKeyword}), type, categories
    keywords = item.get("keywords", [])
    if not keywords:
        return None
    main = keywords[0]
    parola_it = main.get("keyword", "").strip()
    if not parola_it:
        return None

    fitz = ARASAAC_TYPE_TO_FITZ.get(main.get("type", 1), "giallo")
    emoji, shortcode = guess_emoji_for_keyword(parola_it, shortcode_map)

    # 3 alternative: prima fra emoji random della stessa categoria semantica
    alternative = []
    categorie = item.get("categories", [])
    cat_str = categorie[0] if categorie else ""

    return {
        "id": f"arasaac_{item.get('_id')}",
        "parola": parola_it.capitalize(),
        "fitz": fitz,
        "emoji": emoji,
        "shortcode": shortcode,
        "alternative": alternative,
        "categoria": cat_str,
        "arasaac_id": item.get("_id"),
        "sinonimi": [normalize_keyword(k.get("keyword", "")) for k in keywords[1:]]
    }

def merge_with_curated(arasaac_entries, curated_path):
    """
    Unisce ARASAAC con il vocabolario curato.
    Le voci curate (matchate per parola) hanno priorità: il loro emoji + alternative restano.
    Le voci ARASAAC nuove vengono aggiunte.
    """
    with open(curated_path, encoding="utf-8") as f:
        curated_doc = json.load(f)
    curated_words = {e["parola"].lower(): e for e in curated_doc["parole"]}

    final = list(curated_doc["parole"])  # copia curato
    added = 0
    for a in arasaac_entries:
        if a["parola"].lower() not in curated_words:
            final.append(a)
            added += 1

    return {
        "_meta": {
            **curated_doc.get("_meta", {}),
            "estesa_con_arasaac": True,
            "totale_voci": len(final),
            "voci_da_arasaac": added,
            "voci_curate": len(curated_doc["parole"])
        },
        "parole": final
    }

def main():
    print("ARASAAC fetcher per Inclusia\n" + "=" * 40)

    shortcode_map = load_emoji_shortcode_map()
    print(f"Shortcodes emoji caricati: {len(shortcode_map)}")

    raw = fetch_arasaac()

    print(f"\n→ Trasformazione in schema Inclusia...")
    entries = []
    skipped = 0
    for item in raw:
        e = arasaac_to_vocab_entry(item, shortcode_map)
        if e: entries.append(e)
        else: skipped += 1
    print(f"  {len(entries)} entries valide, {skipped} scartate (senza keyword)")

    with open(ARASAAC_OUT, "w", encoding="utf-8") as f:
        json.dump({"parole": entries}, f, ensure_ascii=False, indent=2)
    print(f"  Salvato: {ARASAAC_OUT}")

    print(f"\n→ Merge con vocabolario curato...")
    merged = merge_with_curated(entries, CURATED_VOCAB)
    with open(MERGED_OUT, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"  Salvato: {MERGED_OUT}")
    print(f"  Totale voci finali: {merged['_meta']['totale_voci']}")
    print(f"  (curate: {merged['_meta']['voci_curate']}, da ARASAAC: {merged['_meta']['voci_da_arasaac']})")

    print(f"\n→ Per usarlo in Inclusia, sostituisci 'vocab_italiano_caa.json' con 'vocab_italiano_caa_estesa.json' nella costante CAA_VOCAB embedded nel file HTML.")
    print("Fatto!")

if __name__ == "__main__":
    main()
