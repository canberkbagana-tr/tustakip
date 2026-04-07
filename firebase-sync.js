// ===== Firebase Sync Module (REST API) =====
// No SDK needed - uses Firebase Realtime Database REST API

(function() {
  'use strict';

  const DB_URL = 'https://tustakip-default-rtdb.europe-west1.firebasedatabase.app';

  const FirebaseSync = {
    // Status
    connected: false,
    lastSync: null,
    syncing: false,

    // ===== Read all data from Firebase =====
    async fetchAll() {
      try {
        const res = await fetch(`${DB_URL}/tus.json`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        this.connected = true;
        this.lastSync = new Date();
        return data;
      } catch (err) {
        console.error('Firebase okuma hatası:', err);
        this.connected = false;
        return null;
      }
    },

    // ===== Write all data to Firebase =====
    async saveAll(data) {
      if (this.syncing) return;
      this.syncing = true;
      try {
        const res = await fetch(`${DB_URL}/tus.json`, {
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
        console.error('Firebase yazma hatası:', err);
        this.connected = false;
        this.syncing = false;
        return false;
      }
    },

    // ===== Save specific path =====
    async savePath(path, data) {
      try {
        const res = await fetch(`${DB_URL}/tus/${path}.json`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        this.connected = true;
        this.lastSync = new Date();
        return true;
      } catch (err) {
        console.error(`Firebase ${path} yazma hatası:`, err);
        return false;
      }
    },

    // ===== Get sync status badge HTML =====
    getStatusHTML() {
      if (this.connected) {
        const timeStr = this.lastSync
          ? this.lastSync.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' })
          : '-';
        return `<span class="sync-badge sync-online" title="Son senkronizasyon: ${timeStr}">🟢 Senkron</span>`;
      }
      return `<span class="sync-badge sync-offline" title="Firebase bağlantısı yok">🔴 Çevrimdışı</span>`;
    }
  };

  window.FirebaseSync = FirebaseSync;
})();
