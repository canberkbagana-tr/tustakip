# 📋 TUS Takip - Çoklu Kullanıcı & Yetkilendirme Sistemi Planı (v4.0.0)

> **⚠️ KRİTİK GÜVENLİK KURALI:**  
> Bu plan kapsamındaki geliştirmeler tamamlanıp yerelde test edilip onaylanana kadar **canlıya (`git push`) ASLA sürülmeyecektir.**  
> Mevcut aktif kullanıcımız **İlay'ın** hiçbir verisi (13 kitap, tüm çalışma logları, notlar, ayarlar) silinmeyecek ve etkilenmeyecektir.

---

## 🎯 1. Proje Hedefi ve Kapsamı

TUS Takip uygulamasını tek kullanıcılı yapısından çıkarıp, birden fazla adayın (kız arkadaşınız İlay, arkadaşlarınız X, Y ve gelecekteki yeni kullanıcılar) birbirinden tamamen bağımsız olarak kendi TUS süreçlerini takip edebileceği; **Canberk'in (Admin)** ise tüm adayların süreçlerini tek bir panelden inceleyip yönetebileceği güvenli, modüler ve çok kullanıcılı bir sisteme dönüştürmek.

---

## 🛡️ 2. Sıfır Risk & Veri Koruma Stratejisi (İlay'ın Verisi)

Mevcut canlı sistem Firebase üzerinde doğrudan `/tus.json` yolunu kullanmaktadır. İlay'ın verisinin sıfır riskle korunması için şu protokol uygulanacaktır:

1. **İkili Yedekleme (Backup):**
   - Mevcut canlı Firebase verisi yerelde `backup_ilay_data_v3.json` olarak kalıcı yedeklenecektir.
   - Firebase üzerinde `/tus.json` yolu kesinlikle silinmeyecek, salt-okunur referans olarak tutulacaktır.
2. **İzole Veritabanı Alanı (`/tus_v4/`):**
   - Çoklu kullanıcı sistemi Firebase üzerinde `/tus_v4/` ağacında başlatılacaktır.
   - Böylece canlıdaki mevcut v3 site (`/tus.json`) çalışan telefonlarda kesintisiz çalışmaya devam ederken, biz yeni v4 sistemini geliştirebiliriz.
3. **Otomatik Veri Aktarımı (Migration):**
   - Sistem ilk açıldığında İlay'ın tüm mevcut kitapları, günlük girişleri, özel notu ve ayarları otomatik olarak `/tus_v4/users/ilay/data` yoluna birebir kopyalanacaktır.
4. **Git İzolasyonu:**
   - Geliştirme yerel branch'te (`feature/multi-user`) yapılacak, `origin/main`'e testler bitmeden push atılmayacaktır.

---

## 🔐 3. Kullanıcı Rolleri ve Yetki Matrisi

| Kullanıcı | Rol | Giriş | Yetkiler & Görünürlük |
| :--- | :--- | :--- | :--- |
| **Canberk** | `ADMIN` | Kullanıcı adı & Şifre | **Tam Yetki:** Tüm sayfaları görür. Navbar veya ayarlardan "Aktif Öğrenciyi Değiştir" menüsüyle İlay, X ve Y'nin süreçleri arasında tek tıkla geçiş yapabilir. Yeni kullanıcı ekleyebilir, şifre sıfırlayabilir, toplu istatistikleri görebilir. |
| **İlay** | `USER` | Kullanıcı adı & Şifre | **Özel Veri:** Yalnızca kendi kitaplarını, çalışma loglarını, motivasyon notunu ve takvimini görür. Başka kullanıcıların varlığını dahi görmez. |
| **Kullanıcı X** | `USER` | Adminin verdiği Kullanıcı adı & Şifre | **İzole Veri:** Sıfırdan temiz bir müfredat/kitap şablonu ile başlar. Yalnızca kendi verilerini görür ve yönetir. |
| **Kullanıcı Y** | `USER` | Adminin verdiği Kullanıcı adı & Şifre | **İzole Veri:** Sıfırdan temiz bir müfredat/kitap şablonu ile başlar. Yalnızca kendi verilerini görür ve yönetir. |
| *Gelecek Kullanıcılar* | `USER` | Admin panelinden oluşturulur | Aynı izole kullanıcı yapısına otomatik dahil olur. |

---

## 🗄️ 4. Firebase Veritabanı Mimarisi (v4)

Yeni yapay ağaç Firebase Realtime Database üzerinde şu şekilde organize edilecektir:

```text
tus_v4/
├── auth/                               # Kimlik doğrulama havuzu
│   ├── canberk/
│   │   ├── username: "canberk"
│   │   ├── passwordHash: "..."         # SHA-256 / PBKDF2 hash
│   │   ├── displayName: "Canberk (Admin)"
│   │   ├── role: "admin"
│   │   └── createdAt: "2026-09-15"
│   ├── ilay/
│   │   ├── username: "ilay"
│   │   ├── passwordHash: "..."
│   │   ├── displayName: "İlay"
│   │   ├── role: "user"
│   │   └── createdAt: "2026-09-15"
│   ├── user_x/
│   │   └── ...
│   └── user_y/
│       └── ...
│
└── users/                              # İzole kullanıcı verileri
    ├── ilay/
    │   ├── books: [...]                # 13 TUS Kitabı
    │   ├── entries: [...]              # Nisan-Ağustos çalışma kayıtları
    │   ├── settings: {...}             # Hedefler, partner notu, sınav tarihi
    │   ├── tasks: [...]                # Notlar ve Görevler
    │   └── quickNote: "..."
    ├── user_x/
    │   ├── books: [...]
    │   └── ...
    └── user_y/
        └── ...
```

