"""
Civil Ház Veszprém – Felhős napi hírfrissítő
GitHub Actions futtatja naponta 07:00-kor (CET).
Anthropic API + web_search eszköz → aktualis.html + index.html frissítés.
"""

import anthropic
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

BASE_DIR  = Path(__file__).parent.parent
AKTUALIS  = BASE_DIR / "aktualis.html"
INDEX     = BASE_DIR / "index.html"

HU_MONTHS = ["január","február","március","április","május","június",
             "július","augusztus","szeptember","október","november","december"]

def today_hu() -> str:
    d = date.today()
    return f"{d.year}. {HU_MONTHS[d.month-1]} {d.day}."

# ── PROMPT ─────────────────────────────────────────────────────────────────────

SYSTEM = """Te a Civil Ház Veszprém weboldal automatikus hírfrissítő robotja vagy.
Feladatod: a webes kereső eszközzel megtalálni a legfrissebb magyar civil/nonprofit
szektort érintő híreket és pályázati aktualitásokat, majd ezeket strukturált JSON
formátumban visszaadni."""

def user_prompt() -> str:
    year = date.today().year
    return f"""Ma: {today_hu()}

Keresd meg a következő témákra vonatkozó LEGFRISSEBB híreket a weben:
1. NEA {year} (Nemzeti Együttműködési Alap) – döntések, kifizetések, új körök
2. Norvég Civil Alap {year} – aktív pályázatok, határidők
3. Falusi Civil Alap (FCA) / Városi Civil Alap (VCA) {year}
4. SZJA 1% civil szervezetek {year} – NAV frissítések, közzétételek
5. KAP civil szervezetek {year}
6. Civil szektort érintő jogszabályváltozás {year}
7. Veszprém megye civil aktualitások {year}

Ellenőrizd ezeket a forrásokat: civil.info.hu, nonprofit.hu, bgazrt.hu, nav.gov.hu,
okotars.hu, palyazatmenedzser.hu, erke.hu

Állíts össze pontosan 6 hírkártyát JSON formátumban:

```json
{{
  "frissitve": "{today_hu()}",
  "hirek": [
    {{
      "id": "rövid-kebab-id",
      "cim": "Pontos, informatív cím",
      "osszefoglalo": "2-3 mondatos összefoglaló konkrét számokkal, határidőkkel. Emeld ki a lényeget bold jelöléssel: **szöveg**.",
      "kategoria": "palyazat",
      "datum": "2026. június 3.",
      "forras_nev": "Forrás neve",
      "forras_url": "https://valós-url.hu",
      "tagek": ["TAG1", "TAG2", "TAG3"],
      "allapot": "aktiv"
    }}
  ],
  "hataridok": [
    {{
      "nev": "Határidő neve",
      "datum": "2026. július 1.",
      "szin": "zold",
      "megjegyzes": "Rövid leírás"
    }}
  ]
}}
```

Kategóriák (csak ezek egyike lehet): palyazat | szamvitel | szektorhir | hataridok
Állapotok: aktiv | lejart | varhato
Határidő-szín: piros (lejárt/sürgős) | sarga (közeledő) | zold (van még idő)
Határidők: max 4 db, legrelevánsabbak.

FONTOS:
- Csak valós, ellenőrizhető forrásokat használj!
- Magyar nyelv, közérthető fogalmazás civil szervezetek számára
- Lezárt pályázatoknál jelezd a döntés-várható státuszt
- A JSON-t pontosan ```json ... ``` blokkba tedd, res más szöveget ne adj!
"""

# ── JSON KINYERÉS ───────────────────────────────────────────────────────────────

def extract_json(text: str) -> dict:
    m = re.search(r'```json\s*([\s\S]*?)```', text)
    raw = m.group(1) if m else text
    return json.loads(raw)

# ── HTML GENERÁLÁS ──────────────────────────────────────────────────────────────

ICON_DOC = '''<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
  <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
</svg>'''

ICON_BUILDING = '''<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
  <path stroke-linecap="round" stroke-linejoin="round" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
</svg>'''

