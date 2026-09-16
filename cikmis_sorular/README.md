# 📚 TUS Virtual Soru Tabanı (Virtual Question Bank) & PDF Havuzu

Bu klasör, sisteme aktarılacak TUS çıkmış soru kitapçıkları (`.pdf`) ve bu kitaplardan **akıllı ayıklama boru hattı (extraction pipeline)** ile üretilen **kitap bazlı hafif yapay JSON** dosyalarının merkezidir.

---

## ⚠️ ALTIN KURAL: Soru Olmayan Kısımları Kesmeme (Zero Non-Question Crop)

PDF kitaplarında sıkça karşılaşılan ve **KESİNLİKLE SORU TABANINA DAHİL EDİLMEYECEK** unsurlar:
1. 🚫 **Telif ve Yasal Uyarı Metinleri:** ("Telif hukuku", "kul hakkı", "yasal olmayan yollarla", "fotokopi" gibi uyarılar).
2. 🚫 **Bölüm Kapakları ve İçindekiler Sayfaları:** Ünite girişleri, konu listeleri, yazar bilgileri.
3. 🚫 **Salt Teori / Konu Anlatımı Paragrafları:** Dahiliye veya Patoloji gibi kitaplarda sorular metinlerin arasına serpiştirilmiştir; aradaki özet tablolar, spot bilgiler ve vaka anlatımları **kırpılmaz veya soru yapılmaz**.
4. 🚫 **Körlemesine Sayfa PNG Kırpmak:** Bütün sayfayı veya rastgele kutuları PNG olarak kesmek hem disk alanını şişirir hem de hatalı soru üretir.

---

## 🔬 Akıllı Soru Doğrulama Filtresi (4 Kural)

Bir metin bloğunun soru tabanına girebilmesi için şu **4 şartı birden** eksiksiz taşıması zorunludur:
1. **Soru Numarası & Sınav Dönemi:** `1.`, `2.` gibi numarayla başlamalı ve tercihen `(Nisan 2001)`, `(Eylül 1999)` gibi TUS dönemini belirtmelidir.
2. **A-E Şık Bütünlüğü:** `A)`, `B)`, `C)`, `D)`, `E)` şıklarının tamamı bulunmalıdır. Şıksız metinler derhal elenir.
3. **Cevap Anahtarı:** `Doğru cevap: C` veya `Cevap: C` ibaresi tespit edilmelidir.
4. **TUS Klinik Püf Noktası (Açıklama):** Doğru cevabın altındaki çözüm ve klinik not ayrıştırılmalıdır.

---

## 🗄️ Klasör Yapısı ve Kitap Bazlı Yapay JSON Mimarisi

```
cikmis_sorular/
├── Fizyoloji.pdf                     <- Kaynak PDF (Gitignore'da, sunucuyu yormaz)
├── README.md                         <- Bu rehber
├── virtual_db/                       <- SANAL SORU TABANI (JSON DEPOSU)
│   ├── question_bank_manifest.json   <- 13 TUS dersinin merkezi soru sayacı ve konu dağılımı
│   ├── questions_fizyoloji.json      <- Fizyoloji çıkmış soru bankası (~6 KB)
│   ├── questions_patoloji.json       <- Patoloji çıkmış soru bankası
│   ├── questions_dahiliye.json       <- Dahiliye çıkmış soru bankası
│   └── ... (diğer 13 TUS branşı)
```

### 💡 Neden Yapay JSON?
- **Sıfır Görsel Maliyeti:** 100 soru sadece **~35 KB** yer tutar. 5.000 soru dahi **3-4 MB** tutar.
- **Firebase ve Kota Dostu:** Ne disk şişer ne de internet kotası harcanır.
- **Görsel İstisnası:** YALNIZCA soruda gerçek bir klinik tanı görseli (EKG dalgası, histopatoloji mikroskop görüntüsü, BT/MR kesiti) varsa o spesifik görsel alanı WebP olarak kırpılıp JSON'a bağlanır.
