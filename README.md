# Pompa & Nozzle Seçici

Boru hattı, nozzle ve hedef basınca göre pompa çalışma noktasını hesaplayan, en uygun pompa ve nozzle'ları sıralayan tek dosyalık bir uygulama.

**Kullanım:** `Pompa_Nozzle_Secici.html` dosyasını çift tıklayarak tarayıcıda açın. Kurulum gerekmez; tüm veriler ve fotoğraflar dosyanın içindedir.

## Ekranlar

- **Sistem Analizi:** Seçilen pompa, nozzle ve boru hattıyla gerçek debi ve basınç (pompa eğrisi ile sistem eğrisinin kesişimi).
- **Pompa Seçimi:** Hedef nozzle basıncına göre pompaları performans, fiyat veya fiyat/performans sırasıyla listeler.
- **Pompa + Nozzle:** Yalnızca hedef basınçtan en uygun pompa–nozzle kombinasyonlarını bulur.
- **Katalog:** Tüm pompa ve nozzle'lar, eğrileri ve teknik verileriyle.
- **Hesap Yöntemi** ve **Nasıl Kullanılır** sayfaları.

## Veri kaynakları

| Dosya | İçerik |
|---|---|
| `eSH_50Hz_EN.pdf` | Lowara e-SH santrifüj pompalar (115 model) |
| `Kresmak temmuz.pdf` | Kresmak / Atlantis blu fiyat listesi (467 model) |
| `05_Full_Cone_Nozzles 490.pdf` | Lechler tam koni nozzle'lar |
| `lechler_flat_fan_nozzles_series_632_633.pdf`, `Series_650_651.pdf`, `Series_602_608_652_FlatFan.pdf` | Lechler düz fan nozzle'lar |

## Yeniden derleme

Uygulamanın kaynağı `_kaynak/` klasöründedir:

- `app_src.html`: arayüz ve hesap kodu (şablon)
- `data/*.json`: kataloglardan okunan pompa ve nozzle verileri
- `imgs/`: ürün fotoğrafları
- `build.py`: verileri ve fotoğrafları şablona gömüp `Pompa_Nozzle_Secici.html` dosyasını üretir
- `render_imgs.py`: ürün fotoğraflarını PDF sayfalarından yeniden üretir
- `build_base.py`, `pumps_raw.txt`: Lowara ve Lechler düz fan verilerinin ham hali

```
cd _kaynak
python render_imgs.py   # yalnızca fotoğraflar yeniden üretilecekse (pymupdf gerekir)
python build.py         # Pillow gerekir
```

> Değerler taranmış kataloglardan okunmuştur. Kritik bir seçimden önce uygulamadaki detay penceresinde yazan kaynak sayfa ile karşılaştırın.