ICON_CHART = '''<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
  <path stroke-linecap="round" stroke-linejoin="round" d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
</svg>'''

ICON_HEART = '''<svg fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5" aria-hidden="true">
  <path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"/>
</svg>'''

CAT_MAP = {
    "palyazat":   ("thumb-palyazat",   "cat-palyazat",   "Pályázat",       ICON_DOC),
    "szamvitel":  ("thumb-szamvitel",  "cat-szamvitel",  "Számvitel",      ICON_CHART),
    "szektorhir": ("thumb-szektorhir", "cat-szektorhir", "Szektorhír",     ICON_HEART),
    "hataridok":  ("thumb-hataridok",  "cat-hataridok",  "Sürgős határidő",ICON_DOC),
}

def bold_to_strong(text: str) -> str:
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)

def article_html(h: dict, idx: int) -> str:
    cat    = h.get("kategoria", "palyazat")
    thumb_cls, cat_cls, cat_label, icon = CAT_MAP.get(cat, CAT_MAP["palyazat"])
    allapot = h.get("allapot", "aktiv")
    allapot_sfx = {"lejart": " · Lezárult", "varhato": " · Döntés várható"}.get(allapot, "")
    tagek_html = "".join(f'<span class="na-tag">{t}</span>' for t in h.get("tagek", []))
    excerpt = bold_to_strong(h.get("osszefoglalo", ""))

    return f'''
    <article id="{h['id']}" class="news-article reveal" data-cat="{cat}">
      <a href="{h.get('forras_url','#')}" target="_blank" rel="noopener noreferrer" class="na-link">
        <div class="na-thumb {thumb_cls}">
          <div class="na-thumb-pattern" aria-hidden="true"></div>
          <div class="na-thumb-icon" aria-hidden="true">{icon}</div>
        </div>
        <div class="na-body">
          <div class="na-meta">
            <span class="na-cat {cat_cls}">{cat_label}</span>
            <span class="na-date">{h.get('datum','')}{allapot_sfx}</span>
          </div>
          <h2 class="na-title">{h['cim']}</h2>
          <p class="na-excerpt">{excerpt}</p>
          <div class="na-tags">{tagek_html}</div>
        </div>
      </a>
      <div class="na-footer">
        <div class="na-source">Forrás: <a href="{h.get('forras_url','#')}" target="_blank" rel="noopener">{h.get('forras_nev','—')} ↗</a></div>
        <span class="na-read">Segítségre van szüksége? →</span>
      </div>
    </article>'''

def hatarido_html(hd: dict) -> str:
    cls_map = {"piros":"hd-piros", "sarga":"hd-sarga", "zold":"hd-zold"}
    cls = cls_map.get(hd.get("szin","zold"), "hd-zold")
    return (f'        <div class="hd-item {cls}">\n'
            f'          <div class="hd-name">{hd["nev"]}</div>\n'
            f'          <div class="hd-date">{hd["datum"]}</div>\n'
            f'          <div class="hd-sub">{hd.get("megjegyzes","")}</div>\n'
            f'        </div>')

# ── HTML FÁJLOK FRISSÍTÉSE ──────────────────────────────────────────────────────

def update_aktualis(html: str, data: dict) -> str:
    # Cikk-blokk csere
    articles = "\n".join(article_html(h, i) for i, h in enumerate(data["hirek"]))
    articles += ('\n\n    <div class="empty-state" id="emptyState" style="display:none;" role="status">'
                 '<p>Ebben a kategóriában jelenleg nincsenek hírek.</p></div>')
    html = re.sub(
        r'(<main id="news-feed"[^>]*>)([\s\S]*?)(</main>)',
        lambda m: m.group(1) + "\n" + articles + "\n\n  " + m.group(3),
        html
    )

    # Határidők sidebar csere
    if data.get("hataridok"):
        hd_block = "\n".join(hatarido_html(h) for h in data["hataridok"])
        html = re.sub(
            r'(<div class="hatarido-list">)([\s\S]*?)(</div>)',
            lambda m: m.group(1) + "\n" + hd_block + "\n      " + m.group(3),
            html, count=1
        )
    return html


