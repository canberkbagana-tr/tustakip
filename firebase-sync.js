// ===== Firebase Sync Module (v4 - Multi-User REST API) =====
// Uses Firebase Realtime Database REST API with per-user data isolation

(function() {
  'use strict';

  const DB_URL = 'https://tustakip-default-rtdb.europe-west1.firebasedatabase.app';

  // Standard TUS books template for newly registered students
  const DEFAULT_TUS_BOOKS_TEMPLATE = [
    { id: "tus_dahiliye", name: "Dahiliye", totalPages: 560, color: "#7c5cfc", createdAt: "2026-09-15" },
    { id: "tus_pediatri", name: "Pediatri", totalPages: 626, color: "#38d9d9", createdAt: "2026-09-15" },
    { id: "tus_genelcerrahi", name: "Genel Cerrahi", totalPages: 451, color: "#eab308", createdAt: "2026-09-15" },
    { id: "tus_kadindogum", name: "Kadın Doğum", totalPages: 316, color: "#84cc16", createdAt: "2026-09-15" },
    { id: "tus_kucukstajlar", name: "Küçük Stajlar", totalPages: 432, color: "#10b981", createdAt: "2026-09-15" },
    { id: "tus_biyokimya", name: "Biyokimya", totalPages: 320, color: "#4ade80", createdAt: "2026-09-15" },
    { id: "tus_mikrobiyoloji", name: "Mikrobiyoloji", totalPages: 360, color: "#f97316", createdAt: "2026-09-15" },
    { id: "tus_patoloji", name: "Patoloji", totalPages: 388, color: "#f472b6", createdAt: "2026-09-15" },
    { id: "tus_farmakoloji", name: "Farmakoloji", totalPages: 444, color: "#f87171", createdAt: "2026-09-15" },
    { id: "tus_anatomi", name: "Anatomi", totalPages: 354, color: "#d946ef", createdAt: "2026-09-15" },
    { id: "tus_fizyoloji", name: "Fizyoloji", totalPages: 302, color: "#ef4444", createdAt: "2026-09-15" },
    { id: "tus_entegrehucre", name: "Entegre Hücre", totalPages: 52, color: "#4f8cff", createdAt: "2026-09-15" },
    { id: "tus_orjinalsorular", name: "Orijinal TUS Soruları", totalPages: 33, color: "#ef4444", createdAt: "2026-09-15" }
  ];

  const FirebaseSync = {
    connected: false,
    lastSync: null,
    syncing: false,
    activeUser: 'ilay', // target user profile to sync

    // Set target user profile (used when switching students or on user login)
    setTargetUser(username) {
      if (username) {
        this.activeUser = username.trim().toLowerCase();
      }
    },

    getTargetUser() {
      return this.activeUser;
    },

    getDefaultBooksTemplate() {
      return JSON.parse(JSON.stringify(DEFAULT_TUS_BOOKS_TEMPLATE));
    },

    // ===== Read user data from Firebase =====
    async fetchAll() {
      const user = this.activeUser || 'ilay';
      try {
        const res = await fetch(`${DB_URL}/tus_v4/users/${user}/data.json`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        let data = await res.json();

        // 🛡️ ZERO-LOSS MIGRATION: If İlay has no data in tus_v4 yet, seamlessly copy from original /tus.json
        if (!data && user === 'ilay') {
          console.log('Migrating existing İlay live data to /tus_v4/users/ilay/data...');
          const legacyRes = await fetch(`${DB_URL}/tus.json`);
          if (legacyRes.ok) {
            const legacyData = await legacyRes.json();
            if (legacyData) {
              data = legacyData;
              // Save it to new location immediately
              await this.saveAll(data);
            }
          }
        }

        this.connected = true;
        this.lastSync = new Date();
        return data;
      } catch (err) {
        console.error(`Firebase okuma hatası (${user}):`, err);
        this.connected = false;
        return null;
      }
    },

    // ===== Write user data to Firebase =====
    async saveAll(data) {
      if (this.syncing) return;
      this.syncing = true;
      const user = this.activeUser || 'ilay';
      try {
        const res = await fetch(`${DB_URL}/tus_v4/users/${user}/data.json`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        this.connected = true;
        this.lastSync = new Date();
        this.syncing = false;
        return true;
      } catch (err) {
        console.error(`Firebase yazma hatası (${user}):`, err);
        this.connected = false;
        this.syncing = false;
        return false;
      }
    },

    // ===== Save specific path for active user =====
    async savePath(path, data) {
      const user = this.activeUser || 'ilay';
      try {
        const res = await fetch(`${DB_URL}/tus_v4/users/${user}/data/${path}.json`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        this.connected = true;
        this.lastSync = new Date();
        return true;
      } catch (err) {
        console.error(`Firebase ${user}/${path} yazma hatası:`, err);
        return false;
      }
    },

    // ===== Fetch overview progress for all users (for Admin dashboard) =====
    async fetchAllUsersOverview() {
      try {
        const res = await fetch(`${DB_URL}/tus_v4/users.json`);
        if (!res.ok) return {};
        const allUsers = await res.json();
        return allUsers || {};
      } catch (e) {
        console.error('Fetch all users overview error:', e);
        return {};
      }
    },

    // ===== Get sync status badge HTML =====
    getStatusHTML() {
      if (this.connected) {
        const timeStr = this.lastSync
          ? this.lastSync.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
          : '-';
        return `<span class="sync-badge sync-online" title="Son senkronizasyon: ${timeStr}">🟢 Senkron (${this.activeUser})</span>`;
      }
      return `<span class="sync-badge sync-offline" title="Firebase bağlantısı yok">🔴 Çevrimdışı</span>`;
    }
  };

  window.FirebaseSync = FirebaseSync;
})();
