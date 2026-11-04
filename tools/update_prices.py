"""Odświeża ceny i status na lego.pl z Łowcy Klocków (lowcaklockow.pl/products/<numer>) w page/data.json.
Pobiera powoli (1 strona na sekundę). Potem: python build.py, commit, push.
Uruchom z katalogu repozytorium:  python tools/update_prices.py"""
import datetime, html, json, os, re, time, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH = os.path.join(ROOT, 'page', 'data.json')

def text(page):
    page = re.sub(r'<script.*?</script>|<style.*?</style>', '', page, flags=re.S)
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', page)))

def num(s):
    m = re.search(r'\d+(?:[.,]\d+)?', s or '')
    return float(m.group(0).replace(',', '.')) if m else None

def fetch(n):
    req = urllib.request.Request(f'https://lowcaklockow.pl/products/{n}', headers={'User-Agent': 'lego-wybor (rodzinna lista prezentow)'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'ignore')

def parse(n, page):
    body = text(page)
    g = lambda k: (re.search(re.escape(k) + r' (\S+)', body) or [None, None])[1]
    i = body.find('Zestawienie ofert'); j = body.find('Opis zestawu', i)
    sec = re.sub(r'Dostawa \d+[.,]\d{2} zł', '', body[i:j if j > 0 else None] if i >= 0 else '')
    offers = [float(x) for x in re.findall(r'LEGO ' + n + r' [^|]*?(\d+\.\d{2}) zł', sec)]
    st = re.search(r'Status na lego\.pl (.{0,30}?) (Cena katalogowa|Wycofanie|Liczba)', body)
    lk = {'st': st.group(1).strip() if st else None, 'rrp': num(g('Cena katalogowa')),
          'now': min(offers) if offers else None, 'low': num(g('Najniższa cena w historii'))}
    return {k: v for k, v in lk.items() if v is not None}

data = json.load(open(PATH, encoding='utf-8'))
nums = []
for L in data['lists'].values():
    for n in L['sets']:
        if n not in nums: nums.append(n)
sets = {s['n']: s for s in data['sets']}
ok = 0
for k, n in enumerate(nums, 1):
    try:
        lk = parse(n, fetch(n))
        if lk.get('rrp'): sets[n]['lk'] = lk; ok += 1
    except Exception as e:
        print('  pominięto', n, e)
    if k % 50 == 0: print(f'{k}/{len(nums)}')
    time.sleep(1)
data['priceDate'] = datetime.date.today().isoformat()
json.dump(data, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(f'Zaktualizowano ceny {ok} z {len(nums)} zestawów (data {data["priceDate"]}). Teraz: python build.py')