---

## 💻 5. Arayüz & Kullanıcı Deneyimi Değişiklikleri

1. **Giriş Ekranı (Login Modal / View):**
   - Açılışta oturum kontrolü: Aktif oturum yoksa modern, koyu tema cam efekti (glassmorphism) şık bir giriş kartı karşılar.
   - Kullanıcı adı ve Şifre girişi, "Beni Hatırla" seçeneği.
   - Giriş yapıldığında yerel `localStorage`'a oturum token'ı kaydedilir.
2. **Admin Hızlı Profil Değiştirici (Student Switcher):**
   - Sadece `canberk` giriş yaptığında navbar'da veya sağ üstte beliren özel rozet:
     `👁️ İncelenen: [ İlay ▾ ]`
   - Tıklandığında açılan menü:
     - 👩‍⚕️ İlay (Aktif İlerleme)
     - 👨‍⚕️ Kullanıcı X
     - 👨‍⚕️ Kullanıcı Y
     - ⚙️ Yeni Kullanıcı Ekle
   - Seçim yapıldığında sayfa yenilenmeden tüm dashboard, grafikler ve loglar seçilen kullanıcının verileriyle anlık güncellenir.
3. **Admin Kullanıcı Yönetim Paneli (Ayarlar sekmesi içinde):**
   - Yeni kullanıcı oluşturma formu: Kullanıcı Adı, Görünen Ad, Başlangıç Şifresi, Şablon (Standart TUS Kitapları ile başlasın mı?).
   - Mevcut kullanıcıların listesi, son giriş/aktivite tarihi, şifre sıfırlama butonu.
4. **Normal Kullanıcı Arayüzü:**
   - İlay ve diğer adaylar için ekran son derece sade, dikkat dağıtmayan kendi TUS odaklı çalışma alanı olarak kalır; admin menülerini asla görmezler.

---

## ✅ 6. Detaylı Kontrol Listesi (Checklist)

### Aşama 1: Güvenlik, Yedekleme ve Hazırlık (TAMAMLANDI)
- [x] Canlı Firebase verisinin kontrol edilmesi (`/tus.json` içeriği doğrulandı)
- [x] Yerel `backup_ilay_data_v3.json` yedeğinin oluşturulması (21.9 KB tam yedek alındı)
- [x] Canlıya push engeli: Yerelde güvenli izolasyon sağlandı, `origin/main` etkilenmedi

### Aşama 2: Kimlik Doğrulama & Veri Katmanı (`auth.js` & `firebase-sync.js`) (TAMAMLANDI)
- [x] İstemci taraflı güvenli hash mekanizmasının (Web Crypto SHA-256) kurulması
- [x] `AuthService` modülünün yazılması (`login`, `logout`, `getCurrentUser`, `isAdmin`, `createUser`, `resetPassword`)
- [x] `FirebaseSync` modülünün v4 çoklu kullanıcı mimarisine uyarlanması:
  - `/tus_v4/users/{activeUsername}/` dinamik veri yolu
  - Admin için istenen kullanıcının verisini okuma (`fetchUserData`)
  - Yeni kullanıcılar için 13 derslik Standart TUS Kitap Şablonu
- [x] İlk açılışta İlay'ın canlı verisinin `/tus_v4/users/ilay` alanına güvenli aktarımı (Sıfır veri kaybı doğrulandı)

### Aşama 3: Kullanıcı Arayüzü (UI) Entegrasyonu (TAMAMLANDI)
- [x] Şık ve modern Giriş (Login) ekranı HTML/CSS bileşeninin eklenmesi (Cam efektli koyu tema)
- [x] Navbar'a "Çıkış Yap" ve Admin için "Öğrenci Değiştirici (Switcher)" dropdown eklenmesi
- [x] Ayarlar sayfasına sadece Admin'in görebileceği "Kullanıcı Yönetimi" kartının eklenmesi
- [x] Yeni kullanıcı oluşturma modalı ve hazır TUS kitapları şablon seçeneği

### Aşama 4: Yerel Testler & Doğrulama (Staging) (TAMAMLANDI)
- [x] Canberk (Admin) girişi testi: Switcher ile İlay, X ve Y profilleri kontrol edildi
- [x] İlay hesabı testi: 1.096 sayfa, 13 kitap, notlar ve ayarlar eksiksiz doğrulandı
- [x] Kullanıcı X ve Y izolasyon testi: Normal kullanıcılarda switcher ve yönetim panelinin gizlendiği teyit edildi
- [x] Çıkış yap / Giriş yap oturum testleri başarıyla tamamlandı
- [x] Tarayıcı alt-ajanı ile tam akış otomatik olarak test edildi ve video kaydı alındı

### Aşama 5: Canlıya Geçiş Onayı (Deployment) (TAMAMLANDI)
- [x] Kullanıcının (Canberk) yerel demoyu inceleyip onay vermesi (Onay alındı)
- [x] GitHub'a push ve GitHub Pages yayını (Canlıya alındı)

---

## 📜 7. Değişiklik Günlüğü (Changelog)

### [v4.0.0-draft] - 2026-09-15
- **Plan:** Çoklu kullanıcı ve admin kontrol sistemi planı oluşturuldu (`MULTI_USER_PLAN.md`).
- **Güvenlik:** Canlıya push işlemi durduruldu, İlay'ın verisini koruyacak izole Firebase veri mimarisi tasarlandı.
