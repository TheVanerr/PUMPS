"""Uygulamada kullanılan ürün fotoğraflarını PDF sayfasından, görselin kendi alanı kırpılarak render eder.
Ham görsel akışını çıkarmak bazı dosyalarda (CMYK, maske, ters satır düzeni) bozuk sonuç veriyordu;
sayfayı render etmek fotoğrafı katalogda göründüğü gibi verir.
Kullanım: python render_imgs.py   (build.py'den önce)
"""
import json, os, re, glob
import pymupdf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
IMGS = os.path.join(HERE, 'imgs')
PDFS = {'kres': 'Kresmak temmuz.pdf', 'fc': '05_Full_Cone_Nozzles 490.pdf', 'esh': 'eSH_50Hz_EN.pdf',
        's650': 'Series_650_651.pdf', 's602': 'Series_602_608_652_FlatFan.pdf',
        's632': 'lechler_flat_fan_nozzles_series_632_633.pdf'}

used = set()
for f in glob.glob(os.path.join(HERE, 'data', '*.json')):
    for x in json.load(open(f, encoding='utf-8')):
        if x.get('image'):
            used.add(x['image'])

docs = {}
ok = bad = 0
for name in sorted(used):
    m = re.match(r'(\w+?)_p(\d+)_x(\d+)\.png$', name)
    if not m:
        print('ad çözülemedi:', name); bad += 1; continue
    tag, page, xref = m.group(1), int(m.group(2)), int(m.group(3))
    d = docs.get(tag) or docs.setdefault(tag, pymupdf.open(os.path.join(ROOT, PDFS[tag])))
    pg = d[page - 1]
    rects = pg.get_image_rects(xref)
    if not rects:
        print('alan bulunamadı:', name); bad += 1; continue
    r = rects[0] & pg.rect
    # kırpma çerçevesi sayfa dışına taşmasın; çok büyük görsellerde çözünürlüğü sınırla
    dpi = max(96, min(220, int(420 / max(r.width, 1) * 72)))
    pg.get_pixmap(clip=r, dpi=dpi, alpha=False).save(os.path.join(IMGS, name))
    ok += 1
print(f'render edildi: {ok}  hata: {bad}')
