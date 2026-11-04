"""Składa stronę z page/ do public/index.html (Cloudflare) i build/artifact.html (wersja na claude.ai).
Uruchom: python3 build.py"""
import base64, json, os
root = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(root, *a)
t = open(P('page', 'template.html'), encoding='utf-8').read()
# Zdjęcie na karcie: pudełko (page/img, z BrickLink); gdy go brak – zdjęcie zestawu (page/img-zestaw, z Brickset).
# Cloudflare: zdjęcia jako osobne pliki public/img/<numer>.jpg (strona < 25 MB, ładowanie przy przewijaniu).
# claude.ai: zdjęcia osadzone (data:), ale tylko dla list z gazetki – limit 16 MB.
import shutil
data = json.load(open(P('page', 'data.json'), encoding='utf-8'))
files = {}
for folder in ('img-zestaw', 'img'):
    for f in sorted(os.listdir(P('page', folder))):
        if f.endswith('.jpg'): files[f[:-4]] = P('page', folder, f)
os.makedirs(P('public', 'img'), exist_ok=True)
for f in os.listdir(P('public', 'img')):
    if f.endswith('.jpg') and f[:-4] not in files: os.remove(P('public', 'img', f))
for n, src in files.items(): shutil.copyfile(src, P('public', 'img', n + '.jpg'))
img_web = {n: 'img/' + n + '.jpg' for n in files}
small = set(data['lists']['gazetka-jas']['sets']) | set(data['lists']['gazetka-antek']['sets'])
img_art = {n: 'data:image/jpeg;base64,' + base64.b64encode(open(src, 'rb').read()).decode() for n, src in files.items() if n in small}
def fill(img):
    return (t.replace('__DATA__', open(P('page', 'data.json'), encoding='utf-8').read())
             .replace('__IMG__', json.dumps(img))
             .replace('__CATALOG__', open(P('page', 'catalog.json'), encoding='utf-8').read()))
os.makedirs(P('build'), exist_ok=True)
open(P('build', 'artifact.html'), 'w', encoding='utf-8').write(fill(img_art))
head = ('<!doctype html><html lang="pl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="robots" content="noindex,nofollow">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>')
open(P('public', 'index.html'), 'w', encoding='utf-8').write(head + fill(img_web) + '</body></html>')
print('public/index.html', os.path.getsize(P('public', 'index.html')) // 1024, 'KB |', len(files), 'zdjęć w public/img |',
      'artifact', os.path.getsize(P('build', 'artifact.html')) // 1024, 'KB')
