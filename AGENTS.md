# Wymarzone zestawy LEGO (lego-wybor)

Strona, na której Jaś (8 lat) i Antek (6 lat) zawężają listy wymarzonych zestawów LEGO.
Wdrażana przez Cloudflare Workers (Workers Builds podpięte do tego prywatnego repozytorium): każdy push na `main` jest na żywo po ok. 30 s.
Adres: https://lego.mariollo.com (custom domain w `wrangler.jsonc`; zapasowo https://lego-wybor.mariollo.workers.dev).
Ta sama strona działa też jako artefakt na claude.ai: https://claude.ai/artifact/VnzeDL4yzZvFZL8sYbuzbA

## Pliki

- `page/template.html` – źródło strony (HTML, CSS, JS). Tu wprowadzaj zmiany.
- `page/data.json` – dane zestawów (nazwy PL, seria, wiek, liczba elementów) i listy `lists`: `gazetka-jas`, `gazetka-antek`
  (gazetka lipiec–grudzień 2026) oraz `rok-2026` – wszystkie zestawy z 2026 bez Duplo (471; źródło: Rebrickable CSV + Brickset;
  bez gadżetów, książek, minifigurek kolekcjonerskich, promocyjnych, edukacyjnych, BrickLink Designer Program, saszetek 30xxx,
  pakietów 66xxx i 6-cyfrowych dodatków). Nazwy bez potwierdzenia mają `nameCheck`.
- `page/catalog.json` – katalog ~2200 zestawów 2022–2026 do opcji „Dodaj zestaw po numerze”.
- `page/img/<numer>.jpg` – zdjęcia pudełek (z BrickLink, `img.bricklink.com/ItemImage/ON/0/<numer>-1.png`, zmniejszone do 520 px), osadzane w stronie – rodzic chce jedno zdjęcie, z pudełkiem.
- `page/img-zestaw/<numer>.jpg` – zdjęcia samych zestawów (z Brickset); używane tylko, gdy brak zdjęcia pudełka.
- `build.py` – składa `public/index.html` (Cloudflare) i `build/artifact.html` (claude.ai). Uruchom po każdej zmianie w `page/`.
- `public/index.html` – gotowa strona (generowana, ale commitowana, bo Workers Builds nie ma kroku build).
- `public/img/<numer>.jpg` – zdjęcia kopiowane przez `build.py` (strona www ładuje je leniwie; plik strony < 25 MB).
  Wersja claude.ai ma zdjęcia osadzone tylko dla list z gazetki (limit 16 MB); zestawy z `rok-2026` są tam bez zdjęć.
- `public/_headers` – nagłówki (noindex; strona no-cache, zdjęcia cache 30 dni).
- `src/worker.js` – Worker: serwuje `public/` i API `/api/state/{jas|antek|settings|hist-jas|hist-antek}` (GET/PUT).
- `wrangler.jsonc` – konfiguracja Cloudflare; Durable Object `FamilyStore` (SQLite, darmowy plan).

## Zapis postępu

- Każde dziecko ma osobny dokument (`jas`, `antek`) plus `settings`. Wybory jednego dziecka nie wpływają na drugie.
- Na Cloudflare dostęp do danych daje **kod rodzinny** wysyłany w nagłówku `x-family-code`. Worker porównuje go z sekretem
  `FAMILY_CODE` ustawionym w Cloudflare (Settings → Variables and Secrets, typ Secret). Kodu nie zapisujemy w repozytorium (repo jest publiczne).
  Zły kod = odpowiedź 401 i komunikat na stronie. Cały postęp jest w jednym Durable Object (`family`), więc zmiana kodu nie kasuje danych.
- Link dla nowego urządzenia: `https://<adres>/#kod=<kod>` – kod zapisuje się w przeglądarce i znika z paska adresu.
- Urządzenia odpytują serwer co 4 s; ostatni zapis wygrywa.
- Jaś i Antek mogą grać jednocześnie na dwóch urządzeniach: każde urządzenie zapisuje tylko dokument grającego dziecka,
  a zmiana u jednego dziecka nie odświeża ekranu gry drugiego. To samo dziecko na dwóch urządzeniach naraz = wygrywa późniejszy zapis.
- Na claude.ai strona używa bazy artefaktu (`window.claude.use("db")`), bez kodu.

## Listy

