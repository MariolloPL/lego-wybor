"""Składa stronę z page/ do public/index.html (Cloudflare) i build/artifact.html (wersja na claude.ai).
Uruchom: python3 build.py"""
import base64, json, os
root = os.path.dirname(os.path.abspath(__file__))
P = lambda *a: os.path.join(root, *a)
t = open(P('page', 'template.html'), encoding='utf-8').read()
img = {f[:-4]: 'data:image/jpeg;base64,' + base64.b64encode(open(P('page', 'img', f), 'rb').read()).decode()
       for f in sorted(os.listdir(P('page', 'img'))) if f.endswith('.jpg')}
t = (t.replace('__DATA__', open(P('page', 'data.json'), encoding='utf-8').read())
      .replace('__IMG__', json.dumps(img))
      .replace('__CATALOG__', open(P('page', 'catalog.json'), encoding='utf-8').read()))
os.makedirs(P('build'), exist_ok=True)
open(P('build', 'artifact.html'), 'w', encoding='utf-8').write(t)
head = ('<!doctype html><html lang="pl"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
        '<meta name="robots" content="noindex,nofollow">'
        '<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style></head><body>')
open(P('public', 'index.html'), 'w', encoding='utf-8').write(head + t + '</body></html>')
print('public/index.html', os.path.getsize(P('public', 'index.html')) // 1024, 'KB')
