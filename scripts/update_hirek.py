"""
Civil Ház Veszprém – Napi hírfrissítő szkript
Futtatás: py -3 update_hirek.py
Ütemezés: Windows Feladatütemező – naponta 07:00
Szükséges: pip install anthropic requests
"""

import anthropic
import json
import re
import sys
from datetime import date
from pathlib import Path

# ── KONFIGURÁCIÓ ────────────────────────────────────────────────
API_KEY = "IDE_ÍRJA_BE_AZ_ANTHROPIC_API_KULCSÁT"   # https://console.anthropic.com/
BASE_DIR = Path(__file__).parent
AKTUALIS = BASE_DIR / "aktualis.html"
INDEX    = BASE_DIR / "index.html"
LOG_FILE = BASE_DIR / "update_log.txt"
# ────────────────────────────────────────────────────────────────


def log(msg: str):
    ts = date.today().isoformat()
    line = f"[{ts}] {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def build_prompt() -> str:
    today = date.today()
    hu_months = ["január","február","március","április","május","június",
                 "július","augusztus","szeptember","október","november","december"]
    today_hu = f"{today.year}. {hu_months[today.month-1]} {today.day}."

    return f"""Te a Civil Ház Veszprém weboldal automatikus hírfrissítő rendszere vagy.
Ma: {today_hu}

FELADATOD:

1. Keress friss híreket az alábbi civil/pályázati témákban (webes keresés alapján):
   - NEA (Nemzeti Együttműködési Alap) aktuális hírek, döntések, határidők {today.year}
   - Norvég Civil Alap pályázat {today.year}
   - Falusi Civil Alap (FCA) / Városi Civil Alap (VCA) {today.year}
   - SZJA 1% civil szervezetek {today.year}
   - Civil szektort érintő jogszabályváltozások, határidők {today.year}
   - Veszprém civil szervezetek hírek {today.year}

2. Állíts össze 6-8 hírönkártyát JSON formátumban az alábbi sémával:
{{
  "frissitve": "{today_hu}",
  "hirek": [
    {{
      "id": "kebab-id",
      "cim": "Hír teljes címe",
      "osszefoglaló": "2-3 mondatos magyar összefoglaló. Konkrét számok, határidők kiemelve.",
      "kategoria": "palyazat|szamvitel|szektorhir|hataridok",
      "datum": "2026. május 30.",
      "forras_nev": "Forrás neve",
      "forras_url": "https://...",
      "tagek": ["TAG1","TAG2"],
      "allapot": "aktiv|lejart|varható"
    }}
  ],
  "hataridok_sidebar": [
    {{
      "nev": "Határidő neve",
      "datum": "2026. július 1.",
      "szin": "zold|sarga|piros",
      "megjegyzes": "Rövid megjegyzés"
    }}
  ]
}}

FONTOS SZABÁLYOK:
- Csak valós, ellenőrizhető forrásokból dolgozz (bgazrt.hu, civil.info.hu, nonprofit.hu, nav.gov.hu, okotars.hu stb.)
- Lezárt pályázatoknál: allapot = "lejart", de írd le az eredmény-várakozást
- Aktív határidőknél: pontos dátum, és emeld ki ha közeleg
- Magyar nyelv, közérthető fogalmazás
- A JSON-t ```json ... ``` blokkba tedd

Csak a JSON-t add vissza, semmi mást!
"""


def extract_json(text: str) -> dict:
    match = re.search(r'```json\s*([\s\S]*?)```', text)
    if match:
        return json.loads(match.group(1))
    # Ha nincs kód-blokk, próbálja közvetlenül
    return json.loads(text)


def article_html(h: dict) -> str:
    cat = h.get("kategoria", "palyazat")
    cat_map = {
        "palyazat":   ("thumb-palyazat",  "cat-palyazat",   "Pályázat"),
        "szamvitel":  ("thumb-szamvitel", "cat-szamvitel",  "Számvitel"),
        "szektorhir": ("thumb-szektorhir","cat-szektorhir", "Szektorhír"),
        "hataridok":  ("thumb-hataridok", "cat-hataridok",  "Sürgős határidő"),
    }
    thumb_cls, cat_cls, cat_label = cat_map.get(cat, cat_map["palyazat"])

    tagek = "".join(f'<span class="na-tag">{t}</span>' for t in h.get("tagek", []))
    allapot = h.get("allapot","aktiv")
    allapot_txt = {"aktiv": "", "lejart": " · Lezárult", "varható": " · Döntés várható"}.get(allapot, "")

    icon_svg = '''<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
      <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
    </svg>'''

    return f'''
    <article id="{h['id']}" class="news-article reveal" data-cat="{cat}">
      <a href="{h.get('forras_url','#')}" target="_blank" rel="noopener noreferrer" class="na-link">
        <div class="na-thumb {thumb_cls}">
          <div class="na-thumb-pattern" aria-hidden="true"></div>
          <div class="na-thumb-icon" aria-hidden="true">{icon_svg}</div>
        </div>
        <div class="na-body">
          <div class="na-meta">
            <span class="na-cat {cat_cls}">{cat_label}</span>
            <span class="na-date">{h.get('datum','')}{allapot_txt}</span>
          </div>
          <h2 class="na-title">{h['cim']}</h2>
          <p class="na-excerpt">{h.get('osszefoglaló','')}</p>
          <div class="na-tags">{tagek}</div>
        </div>
      </a>
      <div class="na-footer">
        <div class="na-source">Forrás: <a href="{h.get('forras_url','#')}" target="_blank" rel="noopener">{h.get('forras_nev','—')} ↗</a></div>
        <span class="na-read">Segítségre van szüksége? →</span>
      </div>
    </article>'''


