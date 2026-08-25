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
| Notlar & Görev listesi | ✅ (yeni) |
| Aralıklı tekrar / tekrar takibi | ❌ |
| Deneme sınavı net takibi | ❌ |
| Pomodoro / odak zamanlayıcı | ❌ |
| Konu/alt başlık tamamlama | ❌ |
| Streak (çalışma serisi) | ❌ |
| Yanlış soru / zayıf konu analizi | ❌ |
| Motivasyon / puan tahmini | ❌ |

---

## 🚨 Kritik Eksikler (Yüksek Öncelik)

### 1. 🔁 Tekrar Takip Sistemi — EN KRİTİK
> TUS'ta en sık sorulan şey: "Bu konuya kaçıncı tekrarı yaptım?"

**Problem:** Şu an sadece "okuduğum sayfalar" takip ediliyor. Ama **1. tekrar**, **2. tekrar**, **3. tekrar** kavramı yok. Bir kitabı 3 kez geçmek ile 1 kez geçmek aynı görünüyor.

**Ne olmalı:**
- Her kayıta "kaçıncı tekrar?" bilgisi eklenmeli (1/2/3/4)
- Bir kitabın kaç kez geçildiği görünmeli
- Konu bazlı "Bu konuya ne zaman baktım, ne zaman bakmam gerekiyor?" takibi
- Aralıklı tekrar takvimi: Konuyu bitirince → 3 gün sonra tekrar, 7 gün sonra tekrar gibi otomatik hatırlatma

```
Örnek görünüm:
Patoloji Bölüm 1 - İnflamasyon
✅ 1. Tekrar: 12 Ağu | ✅ 2. Tekrar: 16 Ağu | ⏰ 3. Tekrar: 23 Ağu (BUGÜN!)
```

---

### 2. 📝 Deneme Sınavı Net Takibi
> TUS'çuların haftalık denemeleri var, bunun gittiği yer yok.

**Problem:** Şu an "kaç sayfa okuduk" var ama "denemede kaç net yaptık" yok.

**Ne olmalı:**
- "Deneme Ekle" butonu → Tarih, hangi deneme, branş bazlı D/Y/B (doğru/yanlış/boş)
- Net = D - (Y/4) formülü otomatik hesaplansın
- Branş bazlı trend grafiği: "Fizyolojim her denemede artıyor, Patolojim düşüyor"
- TUS puan tahmini (T puanı / K puanı yaklaşık hesabı)

---

### 3. ⏱️ Pomodoro / Odak Zamanlayıcı
> TUS'çular genellikle 25-50 dakika odak, 10 dakika mola döngüsüyle çalışır.

**Problem:** Şu an "kaç sayfa" var ama "kaç dakika çalıştım" takip edilmiyor. Sayfa hızlı okunabilir ama verimli mi? Belli değil.

**Ne olmalı:**
- Dashboard'da veya ayrı sekmede Pomodoro timer
- 25/50 dakika ayarlanabilir odak süresi
- "Bugün X pomodoro tamamladın" istatistiği
- Günlük toplam çalışma süresi

---

## ⚠️ Orta Öncelikli İyileştirmeler

### 4. 📚 Konu/Alt Başlık Takibi
**Problem:** Şu an sadece "Patoloji - 50 sayfa" gibi genel giriş var. Ama "Patoloji → Hücre Hasarı → Apoptozis" gibi alt konu bazında "bitti/yarısı/okunmadı" takibi yok.

**Ne olmalı:**
- Her kitaba alt konular eklenebilsin (Bölüm 1, Bölüm 2...)
- Her bölüm için tamamlanma durumu: `⬜ Okunmadı → 🟡 Okunuyor → ✅ Tamam → 🔁 Tekrarda`
- Bölüm bazlı ilerleme çubuğu

---

### 5. 🔥 Streak (Çalışma Serisi) Sistemi
**Problem:** "Bu ay 18 gün çalıştım ama 5 gün boş geçirdim" bilgisi yok.

**Ne olmalı:**
- Streak takvimi: Her gün çalışıldı mı? (GitHub contribution graph gibi)
- Mevcut streak sayısı: "🔥 12 günlük seri!"
- En uzun streak rekoru
- Streak kırılma uyarısı

---

### 6. ❌ Yanlış Soru Defteri
**Problem:** TUS'ta kritik olan "yanlış yaptığın soruyu anlamak". Bunu kaydetmek için yer yok.

**Ne olmalı:**
- Notlar sayfasına "Yanlış Soru" tag'i veya ayrı mini-bölüm
- Branş, konu, neden yanlış (bilmiyorum / yorumladım / dikkat hatası) bilgisi
- Tekrar edilmesi gereken soruların hatırlatması

---

### 7. 📊 Hedef vs. Gerçek Analizi
**Problem:** Dashboard'da hedef hesaplanıyor ama "ne kadar geride/ilerideyim?" çok net değil.

**Ne olmalı:**
- Dashboard'a belirgin "Programa göre +X sayfa iledesin ✅" veya "-X sayfa gerideysin 🔴"
- Bugün çalışılması gereken sayfa sayısı büyük ve net gösterilsin
- Kalan sürede hedefi yakalamak için günlük sayfa önerisi

---

## 💡 Düşük Öncelik / Nice-to-Have

### 8. 🗂️ Çalışma Programı / Plan Oluşturucu
- "TUS'a 580 gün kaldı, 24 kitap var → günde X sayfa okumalısın" otomatik plan
- Branş sıralaması önerisi (Temel önce, Klinik sonra)

### 9. 🎯 Önceki TUS Sınav Yüzdelikleri Referansı
- "380 net ile kaçıncı yüzdelik?" gibi bir referans tablo
- Hedef branş için gerekli net tahmini

### 10. 🌙 Dark Mode Renk Temaları
- Şu an tek tema var. "Daha fazla mavi ışık azaltma" veya OLED siyah tema seçeneği

### 11. 📱 Mobil Uyumluluk İyileştirme
- Şu an masaüstü odaklı. Telefondan kullanım (ders arası, tuvalet molası 😄) için responsive iyileştirme

### 12. 🔔 Hatırlatıcılar
- "Bugün Patoloji tekrarı yapman gerek!" bildirim sistemi (tarayıcı notification)
- Tekrar günleri yaklaşınca otomatik hatırlatma

---

## 📊 Öncelik Özeti

```
🚨 Kritik (Oyunu değiştirir):
  1. Tekrar Takibi (1./2./3. tekrar sistemi)
  2. Deneme Sınavı Net Takibi
  3. Pomodoro Timer

⚠️ Önemli (Çok faydalı):
  4. Konu/Alt Başlık Takibi
  5. Streak Sistemi
  6. Yanlış Soru Defteri
  7. Hedef vs. Gerçek analizi belirginleştirme

💡 Bonus:
  8. Plan oluşturucu
  9. Yüzdelik referans
  10. Tema seçimi
  11. Mobil iyileştirme
  12. Bildirimler
```

---

> *"TUS'çu için en önemli şey: neyi bildiğini değil, neyi bilmediğini bilmek."*
