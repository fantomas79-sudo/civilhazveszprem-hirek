# Gyere Hozzánk Dolgozni — prémium toborzó weboldal

Elegáns, sötét-arany, egyoldalas weboldal Ferenczy Attila biztosítási tanácsadói
toborzásához (Veszprém). Önálló, statikus oldal — nincs szükség build-lépésre.

## Fájlok

- `index.html` — a teljes oldal (HTML + CSS + JavaScript egyben)
- `README.md` — ez a leírás

## Megnyitás / használat

1. Másold be a mappát a saját gépeden a kívánt helyre (pl. `…\szia\`).
2. Nyisd meg az `index.html` fájlt bármelyik böngészőben (dupla kattintás).
3. Ennyi — a betűtípusok a Google Fontsról töltődnek, ehhez internet kell.

Publikáláshoz (élő weboldal) töltsd fel az `index.html`-t bármelyik tárhelyre,
vagy használj ingyenes hosztolást (pl. Netlify, GitHub Pages, Cloudflare Pages).

## A portréfotó cseréje

Az „RÓLAM" szekcióban jelenleg egy elegáns helykitöltő (`FA` monogram) látszik.
Csere valódi fotóra: az `index.html`-ben keresd meg a `class="portrait"` blokkot,
és cseréld a monogramot egy képre:

```html
<div class="portrait">
  <img src="ferenczy-attila.jpg" alt="Ferenczy Attila" style="width:100%;height:100%;object-fit:cover">
</div>
```

A `ferenczy-attila.jpg` fájlt tedd ugyanebbe a mappába.

## A jelentkezési űrlap bekötése

Alapból az űrlap a jelentkező adataival egy előre kitöltött e-mailt nyit meg
(a `info@gyerehozzankdolgozni.hu` címre). Ha azt szeretnéd, hogy az adatok
automatikusan megérkezzenek (e-mail nyitása nélkül), köss be egy űrlap-szolgáltatást:

1. Regisztrálj pl. a [Formspree](https://formspree.io) oldalon, és hozz létre egy űrlapot.
2. Az `index.html` alján, a `<script>`-ben állítsd be a végpontot:

```js
var FORM_ENDPOINT = "https://formspree.io/f/AZONOSÍTÓD";
var CONTACT_EMAIL = "info@gyerehozzankdolgozni.hu";
```

Ha a `FORM_ENDPOINT` üres marad, az űrlap a mailto-módszerrel működik.

## Testreszabás

- **Színek / betűk:** az `index.html` tetején, a `:root { … }` blokkban minden
  szín és alapbeállítás egy helyen van (arany, háttér, szövegszínek).
- **Elérhetőségek:** telefon és e-mail több helyen szerepel — keress rá a
  `+36308253488` és `info@gyerehozzankdolgozni.hu` értékekre.
- **Biztosítók listája:** a mozgó („marquee") sáv nevei a `mtrack` blokkban
  szerkeszthetők.

## Technikai jellemzők

- Reszponzív (mobil, tablet, asztali), mobil-first.
- Finom, GPU-barát animációk (csak `transform`/`opacity`), amelyek tiszteletben
  tartják a rendszer „csökkentett mozgás" (prefers-reduced-motion) beállítását.
- Akadálymentességi alapok: fókuszjelölés, aria-címkék, billentyűzet-navigáció,
  jó kontrasztarányok.
- Nincs külső függőség a Google Fontson kívül.
