# 📋 Değişiklik Günlüğü (Changelog)

Bu belgede **TUS Takip** projesinde yapılan tüm güncellemeler ve sürüm notları yer almaktadır.

---

## [v3.2.0] - 2026-08-25
### ✨ Yeni Özellikler
- **⏳ 2027 Mart TUS Sınav Geri Sayımı:** 
  - Dashboard istatistik kartları arasına 2027 Mart TUS için canlı gün sayacı eklendi.
  - Kalan gün sayısı ve saniye bazında canlı akan saat:dakika:saniye detayı entegre edildi.
  - Üst motivasyon barına pratik bir `🎯 Mart 2027 TUS: XXX gün` rozeti eklendi.
- **⚙️ Dinamik Sınav Tarihi Ayarı:**
  - Ayarlar sekmesine sınav tarihi seçici eklendi (Varsayılan: `2027-03-21`).
  - Tarih değiştirildiğinde Firebase bulut veritabanına kaydedilir ve tüm cihazlarla senkronize olur.
- **🗄️ JSON Yedekleme Güncellemesi:**
  - `current_firebase_data.json` dosyası en güncel Firebase verileri ile dolduruldu ve yedeklendi.

---

## [v3.1.0] - 2026-05-07
### ✨ Yeni Özellikler
- **💌 İlay'a Özel Not (Floating Note):**
  - Ekranın sağ alt köşesinde tatlı bir post-it / floating not kartı eklendi.
  - Ayarlar sayfasından not yazılabilir ve gizlenebilir, Firebase üzerinden anlık senkronize olur.

---

## [v3.0.0] - 2026-04-08
### ✨ Yeni Özellikler & İyileştirmeler
- **🔄 Firebase Realtime Database Senkronizasyonu:**
  - REST API tabanlı bulut senkronizasyonu (SDK gerektirmeden sıfır yük).
  - 30 saniyede bir otomatik ve sekme odaklandığında anlık eşitleme.
  - Üst barda yeşil/kırmızı senkronizasyon durum rozeti.
- **📅 Haftalık Rapor Sekmesi:**
  - Haftalık toplam çalışma, gün gün sayfa dağılımı ve kitap bazlı grafikler.
- **🎨 Genişletilmiş Renk Paleti:**
  - Kitaplar için 20 farklı renk seçeneği.

---

## [v1.0.0 - v2.0.0] - 2026-04
- 🚀 **İlk Canlı Sürüm:**
  - Kitap ekleme/silme ve sayfa takibi.
  - Günlük çalışma, nöbet ve tatil kaydı.
  - İlerleme çubukları, Chart.js grafikleri ve streak takibi.
  - Tahmini bitiş tarihi ve çalışma senaryoları.
  - JSON ile dışa/içe veri aktarımı.
