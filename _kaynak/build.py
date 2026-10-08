"""Katalog verilerini birleştirir, doğrular ve tek dosyalık HTML uygulamasını üretir.
Kullanım: python build.py  ->  ../Pompa_Nozzle_Secici.html
"""
import json, os, io, base64, re
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
IMGS = os.path.join(HERE, 'imgs')
OUT = os.path.join(os.path.dirname(HERE), 'Pompa_Nozzle_Secici.html')

def load(name):
    with open(os.path.join(DATA, name), encoding='utf-8') as f:
        return json.load(f)

warnings = []
pumps = []
for p in load('lowara.json'):
    pumps.append(p)
for part in 'ABCD':
    for p in load(f'kres_{part}.json'):
        p['brand'] = 'Kresmak'
        p['source'] = 'Kresmak temmuz.pdf'
        pumps.append(p)

clean = []
for i, p in enumerate(pumps):
    q, h = [float(x) for x in p['q']], [float(x) for x in p['h']]
    if len(q) != len(h):
        warnings.append(f"atlandı (uzunluk): {p['model']}"); continue
    pts = sorted(zip(q, h))
    # tek nokta çöküşü (katalog dizgi hatası): komşularından belirgin düşük ve sonraki noktadan küçük
    changed = True
    while changed and len(pts) > 3:
        changed = False
        for k in range(1, len(pts) - 1):
            if pts[k][1] < pts[k + 1][1] - 0.5 and pts[k][1] < pts[k - 1][1]:
                warnings.append(f"aykırı nokta çıkarıldı: {p['model']} Q={pts[k][0]} H={pts[k][1]}")
                pts.pop(k); changed = True; break
    # katalogda doğrulanmış dizgi hataları (sayfa görüntüsüyle kontrol edildi)
    for model, qbad in (('WQ 65-5.5T', 22.0), ('KBZ 28-33.7T', 30.0)):
        if p['model'] == model:
            pts = [pt for pt in pts if pt[0] != qbad]
            warnings.append(f"dizgi hatası noktası çıkarıldı: {model} Q={qbad}")
    if len(pts) < 2:
        warnings.append(f"atlandı (nokta yok): {p['model']}"); continue
    p['q'] = [a for a, _ in pts]; p['h'] = [b for _, b in pts]
    p['id'] = f"P{i}"
    clean.append(p)
pumps = clean

noz = []
for n in load('flatfan.json'):
    noz.append(n)
for n in load('fullcone.json'):
    m = dict(n)
    for k_in, k_mm in (('orifice_in', 'orifice_mm'), ('free_passage_in', 'free_passage_mm')):
        v = m.pop(k_in, None)
        m[k_mm] = round(v * 25.4, 2) if isinstance(v, (int, float)) else None
    m['source'] = '05_Full_Cone_Nozzles 490.pdf'
    m['kind'] = m.get('kind') or 'Tam koni'
    pts = [pt for pt in (m.get('points') or []) if pt and pt[0] > 0 and pt[1] > 0]
    pts.sort()
    if m['code'] == '502.588':  # katalog hatası: 10/20 psi değerleri tutarsız
        pts = []
    else:  # gpm değerlerinin 2 hane yuvarlamasından doğan geri düşen noktaları at
        mono = []
        for pt in pts:
            if not mono or pt[1] > mono[-1][1]:
                mono.append(pt)
        pts = mono
    m['points'] = pts
    if pts:
        m['p_range'] = [min(a for a, _ in pts), max(a for a, _ in pts)]
    noz.append(m)
for i, n in enumerate(noz):
    n['id'] = f"N{i}"
    n.pop('q2bar_note', None)

# ---- görseller ----
used = sorted({x.get('image') for x in pumps + noz if x.get('image')})
images = {}
for name in used:
    path = os.path.join(IMGS, name)
    if not os.path.exists(path):
        warnings.append(f"görsel yok: {name}"); continue
    im = Image.open(path)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, 'white'); bg.paste(im, mask=im.split()[-1]); im = bg
    else:
        im = im.convert('RGB')
    im.thumbnail((300, 300))
    buf = io.BytesIO(); im.save(buf, 'JPEG', quality=78, optimize=True)
    images[name] = 'data:image/jpeg;base64,' + base64.b64encode(buf.getvalue()).decode()
for x in pumps + noz:
    if x.get('image') and x['image'] not in images:
        x['image'] = None

src = open(os.path.join(HERE, 'app_src.html'), encoding='utf-8').read()
dump = lambda o: json.dumps(o, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
src = src.replace('/*__PUMPS__*/[]', dump(pumps)).replace('/*__NOZZLES__*/[]', dump(noz)).replace('/*__IMAGES__*/{}', dump(images))
with open(OUT, 'w', encoding='utf-8') as f:
    f.write(src)

print(f"pompa: {len(pumps)}  nozzle: {len(noz)}  görsel: {len(images)}  boyut: {os.path.getsize(OUT)/1024:.0f} KB")
print('\n'.join(warnings))
