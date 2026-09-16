# 📋 Değişiklik Günlüğü (Changelog)

Bu belgede **TUS Takip** projesinde yapılan tüm güncellemeler ve sürüm notları yer almaktadır.

---

## [v4.3.6] - 2026-09-16 (Giriş Butonları & Hızlı Hesap Düzeltmesi)
### 🐛 Giriş Ekranı ve Hızlı Hesap Seçimi Düzeltildi
- **🔧 initAuthAndSession ReferenceError Giderildi:**
  - `app.js` içerisindeki `initAuthAndSession()` fonksiyonunda `const user = await window.AuthService.init();` satırı eksik kaldığı için oluşan `ReferenceError: user is not defined` hatası giderildi.
  - Bu hata sebebiyle `setupLoginOverlay()` çalışmıyor, form submit listener'ı ve "Hızlı Hesap Seç" butonlarının `onclick` fonksiyonları bağlanamıyordu; hata düzeltilerek butonlar ve form tam çalışır hale getirildi.
- **🚀 Cache Buster v4.3.6:** Tüm asset ve script referansları `?v=4.3.6` yapılarak tarayıcıların anında güncel kodu çekmesi sağlandı.

---

## [v4.3.2] - 2026-09-16 (Canlıya Dağıtım - Zorunlu Giriş & Soru Motoru Entegrasyonu)
### 🔐 Zorunlu Kimlik Doğrulama & Canlıya Güvenli Dağıtım
- **🚪 Şifresiz Giriş Açığı Kapatıldı:**
  - `index.html`'deki `loginOverlay`'den `style="display:none;"` kaldırıldı; overlay varsayılan olarak açık başlar. Sadece geçerli bir oturum doğrulandığında gizlenir.
  - `auth.js` içindeki `getActiveStudent()` fonksiyonunda unauthenticated durumda 'ilay' fallback'i kaldırıldı; oturum yoksa `null` döner.
  - Mobil ve tarayıcı önbelleklerini kırmak için script ve CSS referansları `?v=4.3.2` olarak güncellendi.
- **🛡️ Firebase Senkronizasyon İzolasyonu (AUDIT 🟡-4):**
  - `firebase-sync.js` içindeki `activeUser: 'ilay'` varsayılanı `null` yapıldı. Oturum açılmadan veya `setTargetUser()` çağrılmadan Firebase'e veri yazma ve okuma işlemleri tamamen bloke edildi.
- **📚 Çoklu Branş Manifest Soru Yükleyici (AUDIT 🟡-2):**
  - `quiz.js`'deki sabit tek dosya (`questions_fizyoloji.json`) yükleme mantığı kaldırıldı. `question_bank_manifest.json` üzerindeki tüm aktif branşların (`questionCount > 0`) JSON dosyalarını dinamik yükleyip tek havuzda birleştiren `loadQuestions()` motoru devreye alındı.
- **🔬 Tesseract Türkçe OCR Desteği & Yerel Model Koruması:**
  - `tur.traineddata` modeli yerel ortama eklendi, çift dilli (tur+eng) soru ayıklama hattı aktive edildi. Model dosyaları `.gitignore` ile korunarak reponun şişmesi engellendi.
- **📚 319 Gerçek Çıkmış TUS Sorusu Sanal DB'ye Eklendi (Sayfa 137 / 304):**
  - `Fizyoloji.pdf` kitabından 3. parti (Sayfa 93-137) taranarak **130 yeni soru** daha eklendi ve toplam havuz **319 soruya** ulaştı.
  - 319 soruluk devasa çıkmış soru tabanı (`questions_fizyoloji.json`) yalnızca **415 KB** boyuttadır.
  - **📍 Checkpoint & Resume Altyapısı (`extraction_state.json`):** Kaldığımız yer `lastProcessedPage: 137` olarak kaydedildi.
  - `question_bank_manifest.json` otomatik güncellendi: **Toplam Soru: 319 | Aktif Branş: 1/13**.

---

## [v4.3.1-security-cleanup] - 2026-09-16 (Güvenlik Temizliği)
### 🔒 Hassas Veri Koruması & Firebase Güvenlik Notu
- **🗑️ Backup JSON'lar git'ten çıkarıldı:**
  - `backup_ilay_data_v3.json` ve `current_firebase_data.json` dosyaları `git rm --cached` ile git takibinden kaldırıldı.
  - Bu dosyalar yerel diskte korunuyor (veri kaybı yok). İlay'ın gerçek verisi Firebase'de güvende.
  - `.gitignore`'a `backup_*.json`, `current_firebase_data.json` ve `*_SAFE_COPY_*.json` kuralları eklendi.
  - Yerel güvenlik kopyaları alındı (`*_SAFE_COPY_16092026.json`).
