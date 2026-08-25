# TUS Takip — Kullanım Rehberi 📚

## 🌐 Canlı Site
**https://canberkbagana-tr.github.io/tustakip/**

---

## ⚠️ Firebase 30 Gün Sonra Yapılacak İşlem

Firebase'i "test mode"da açtın. **7 Mayıs 2026** civarında süresi dolacak ve veriler senkronize olmayı durduracak.

### Çözüm (2 dakika):
1. https://console.firebase.google.com adresine git
2. Sol menüden **Build → Realtime Database** tıkla
3. Üstten **Rules** sekmesine geç
4. Mevcut kuralları sil, yerine şunu yapıştır:

```json
{
  "rules": {
    ".read": true,
    ".write": true
  }
}
```

5. **Publish** butonuna bas → Bitti! ✅

> ⚡ Bu kural herkese okuma/yazma izni verir. Bu uygulama için yeterli çünkü hassas veri yok. Daha güvenli istersen ileride authentication eklenebilir.

---

## 📱 Uygulama Özellikleri

| Sekme | Açıklama |
|-------|----------|
| 📊 Dashboard | 2027 Mart TUS geri sayımı, genel ilerleme, kitap bazlı progress, hızlı kayıt ekleme |
| 📚 Kitaplar | Kitap ekle/sil, 20 renk seçeneği, sayfa sayısı belirle |
| 📝 Kayıtlar | Tüm kayıtlar, filtreleme (kitap/ay/gün tipi) |
| 📅 Haftalık | Bu haftanın raporu, gün gün detay, kitap dağılımı |
| 📈 İstatistikler | 30 günlük grafik, aylık özet, doughnut chart, streak, senaryolar |
| ⚙️ Ayarlar | Hedef sınav tarihi, tekrar payı, hedef, nöbet/tatil günleri, veri yönetimi |

---

## 🔄 Senkronizasyon Nasıl Çalışıyor?

- İlay → veri girer → **Firebase'e otomatik yazılır**
- Sen → sayfayı açarsın → **Firebase'den otomatik yüklenir**
- Her **30 saniyede** otomatik güncelleme
- Tab'a **geri döndüğünde** anında güncelleme
- Üst barda: 🟢 Senkron / 🔴 Çevrimdışı göstergesi
- Ayarlarda **"🔄 Firebase Senkronize Et"** butonu ile manuel senkronizasyon

---

## 🗂️ Veri Yedekleme

Ayarlar → Veri Yönetimi:
- **📤 Dışa Aktar** → JSON dosyası indirir
- **📥 İçe Aktar** → JSON dosyasından geri yükler
- **🗑️ Tüm Verileri Sil** → Sıfırdan başlar

---

## 💻 Teknik Bilgiler

| Bileşen | Teknoloji |
|---------|-----------|
| Frontend | HTML + CSS + Vanilla JS |
| Hosting | GitHub Pages (ücretsiz) |
| Veritabanı | Firebase Realtime Database (ücretsiz) |
| Grafik | Chart.js (CDN) |
| Veri | localStorage + Firebase REST API |

### Proje Dosyaları
```
ilaytus/
├── index.html          ← Ana sayfa (SPA)
├── style.css           ← Koyu tema + responsive tasarım
├── app.js              ← Uygulama mantığı
├── firebase-sync.js    ← Firebase senkronizasyon modülü
├── README.md           ← Proje açıklaması
└── REHBER.md           ← Bu dosya
```

### Firebase Bilgileri
- **Proje:** tustakip
- **DB URL:** https://tustakip-default-rtdb.europe-west1.firebasedatabase.app
- **Console:** https://console.firebase.google.com/project/tustakip

### GitHub Bilgileri
- **Repo:** https://github.com/canberkbagana-tr/tustakip
- **Site:** https://canberkbagana-tr.github.io/tustakip/

---

## 🚀 Kod Değişikliği Nasıl Yayınlanır?

```bash
cd c:\Users\canbe\Downloads\ilaytus
git add -A
git commit -m "açıklama yaz"
git push
```
Birkaç dakika sonra site güncellenir.





🏅 3. Başarı Rozetleri (Milestones)
📖 İlk 100 sayfa!
🔥 7 gün streak!
📚 İlk kitap %50 tamamlandı!
🏆 1000 sayfa okudun!
Küçük konfeti animasyonu ile kutlama — çalışmayı oyunlaştırır.

Bence en çok farkı PWA yaratır çünkü İlay her gün telefondan açacak ve "uygulama gibi" hissetmesi çok önemli. Günlük hedef göstergesi de 5 dakikalık iş, onu da yanına eklerim.

Hangilerini istiyorsun? Hepsini mi, PWA + hedef mi?

başarı rozetlerini istiyorum telefonlarımız apple oldugundan zor olur ayrıca benimde kenara not yazabileceğim bir alan olsun böyle şirin tatlı ekranın sağ tarafında boşluklarda veya solda 