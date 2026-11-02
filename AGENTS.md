# Wymarzone zestawy LEGO (lego-wybor)

Strona, na której Jaś (8 lat) i Antek (6 lat) zawężają listy wymarzonych zestawów LEGO.
Wdrażana przez Cloudflare Workers (Workers Builds podpięte do tego prywatnego repozytorium): każdy push na `main` jest na żywo po ok. 30 s.
Ta sama strona działa też jako artefakt na claude.ai: https://claude.ai/artifact/VnzeDL4yzZvFZL8sYbuzbA

## Pliki

- `page/template.html` – źródło strony (HTML, CSS, JS). Tu wprowadzaj zmiany.
- `page/data.json` – listy chłopców i dane zestawów (nazwy PL, seria, wiek, liczba elementów).
- `page/catalog.json` – katalog ~2200 zestawów 2022–2026 do opcji „Dodaj zestaw po numerze”.
- `page/img/<numer>.jpg` – zdjęcia zestawów (z Brickset, zmniejszone do 520 px), osadzane w stronie.
- `build.py` – składa `public/index.html` (Cloudflare) i `build/artifact.html` (claude.ai). Uruchom po każdej zmianie w `page/`.
- `public/index.html` – gotowa strona (generowana, ale commitowana, bo Workers Builds nie ma kroku build).
- `public/_headers` – nagłówki (noindex, no-cache).
- `src/worker.js` – Worker: serwuje `public/` i API `/api/state/{jas|antek|settings}` (GET/PUT).
- `wrangler.jsonc` – konfiguracja Cloudflare; Durable Object `FamilyStore` (SQLite, darmowy plan).

## Zapis postępu

- Każde dziecko ma osobny dokument (`jas`, `antek`) plus `settings`. Wybory jednego dziecka nie wpływają na drugie.
- Na Cloudflare dostęp do danych daje **kod rodzinny** wysyłany w nagłówku `x-family-code`. Worker porównuje go z sekretem
  `FAMILY_CODE` ustawionym w Cloudflare (Settings → Variables and Secrets, typ Secret). Kodu nie zapisujemy w repozytorium (repo jest publiczne).
  Zły kod = odpowiedź 401 i komunikat na stronie. Cały postęp jest w jednym Durable Object (`family`), więc zmiana kodu nie kasuje danych.
- Link dla nowego urządzenia: `https://<adres>/#kod=<kod>` – kod zapisuje się w przeglądarce i znika z paska adresu.
- Urządzenia odpytują serwer co 4 s; ostatni zapis wygrywa.
- Na claude.ai strona używa bazy artefaktu (`window.claude.use("db")`), bez kodu.

## Zasady selekcji (ustalone z rodzicem)

1. Przegląd: Super! / Może / Nie.
2. Pojedynki 1 na 1: Super zaczyna z 3 serduszkami, Może z 2; przegrana = −1 serduszko; rywale dobierani wg wyniku;
   „druga szansa” dla zestawu, który przegrał tylko z finalistami; ręczne „Jeszcze raz” w tabeli.
3. Wielki finał: każdy z każdym.
4. Lista marzeń z możliwością poprawienia kolejności.

Numery zestawów z list źródłowych są nadrzędne. Podejrzane numery najpierw zweryfikuj (Brickset), nie poprawiaj ich automatycznie – zgłoś rodzicowi.

## Sprawdzenie przed pushem

1. `python3 build.py`
2. Utwórz `.dev.vars` (jest w .gitignore) z linią `FAMILY_CODE=TEST1234`, uruchom `npx wrangler dev` i otwórz http://localhost:8787/#kod=TEST1234.
3. Sprawdź telefon (420 px) i komputer, jasny i ciemny motyw, przegląd, pojedynek, finał, zapis między dwoma oknami.
4. Commit z jasnym opisem, potem push na `main`.