- **⚠️ YAPILACAK — Firebase Rules (Seçenek B) — GEMİNİ HATIRLATICI:**
  - Firebase Realtime Database kuralları şu an herkese açık (public read/write).
  - Yapılacak iş: `tus_v4/auth` → `.read: false` (şifre hash'leri korunur).
  - `tus_v4/users` → `.write: true` bırakılmalı (app yazmaya devam eder).
  - Firebase Console → Realtime Database → Rules ekranından yapılacak (ücretsiz, 2 tıklama).
  - **Neden ertelendi:** Yalnızca 2 kişi Firebase URL'ini biliyor, risk şimdilik kabul edilebilir.
  - **Neden yapılmalı:** URL bilinse dahi tüm kullanıcı hash'leri görünür olabilir.
  - 🔔 **SONRAKİ OTURUMDA İLK YAPILACAK:** AUDIT_15_09_2026.md Karar 2-B referansı.

---

## [v4.3.0-manifest-and-spaced-repetition] - 2026-09-15 (Yerel Geliştirme - Soru Tabanı & İstatistik)
### 📊 13 TUS Dersi Manifest Sistemi, Ders Bazlı Soru Takibi & Aralıklı Tekrar Motoru
- **📚 13 TUS Dersi Soru Takip Manifestosu (`question_bank_manifest.json`):**
  - Tüm TUS branşlarını (Fizyoloji, Patoloji, Dahiliye, Pediatri, Genel Cerrahi, Kadın Doğum, Küçük Stajlar, Biyokimya, Mikrobiyoloji, Farmakoloji, Anatomi, Tıbbi Biyoloji, Halk Sağlığı) içeren merkezi soru manifestosu oluşturuldu.
  - Her ders için ikon, renk, soru sayısı ve alt konu kategorileri (`categories`) takip edilebilir hale getirildi.
  - Soru tabanında toplam soru adedi (`totalQuestions: 7`), aktif ders sayısı (`1 / 13`) ve her dersin JSON yolu standartlaştırıldı.
- **🔍 Ders Bazlı Soru Havuzu Modalı (`index.html`, `quiz.js`, `style.css`):**
  - Dashboard'daki Günlük Quiz kartına etkileşimli `"Havuz: X Soru [🔍 Detay]"` hap butonu eklendi.
  - Tıklandığında açılan modern cam efektli modalda:
    - Toplam soru sayısı, aktif ders sayısı ve Virtual DB altyapısı gösterge kartları.
    - 13 dersin durumunu gösteren dinamik grid (sorusu olan dersler zümrüt yeşili kenarlıkla öne çıkarılır, alt konu dağılımları etiket olarak listelenir).
- **🔁 5.000+ Soru Takibi & Aralıklı Tekrar (Spaced Repetition) Motoru:**
  - Kullanıcının çözdüğü her sorunun durumu (`status: correct/wrong`), son çözüm tarihi (`lastDate`) ve hata sayısı (`wrongCount`) profil bazında kaydedilir.
  - Daha önce yanlış yapılan sorular ~1 hafta sonra öncelikli olarak tekrar sunulur.
  - Yanlış yapılmış bir soru tekrar geldiğinde soru kartının üstünde `"🔄 1 Hafta Önce Bu Soruda Yanılmıştın! Hadi intikam vakti! 💪"` motivasyon rozeti belirir.
- **⚙️ Otomatik Soru Ayıklama Boru Hattı v2.0 (`extract_questions.py`):**
  - **Soru Olmayan Kısımları Kesmeme İlkesi:** İlk denemelerdeki hatalı PNG kesimlerinin (telif yazıları, ünite başlıkları, özet tabloları) tekrarlanmaması için kara liste anahtar kelimeleri (`telif hukuku`, `kul hakkı`, `fotokopi` vb.) eklendi.
  - **Karma Kitaplar Sentaks İzolasyonu:** Patoloji ve Dahiliye gibi soruların konu anlatımlarının arasına serpiştirildiği kitaplarda, metinler taranırken yalnızca `1.`, `A-E` şık dizilimi ve `Doğru cevap:` üçlüsüne sahip izole soru blokları ayıklanır; aradaki teorik kısımlar tamamen atlanır (kesilmez).
  - **Otomatik Manifest Senkronizasyonu:** Kitaptan yeni sorular ayıklandığında `question_bank_manifest.json` dosyasını otomatik güncelleyen ve toplam soru adedini yeniden hesaplayan mekanizma entegre edildi.
- **⛔ Canlıya Çıkış Kilidi (Katı Kural):** Sistem şu anda tamamen yerel geliştirme modundadır (`http://localhost:8080`). En az 2 farklı kitaptan (Fizyoloji + 1 diğer ders) soru tabanı oluşturulup yerel testler başarıyla sonuçlanmadan kesinlikle canlıya (GitHub Pages) dağıtım yapılmayacaktır.

---

## [v4.2.0-virtual-db-pipeline] - 2026-09-15 (Yerel Geliştirme - Plan & Pipeline)
### 🧠 Sanal Soru Tabanı (Virtual DB) Pipeline'ı & Katı Kullanıcı İzolasyonu Düzeltmesi
- **🔒 Kullanıcı İzolasyonu Güvenlik Düzeltmesi (Bugfix):**
  - Uygulama ilk açıldığında oturum doğrulanmadan önce `loadData()` ve `syncFromFirebase()` çağrılarak İlay'ın verilerinin hafızaya alınmasına neden olan yarış durumu (race condition) tamamen kaldırıldı.
  - `activeStudent` varsayılan `'ilay'` değeri `null` yapıldı; veriler sadece kullanıcı başarıyla giriş yaptıktan sonra yüklenir.
  - Kullanıcı Z gibi yeni/boş hesapların Firebase'de verisi yoksa (`null`), İlay'ın veya eski kullanıcının hafızadaki verilerini devralması engellendi; standart boş şablon sıfırdan oluşturulur.
  - Canberk'in İlay'a özel motivasyon notu (`floatingNote`), katı `activeStudent === 'ilay'` koşuluna bağlandı; Kullanıcı Z, X veya başka hiçbir kullanıcı bu notu göremez.
- **📚 Virtual Soru Tabanı (Virtual Question Bank) Mimarisi:**
  - `cikmis_sorular/virtual_db/` dizini kuruldu ve `questions_fizyoloji.json` ile yapısal hafif JSON formatına geçildi.
  - **Soru Olmayan Kısımları Atla Kuralı:** Kapaklar, telif sayfaları, içindekiler, salt teori paragrafları ve özet tabloları soru olarak kırpılmayacak.
  - **Dörtlü Soru Doğrulama Şartı:** Bir bloğun soru sayılabilmesi için (1) Soru kökü + Sınav dönemi, (2) A-E şık bütünlüğü, (3) Doğru cevap anahtarı ve (4) TUS klinik püf noktası açıklamasının bulunması şart koşuldu.
  - **Ultra Hafif Yapay JSON Depolama:** 500 soru için yüzlerce megabaytlık PNG üretimi yerine, metin tabanlı sorular salt JSON içinde (100 soru ~35 KB) saklanır. Yalnızca soruda gerçek bir klinik görsel (EKG, tomografi, patoloji kesiti) varsa o kısım WebP olarak kırpılır.
- **📑 Dokümantasyon:**
  - `SORU_EKLEME_PLANI.md` (v4.2.0) sanal soru tabanı mimarisi, kitap bazlı ayrıştırma boru hattı ve yarınki adımlarla baştan sona güncellendi.

---

## [v4.1.0-local-demo] - 2026-09-15 (Yerel Geliştirme Ortamı - Canlıya Alınmadı)
### 🎯 TUS Fizyoloji Çıkmış Soru Bankası & Oyunlaştırılmış Mini-Quiz Motoru
- **🛡️ Sıfır Firebase Yükü & Git Koruma Mimarisi:**
  - 172 MB'lık `Fizyoloji.pdf` dosyası `.gitignore`'a eklendi (`cikmis_sorular/*.pdf`, `*.pdf`). Git depolama ve GitHub Pages 100 MB limiti korundu.
  - Soru bankası Firebase yerine istemci tarafında statik ve ultra hafif `cikmis_sorular/fizyoloji_sorular.json` olarak yapılandırıldı.
  - Firebase Realtime Database'e yalnızca kullanıcı başına günlük ~100 byte'lık quiz istatistiği (`/tus_v4/users/{username}/quiz`) yazılarak Firebase kotası ve performansı %100 koruma altına alındı.
- **🔬 Çıkmış Soru Ayıklama (OCR & Görüntü İşleme):**
  - Tesseract OCR ve PyMuPDF motoru ile `Fizyoloji.pdf` kitapçığından gerçek çıkmış TUS soruları (Nisan 2001, Eylül 1999, Nisan 1997, Nisan 1994, Eylül 2003, Nisan 2005, Eylül 2006) soru kökü, A-E seçenekleri, doğru cevapları ve detaylı klinik açıklamalarıyla dijitalleştirildi.
- **🎮 Duolingo & RPG Oyunlaştırma Arayüzü (`quiz.js`, `style.css`):**
  - **Dashboard Hero Widget:** Günlük seri (🔥 Streak), toplam XP (⚡), Doktorluk Rütbesi (🩺 Stajyer Dr. ➔ 🥼 İntörn Dr. ➔ 👨‍⚕️ TUS Asistanı ➔ 👑 Uzman Dr.) ve `Günün Quizi (5 Soru) [Quize Başla 🚀]` kartı.
  - **İnteraktif Soru Modalı:** Soru ilerleme çubuğu, anlık zümrüt yeşili doğru ve yakut kırmızısı yanlış geri bildirimi, sallanma ve nabız animasyonları.
  - **TUS Püf Noktası Kartı:** Şık tıklandıktan sonra beliren yüksek verimli klinik ders notu ve püf noktaları.
  - **Kutlama & Sonuç Ekranı:** Canvas-confetti parçacık yağmuru 🎉, doğruluk oranı, kazanılan XP, seri artışı ve tek tıkla dashboard'a dönüş.
- **👥 Multi-User Quiz İzolasyonu:**
  - Canberk (Admin) ve İlay kullanıcılarının quiz verileri, serileri ve XP'leri birbirinden tamamen izole şekilde tutulur; İlay'ın çalışma kayıtlarına sıfır dokunulmuştur.
- **🧪 Doğrulama:**
  - Yerel sunucuda (`http://localhost:8080`) tarayıcı alt ajanı ile soru çözme, streak artışı, açıklama kutusu ve kutlama akışı test edildi.

---

## [v4.0.0] - 2026-09-15 (Canlıda Yayında - GitHub Pages)
### 🔐 Çoklu Kullanıcı & Admin Yönetim Sistemi (Multi-User & Role-Based Access)
- **🛡️ Sıfır Risk & Veri Koruma Protokolü:**
  - İlay'ın tüm canlı verileri (13 kitap, 1.096 sayfa, çalışma logları, notlar, ayarlar) `backup_ilay_data_v3.json` olarak kalıcı yedeklendi ve kayıpsız aktarıldı.
  - Canlı Firebase veritabanı `/tus_v4/` altına taşındı, eski `/tus.json` korundu.
- **🔑 Kimlik Doğrulama Servisi (`auth.js`):**
  - Web Crypto API (`crypto.subtle`) ile güvenli SHA-256 şifre hashleme.
  - Oturum kontrolü (`localStorage` ve Firebase RTDB auth tablosu).
- **🚪 Güvenli Giriş Ekranı (Login Overlay):**
  - Koyu tema cam efektli (glassmorphism) açılış giriş kartı.
  - Hızlı hesap seçim butonları: Seçim yapıldığında kullanıcı adını doldurur fakat **şifre girilmesi kesinlikle zorunludur** (kimse başkasının hesabına yetkisiz giremez).
- **👁️ Admin Öğrenci Değiştirici (Student Switcher):**
  - Sadece Canberk (Admin) giriş yaptığında navbar'da beliren açılır menü ile adayların süreçleri arasında sayfa yenilenmeden anında geçiş.
- **👥 Öğrenci Yönetim Paneli (Ayarlar Sayfası):**
  - Admin için dinamik öğrenci listesi, şifre sıfırlama, modern silme onay modalı (`confirmDeleteModal`) ve Standart 13 TUS Kitabı şablonlu yeni öğrenci ekleme modalı.
- **🔒 Katı Veri İzolasyonu:**
  - Normal öğrenciler (İlay ve diğer adaylar) yalnızca kendi çalışma süreçlerini görür; switcher veya admin menülerini asla göremezler.

---

## [v3.3.0] - 2026-08-25
### ✨ Yeni Özellikler
- **📋 Notlar & Görevler (Checklist & Notes) Sayfası:**
  - Yeni navbar sekmesi `📋 Notlar` eklendi.
  - Görev ekleme, tamamlama, silme ve filtreleme (Tümü / Bekleyen / Tamamlanan).
  - Kitaplardan otomatik tag seçimi ve serbest özel etiket ekleme desteği.
  - **Sürükle-Bırak (Drag & Drop):** Görevleri istenen sırada manuel düzenleyebilme.
  - **İlerleme Halkası (Progress Ring):** Tamamlanan/toplam görev oranı ve haftalık tamamlanan görev istatistikleri.
  - **Aylık Mini Takvim:** Görevli günlerde renkli durum noktaları, tarihe tıklayarak günün görevlerini filtreleme.
  - **📝 Hızlı Not Alanı:** Serbest not defteri ve tek tıkla kaydetme.
- **🗂️ Dashboard Açılır-Kapanır (Collapsible) Akordeon Paneller:**
  - `📚 Kitap Bazlı İlerleme` ve `📋 Görevlerim` bölümleri akordeon şeklinde açılıp kapanabilir hale getirildi.
  - Panel başlıklarında anlık durum rozetleri (`X kitap • %Y`, `X bekliyor`).
  - Dashboard üzerinden Notlar sayfasına geçmeden doğrudan görev tamamlama checkbox desteği.
  - Gecikmiş görevler için kırmızı `⚠️` uyarı gösterimi.
- **🔄 Firebase Senkronizasyonu Genişletildi:**
  - Görevler (`tasks`) ve hızlı not (`quickNote`) gerçek zamanlı bulut eşitlemesine dahil edildi.

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
