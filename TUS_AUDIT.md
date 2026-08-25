# 🩺 TUS Takip — Kapsamlı Audit Raporu

> **Araştırma bazlı:** TUS pedagojisi, aralıklı tekrar sistemi, ve mevcut TUS uygulamaları (TusMapp, TusAI, TUSCoach) incelenerek hazırlanmıştır.

---

## 🧠 TUS'a Nasıl Çalışılır? (Kısa Özet)

TUS, ~25 branş × yüzlerce konu içeren devasa bir müfredattır. Başarı 3 prensibe dayanır:

| Prensip | Açıklama |
|---|---|
| **Aktif Geri Çağırma** | Okumak değil, hatırlamaya çalışmak (soru, flashcard, kendi kendine anlatma) |
| **Aralıklı Tekrar** | 1-3-7-14-30 gün kuralı — bilgi tam unutulmak üzereyken tekrar |
| **Soru Merkezli Çalışma** | "Konu bitti mi?" değil, "Bu konudan net kaçım var?" sorusu |

---

## 🔍 Mevcut TUS Takip Özellikleri

| Özellik | Durum |
|---|---|
| Günlük sayfa girişi | ✅ |
| Kitap bazlı ilerleme | ✅ |
| Dashboard istatistikleri | ✅ |
| Haftalık rapor | ✅ |
| 2027 TUS gün sayacı | ✅ |
| Firebase senkronizasyon | ✅ |
| Notlar & Görev listesi | ✅ |
| Dashboard açılır-kapanır paneller | ✅ |
| Streak sayısı | ✅ |
| Aralıklı tekrar / tekrar takibi (1./2./3. tekrar) | ❌ |
| Deneme sınavı net takibi & analizi | ❌ |
| Konu/alt başlık tamamlama | ❌ |
| Yanlış soru / zayıf konu analizi | ❌ |
| TUS puanı / net tahmini | ❌ |

---

## 🚨 Kritik Eksikler (Yüksek Öncelik)

### 1. 🔁 Tekrar Takip Sistemi (1. / 2. / 3. Tekrar) — EN KRİTİK
> TUS'ta en sık sorulan soru: "Bu kitabı/konuyu kaçıncı kez dönüyorum?"

**Problem:** Şu an sadece "okunan sayfa sayısı" toplanıyor. Ancak TUS pedagojisinde bir kitabı ilk kez okumak (1. tur) ile hızlı pekiştirme (2. veya 3. tekrar) çok farklıdır. Kaçıncı tekrarda olunduğu bilinmeden genel hazırlık seviyesi ölçülemez.

**Ne olmalı:**
- Kayıt eklerken veya kitap bazında "Tekrar No" (1. Tur / 2. Tekrar / 3. Tekrar vb.) seçilebilmeli.
- Kitap bazında kaçıncı tekrarın hangi tarihte bittiği gösterilmeli.
- Konu bazlı aralıklı tekrar (Spaced Repetition) takvimi: Bir konu bitince 3. gün, 7. gün ve 21. gün için otomatik tekrar hatırlatıcısı.

```
Örnek görünüm:
Patoloji: 1. Tur (Tamamlandı - 12 Ağu) ➔ 2. Tekrar (%45 - Devam ediyor)
```

---

### 2. 📝 Deneme Sınavı Net Takibi & Trend Analizi
> TUS başarısının gerçek pusulası deneme netleridir.

**Problem:** Sadece sayfa takibi yapmak, çalışmanın soruya yansıyıp yansımadığını göstermez. Denemelerin takibi için şu an yer yok.

**Ne olmalı:**
- "Deneme Sınavı Ekle" modülü: Temel Tıp ve Klinik Tıp branşları için Doğru/Yanlış/Boş girişi.
- Otomatik Net Hesabı: `Net = Doğru - (Yanlış / 4)`.
- Branş bazlı başarı analizi (Örn: "Dahiliye netlerin yükselişte, Mikrobiyoloji düşüşte").
- Deneme net gelişim grafiği (zaman içindeki net artış eğrisi).
- Yaklaşık TUS Puanı / Sıralama projeksiyonu.

---

## ⚠️ Orta Öncelikli İyileştirmeler

### 3. 📚 Konu ve Alt Başlık Takibi (Checklist Mantığı)
**Problem:** Sadece "Patoloji - 50 sayfa" yazmak yerine hangi klinik/temel alt başlıkların tamamlandığı bilinmelidir.

**Ne olmalı:**
- Kitapların altına standart TUS konu başlıkları (örn: Biyokimya ➔ Enzimler, Lipid Metabolizması vb.) eklenebilmeli.
- Her konu için durum: `⬜ Çalışılmadı ➔ 🟡 Çalışılıyor ➔ ✅ 1. Tekrar Bitti ➔ 🔁 Tekrarda`.

---

### 4. ❌ Yanlış Soru / Spot Bilgi Defteri
**Problem:** TUS'ta en çok puan kazandıran yöntem, denemelerde ve soru bankalarında yapılan yanlışların analiz edilmesidir.

**Ne olmalı:**
- Yanlış yapılan soruların veya unutulan hap/spot bilgilerin branş bazlı hızlıca not alınabilmesi.
- Bu spot bilgilerin haftalık veya sınav öncesi hızlı gözden geçirme listesi olarak filtrelenebilmesi.

---

### 5. 📊 Hedef vs. Gerçek Analizi & Akıllı Planlama
**Problem:** Sınava kalan gün sayısı ile kalan sayfa/tur sayısı arasındaki günlük tempo dengesi yeterince vurgulanmıyor.

**Ne olmalı:**
- "Günde ortalama X sayfa okursan Mart 2027 sınavına kadar tüm dersleri Y tekrar ile bitirirsin" şeklinde akıllı tempo önerisi.
- Mevcut temponun hedef takvimin önünde mi yoksa gerisinde mi olduğunu gösteren net gösterge.

---

## 💡 Düşük Öncelik / Gelecek Fikirler

### 6. 📱 Gelişmiş Mobil Arayüz İyileştirmeleri
- Tıp fakültesi / hastane nöbet aralarında telefondan tek elle hızlı giriş yapabilmek için mobil odaklı optimizasyonlar.

### 7. 🔔 Tarayıcı Bildirimleri ve Hatırlatıcılar
- Planlanan görevler ve planlanan tekrar tarihleri için günlük tarayıcı hatırlatıcısı.

---

## 📊 Güncellenmiş Öncelik Tablosu

```
🚨 Kritik (İlk Yapılması Gerekenler):
  1. 🔁 Tekrar Takip Sistemi (1./2./3. Tekrar Turları)
  2. 📝 Deneme Sınavı Net Takibi & Branş Analizleri

⚠️ Önemli (Çalışma Kalitesini Katlayanlar):
  3. 📚 Konu / Alt Başlık Checklist Takibi
  4. ❌ Yanlış Soru & Spot Bilgi Defteri
  5. 📊 Hedef vs. Gerçek / Akıllı Günlük Tempo

💡 Tamamlayıcı:
  6. 📱 Mobil Deneyim İyileştirmeleri
  7. 🔔 Akıllı Tekrar Hatırlatıcıları
```

---

> *"TUS'çu için en önemli şey: neyi bildiğini değil, neyi unuttuğunu tespit edip tekrar etmektir."*