def update_index(html: str, data: dict) -> str:
    hirek = data["hirek"][:3]
    if len(hirek) < 3:
        return html

    img_classes = ["news-img", "news-img news-img-2", "news-img news-img-3"]

    # Nagy kártya
    h0 = hirek[0]
    cat0 = h0.get("kategoria","palyazat").capitalize()
    tag0 = h0.get("tagek",[""])[0]
    excerpt0 = bold_to_strong(h0.get("osszefoglalo",""))[:220].rstrip() + "…"

    big_card = f'''      <article class="news-card reveal" style="transition-delay:.05s">
        <a href="aktualis.html#{h0['id']}" style="display:block;">
          <div class="{img_classes[0]}">
            <div class="news-img-pattern" aria-hidden="true"></div>
            <span class="news-cat">{cat0} · {tag0}</span>
          </div>
          <div class="news-body">
            <div class="news-date">{h0['datum']}</div>
            <h3 class="news-title">{h0['cim']}</h3>
            <p class="news-excerpt">{excerpt0}</p>
          </div>
        </a>
      </article>'''

    # Kis kártyák
    small_cards = ""
    for i, h in enumerate(hirek[1:3], 1):
        cat_i = h.get("kategoria","palyazat").capitalize()
        allapot_i = {"lejart":"Lezárult","varhato":"Döntés várható","aktiv":"Aktív"}.get(h.get("allapot","aktiv"),"Aktív")
        small_cards += f'''
      <article class="news-card card-sm reveal" style="transition-delay:.{i}s">
        <a href="aktualis.html#{h['id']}" style="display:block;">
          <div class="{img_classes[i]}">
            <div class="news-img-pattern" aria-hidden="true"></div>
            <span class="news-cat">{cat_i} · {allapot_i}</span>
          </div>
          <div class="news-body">
            <div class="news-date">{h['datum']}</div>
            <h3 class="news-title">{h['cim']}</h3>
          </div>
        </a>
      </article>'''

    new_grid_content = "\n" + big_card + small_cards + "\n    "

    html = re.sub(
        r'(<div class="news-grid">)([\s\S]*?)(</div>\s*\n\s*</div>\s*\n\s*<!--\s*═+\s*WIDGET)',
        lambda m: m.group(1) + new_grid_content + m.group(3),
        html, count=1
    )
    return html

# ── CLAUDE API HÍVÁS ───────────────────────────────────────────────────────────

def fetch_news() -> dict:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY környezeti változó hiányzik!")

    client = anthropic.Anthropic(api_key=api_key)

    print("Claude API hívás – webes keresés indul...")
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        system=SYSTEM,
        tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
        messages=[{"role": "user", "content": user_prompt()}]
    )

    # Szöveg tartalom összegyűjtése
    full_text = ""
    for block in response.content:
        if hasattr(block, "text"):
            full_text += block.text

    print(f"Válasz mérete: {len(full_text)} karakter")
    data = extract_json(full_text)
    print(f"Hírek száma: {len(data.get('hirek',[]))}")
    return data

# ── MAIN ───────────────────────────────────────────────────────────────────────

def main():
    print(f"=== Civil Ház hírfrissítő – {today_hu()} ===")

    data = fetch_news()

    # aktualis.html
    html_a = AKTUALIS.read_text(encoding="utf-8")
    html_a = update_aktualis(html_a, data)
    AKTUALIS.write_text(html_a, encoding="utf-8")
    print(f"✅ aktualis.html frissítve")

    # index.html
    html_i = INDEX.read_text(encoding="utf-8")
    html_i_new = update_index(html_i, data)
    if html_i_new != html_i:
        INDEX.write_text(html_i_new, encoding="utf-8")
        print(f"✅ index.html frissítve")
    else:
        print("ℹ️  index.html – nem változott (regex nem talált egyezést)")

    print(f"✓ Kész – {data.get('frissitve')}, {len(data.get('hirek',[]))} cikk")

if __name__ == "__main__":
    main()
