# Civil Ház Veszprém – Weboldal telepítési útmutató

## Amit kap

- **Ingyenes webtárhely**: GitHub Pages (pl. `felhasználónév.github.io/civilhaz`)
- **Napi automatikus hírfrissítés**: minden reggel 07:00-kor, gép nélkül
- **Egyedi domain**: opcionálisan ráköthet saját domain-t (pl. `civilhazveszprem.hu`)

---

## 1. lépés – GitHub fiók létrehozása (ha még nincs)

1. Nyissa meg: **https://github.com**
2. Kattintson: **Sign up**
3. Adjon meg egy felhasználónevet, e-mailt és jelszót
4. Ingyenes fiók elegendő

---

## 2. lépés – Új repó létrehozása

1. GitHub.com → jobb felső sarokban: **+** → **New repository**
2. Repository name: `civilhaz` (vagy `civilhazveszprem`)
3. Legyen **Public** ✅ (ingyenes Pages-hez szükséges)
4. Kattintson: **Create repository**

---

## 3. lépés – Fájlok feltöltése

**Opció A – GitHub webes felület (egyszerűbb):**
1. A repó oldalán: **Add file** → **Upload files**
2. Húzza be az összes fájlt a `civilhazveszprem` mappából
3. Kattintson: **Commit changes**

**Opció B – Git parancssor:**
```bash
cd "J:\Saját meghajtó\Claude Workspace\CODE\WEB PAGES\civilhazveszprem"
git init
git add .
git commit -m "Civil Ház weboldal – első feltöltés"
git branch -M main
git remote add origin https://github.com/FELHASZNÁLÓNÉV/civilhaz.git
git push -u origin main
```

---

## 4. lépés – GitHub Pages bekapcsolása

1. A repó oldalán: **Settings** (fogaskerék ikon)
2. Bal oldali menü: **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main** → mappa: **/ (root)**
5. Kattintson: **Save**

⏳ 1-2 perc múlva elérhető: `https://FELHASZNÁLÓNÉV.github.io/civilhaz`

---

## 5. lépés – Anthropic API kulcs beállítása

Ez szükséges a napi hírfrissítéshez.

### API kulcs megszerzése:
1. Nyissa meg: **https://console.anthropic.com**
2. Regisztráció / bejelentkezés
3. **API Keys** → **Create Key**
4. Másolja ki: `sk-ant-...`

### Kulcs hozzáadása GitHub Secretshez:
1. A repó oldalán: **Settings** → **Secrets and variables** → **Actions**
2. Kattintson: **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Secret: illessze be az `sk-ant-...` kulcsot
5. Kattintson: **Add secret**

---

## 6. lépés – Első frissítés tesztelése

1. A repón: **Actions** fül
2. Bal oldal: **Civil Ház – Napi hírfrissítés**
3. Kattintson: **Run workflow** → **Run workflow**
4. Nézze meg a futást – kb. 2-3 perc
5. Ha sikeres: ✅ zöld pipa jelenik meg

---

## 7. lépés – Saját domain bekötése (opcionális)

Ha van saját domain (pl. `civilhazveszprem.hu`):

1. **Settings** → **Pages** → **Custom domain**
2. Írja be: `civilhazveszprem.hu`
3. A domain regisztrátornál adjon hozzá CNAME rekordot:
   ```
   www  →  FELHASZNÁLÓNÉV.github.io
   ```
4. Pipálja be: **Enforce HTTPS**

---

## Napi működés (automatikus, gép nélkül)

```
Minden nap 07:00 CET
        ↓
GitHub szerver elindul
        ↓
Python szkript lefut
        ↓
Claude API keres civil híreket
        ↓
aktualis.html + index.html frissül
        ↓
Változás automatikusan megjelenik a weboldalon
```

**Költség:** Az Anthropic API 1 napi futtatás ≈ 0,01–0,05 USD (havonta ~0,3–1,5 USD)

---

## Hibaelhárítás

| Probléma | Megoldás |
|----------|----------|
| Actions nem fut | Settings → Actions → Allow all actions |
| API hiba | Ellenőrizze a Secret nevét: pontosan `ANTHROPIC_API_KEY` |
| Oldal nem jelenik meg | Pages → Source: main branch, / (root) mappa |
| HTML nem frissül | Actions logban ellenőrizze a hibát |