def hatarido_html(hd: dict) -> str:
    szin_map = {"piros": "hd-piros", "sarga": "hd-sarga", "zold": "hd-zold"}
    cls = szin_map.get(hd.get("szin","zold"), "hd-zold")
    return f'''        <div class="hd-item {cls}">
          <div class="hd-name">{hd['nev']}</div>
          <div class="hd-date">{hd['datum']}</div>
          <div class="hd-sub">{hd.get('megjegyzes','')}</div>
        </div>'''


def update_aktualis(html: str, data: dict) -> str:
    # Csak az AUTOMATIKUS HÍREK zónát (BOT-HIREK) cseréljük.
    # A KÉZI HÍREK zónát (feltoltes.html) érintetlenül hagyjuk.
    articles_html = "\n".join(article_html(h) for h in data["hirek"])

    html = re.sub(
        r'(<!-- BOT-HIREK-START -->)([\s\S]*?)(<!-- BOT-HIREK-END -->)',
        lambda m: m.group(1) + "\n" + articles_html + "\n\n    " + m.group(3),
        html
    )

    # Határidők sidebar
    if data.get("hataridok_sidebar"):
        hd_html = "\n".join(hatarido_html(h) for h in data["hataridok_sidebar"])
        html = re.sub(
            r'(<div class="hatarido-list">)([\s\S]*?)(</div>)',
            rf'\1\n{hd_html}\n      \3',
            html,
            count=1
        )

    return html


def update_index(html: str, data: dict) -> str:
    hirek = data["hirek"][:3]
    if len(hirek) < 3:
        return html   # nem elég hír, kihagyjuk

    def img_cls(i: int, cat: str) -> str:
        classes = ["", " news-img-2", " news-img-3"]
        return f'news-img{classes[i]}'

    cards = ""

    # Nagy kártya (1.)
    h = hirek[0]
    cards += f'''      <article class="news-card reveal" style="transition-delay:.05s">
        <a href="aktualis.html#{h['id']}" style="display:block;">
          <div class="{img_cls(0, h['kategoria'])}">
            <div class="news-img-pattern" aria-hidden="true"></div>
            <span class="news-cat">{h['kategoria'].capitalize()} · {h.get('tagek',[''])[0]}</span>
          </div>
          <div class="news-body">
            <div class="news-date">{h['datum']}</div>
            <h3 class="news-title">{h['cim']}</h3>
            <p class="news-excerpt">{h['osszefoglaló'][:200]}...</p>
          </div>
        </a>
      </article>'''

    # Kis kártyák (2. és 3.)
    for i, h in enumerate(hirek[1:3], 1):
        delay = f".{i}s"
        cards += f'''
      <article class="news-card card-sm reveal" style="transition-delay:{delay}">
        <a href="aktualis.html#{h['id']}" style="display:block;">
          <div class="{img_cls(i, h['kategoria'])}">
            <div class="news-img-pattern" aria-hidden="true"></div>
            <span class="news-cat">{h['kategoria'].capitalize()} · {h.get('allapot','aktiv').capitalize()}</span>
          </div>
          <div class="news-body">
            <div class="news-date">{h['datum']}</div>
            <h3 class="news-title">{h['cim']}</h3>
          </div>
        </a>
      </article>'''

    html = re.sub(
        r'(<div class="news-grid">)([\s\S]*?)(</div>\s*</div>\s*<!-- /section -->|</div>\s*\n\s*</div>\s*\n\s*<!--.*?CONTACT|</div>\s*\n\s*</section>)',
        lambda m: m.group(1) + "\n" + cards + "\n    " + m.group(3),
        html,
        count=1
    )
    return html


def main():
    if API_KEY == "IDE_ÍRJA_BE_AZ_ANTHROPIC_API_KULCSÁT":
        log("HIBA: Adja meg az Anthropic API kulcsát az update_hirek.py fájlban!")
        sys.exit(1)

    log("Frissítés indul...")

    client = anthropic.Anthropic(api_key=API_KEY)

    try:
        log("Claude API hívás – hírek keresése...")
        message = client.messages.create(
            model="claude-opus-4-8",
            max_tokens=4096,
            messages=[{"role": "user", "content": build_prompt()}]
        )
        raw = message.content[0].text
        log(f"API válasz megérkezett ({len(raw)} karakter)")
    except Exception as e:
        log(f"API HIBA: {e}")
        sys.exit(1)

    try:
        data = extract_json(raw)
        log(f"{len(data['hirek'])} hír feldolgozva")
    except Exception as e:
        log(f"JSON feldolgozási hiba: {e}\nNyers válasz:\n{raw[:500]}")
        sys.exit(1)

    # aktualis.html frissítése
    try:
        html_a = AKTUALIS.read_text(encoding="utf-8")
        html_a = update_aktualis(html_a, data)
        AKTUALIS.write_text(html_a, encoding="utf-8")
        log(f"aktualis.html frissítve ({AKTUALIS})")
    except Exception as e:
        log(f"aktualis.html írási hiba: {e}")

    # index.html frissítése
    try:
        html_i = INDEX.read_text(encoding="utf-8")
        html_i = update_index(html_i, data)
        INDEX.write_text(html_i, encoding="utf-8")
        log(f"index.html frissítve ({INDEX})")
    except Exception as e:
        log(f"index.html írási hiba: {e}")

    log(f"✓ Kész – {data.get('frissitve', date.today().isoformat())}, {len(data['hirek'])} cikk")


if __name__ == "__main__":
    main()