- Każda rozgrywka pamięta listę (`list` w stanie dziecka). Zapis bez pola `list` = gra sprzed wyboru list → `gazetka-<dziecko>`.
- Nowa gra („Zagraj od nowa” albo wyczyszczenie w panelu) zaczyna się ekranem wyboru listy: Jaś – `gazetka-jas` / `rok-2026`,
  Antek – `gazetka-antek` / `rok-2026`. Przed resetem zakończona gra zapisuje do historii ranking Elo, jeśli go nie miała.

## Zasady selekcji (ustalone z rodzicem)

1. Przegląd: Super! / Może / Nie.
2. Pojedynki 1 na 1: Super zaczyna z 3 serduszkami, Może z 2; przegrana = −1 serduszko; rywale dobierani wg wyniku;
   „druga szansa” dla zestawu, który przegrał tylko z finalistami; ręczne „Jeszcze raz” w tabeli.
3. Wielki finał: każdy z każdym, dwa razy (runda 1 + rewanż ze zamienionymi stronami); remis („Tak samo”) = 0,5.
   Bez podpowiedzi przy zestawach: żadnych serii wygranych ani serduszek na kartach i w tabeli (dzieci nie chciały głosować przeciw
   zestawowi z ostatnim serduszkiem). Serduszka działają w silniku, ale dzieci ich nie widzą.
   Strony kart są losowane (powtarzalnie, z numerów zestawów i numeru pojedynku), także w drugiej szansie (pole `c` w dzienniku
   = zestaw walczący o powrót). W dzienniku `a` = lewa karta, `b` = prawa. Panel rodzica pokazuje, jak często wygrywa lewa.
4. Lista marzeń z możliwością poprawienia kolejności.

Wersje zasad (`rules` w stanie dziecka, zapisywane z rozgrywką – zmiana zasad nie może zmienić gry w toku):
- `rules: 1` (zapis bez pola `rules` = gra sprzed zmiany): przycisk „Nie umiem wybrać”, druga szansa dla zestawu, który przegrał tylko z finalistami.
- `rules: 2` (każda nowa rozgrywka, od 2026-11-03): „🤝 Oba super” (para wraca później) i „🙅 Żaden” (`x:"none"` w dzienniku, oba tracą serduszko);
  druga szansa dla maks. 2 najwyżej ocenianych w Elo odpadniętych zestawów, o ile mają Elo wyższe od najsłabszego finalisty
  (Elo liczone tylko z pojedynków przed finałem). Przed zmianą silnika porównaj wynik `engine()` dla prawdziwych zapisów przed i po zmianie.

Zakładka „Wszystkie zestawy” (dla rodzica): wszystkie zestawy z oznaczeniem listy (Jaś/Antek), bieżącą oceną, linkiem
`https://promoklocki.pl/<numer>` i rankingiem Elo liczonym z dziennika pojedynków (start 1500, K = 32, remis w finale = 0,5).
Elo jest wyłącznie informacyjne – nie wpływa na dobór par ani wynik.

Historia wyników: po „Gotowe ✓” na liście marzeń wynik (kolejność, „tuż za finałem”, statystyki) zapisuje się w `hist-jas` /
`hist-antek` (osobne dokumenty, jedna pozycja na rozgrywkę – `runId` w stanie dziecka; ponowne „Gotowe” aktualizuje wpis).
Wpis zawiera też ranking Elo top 10 z całej rozgrywki (`elo`; starsze wpisy bez Elo – liczone na bieżąco, jeśli to wciąż bieżąca gra dziecka).
Zakładka „🏆 Historia wyników” pokazuje wpisy, pozwala je usunąć i pobrać jako PNG (rysowany w canvas z danych; na claude.ai
pobieranie jest zablokowane, więc przycisku nie ma). „🔄 Zagraj od nowa” zeruje rozgrywkę dziecka (zostają zestawy dodane po numerze).

Numery zestawów z list źródłowych są nadrzędne. Podejrzane numery najpierw zweryfikuj (Brickset), nie poprawiaj ich automatycznie – zgłoś rodzicowi.

## Sprawdzenie przed pushem

1. `python3 build.py`
2. Utwórz `.dev.vars` (jest w .gitignore) z linią `FAMILY_CODE=TEST1234`, uruchom `npx wrangler dev` i otwórz http://localhost:8787/#kod=TEST1234.
3. Sprawdź telefon (420 px) i komputer, jasny i ciemny motyw, przegląd, pojedynek, finał, zapis między dwoma oknami.
4. Commit z jasnym opisem, potem push na `main`.
