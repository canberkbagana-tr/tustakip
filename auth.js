// ===== TUS Takip - Authentication & Multi-User Service (v4.0.0) =====
(function() {
  'use strict';

  const DB_URL = 'https://tustakip-default-rtdb.europe-west1.firebasedatabase.app';
  const SESSION_KEY = 'tus_session_v4';
  const HASH_SALT = 'tus_takip_salt_2026';

  // Helper: SHA-256 hash using Web Crypto API
  async function hashPassword(password) {
    if (!password) return '';
    try {
      const msgBuffer = new TextEncoder().encode(password + HASH_SALT);
      const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    } catch (e) {
      // Fallback simple hash for older environments
      let hash = 0;
      const str = password + HASH_SALT;
      for (let i = 0; i < str.length; i++) {
        hash = ((hash << 5) - hash) + str.charCodeAt(i);
        hash |= 0;
      }
      return 'fallback_' + Math.abs(hash).toString(16);
    }
  }

  const AuthService = {
    currentUser: null,
    usersCache: {},

    // ===== Initialize & Check Session (Strict Security: Password on Every Visit) =====
    async init() {
      // 🔒 Katı Güvenlik Protokolü: Sayfa her açıldığında şifre zorunludur.
      this.currentUser = null;
      try {
        localStorage.removeItem(SESSION_KEY);
      } catch (e) {}

      // Check if users exist in Firebase, seed default accounts if empty
      await this.ensureInitialSeed();
      return null;
    },

    // ===== Seed initial accounts if not created yet =====
    async ensureInitialSeed() {
      try {
        const res = await fetch(`${DB_URL}/tus_v4/auth.json`);
        if (!res.ok) return;
        const users = await res.json();
        
        if (!users || Object.keys(users).length === 0) {
          console.log('Seeding initial accounts (canberk, ilay, x, y)...');
          const seedUsers = {
            canberk: {
              username: 'canberk',
              displayName: 'Canberk (Admin)',
              role: 'admin',
              passwordHash: await hashPassword('canberk123'),
              createdAt: new Date().toISOString()
            },
            ilay: {
              username: 'ilay',
              displayName: 'İlay',
              role: 'user',
              passwordHash: await hashPassword('ilay123'),
              createdAt: new Date().toISOString()
            },
            x: {
              username: 'x',
              displayName: 'Kullanıcı X',
              role: 'user',
              passwordHash: await hashPassword('tus123'),
              createdAt: new Date().toISOString()
            },
            y: {
              username: 'y',
              displayName: 'Kullanıcı Y',
              role: 'user',
              passwordHash: await hashPassword('tus123'),
              createdAt: new Date().toISOString()
            }
          };

          await fetch(`${DB_URL}/tus_v4/auth.json`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(seedUsers)
          });
          this.usersCache = seedUsers;
        } else {
          this.usersCache = users;
        }
      } catch (err) {
        console.warn('Seed / Auth check failed:', err);
      }
    },

    // ===== Login =====
    async login(rawUsername, rawPassword) {
      if (!rawUsername || !rawPassword) {
        return { success: false, message: 'Kullanıcı adı ve şifre zorunludur.' };
      }

      const username = rawUsername.trim().toLowerCase();
      const inputHash = await hashPassword(rawPassword.trim());

      try {
        // Fetch specific user from Firebase
        const res = await fetch(`${DB_URL}/tus_v4/auth/${username}.json`);
        if (!res.ok) {
          return { success: false, message: 'Sunucuya bağlanılamadı. İnternet bağlantınızı kontrol edin.' };
        }
        const user = await res.json();

        if (!user) {
          return { success: false, message: 'Kullanıcı bulunamadı.' };
        }

        if (user.passwordHash !== inputHash) {
          return { success: false, message: 'Şifre hatalı!' };
        }

        // Login success
        this.currentUser = {
          username: user.username,
          displayName: user.displayName || user.username,
          role: user.role || 'user',
          loginAt: new Date().toISOString()
        };

        localStorage.setItem(SESSION_KEY, JSON.stringify(this.currentUser));
        return { success: true, user: this.currentUser };
      } catch (err) {
        console.error('Login error:', err);
        return { success: false, message: 'Giriş sırasında bir hata oluştu: ' + err.message };
      }
    },

    // ===== Logout =====
    logout() {
      this.currentUser = null;
      localStorage.removeItem(SESSION_KEY);
      localStorage.removeItem('tus_active_target_student');
      window.location.reload();
    },

    // ===== Get Current User =====
    getCurrentUser() {
      return this.currentUser;
    },

    // ===== Get Active Target Student (for Multi-User) =====
    getActiveStudent() {
      if (!this.currentUser) return null;
      if (this.isAdmin()) {
        const target = localStorage.getItem('tus_active_target_student');
        if (target) return target;
      }
      return this.currentUser.username;
    },

    // ===== Check Admin =====
    isAdmin() {
      return this.currentUser && this.currentUser.role === 'admin';
    },

    // ===== Admin: Fetch All Users =====
    async getAllUsers() {
      if (!this.isAdmin()) return [];
      try {
        const res = await fetch(`${DB_URL}/tus_v4/auth.json`);
        if (!res.ok) return [];
        const data = await res.json();
        if (!data) return [];
        return Object.values(data).map(u => ({
          username: u.username,
          displayName: u.displayName,
          role: u.role,
          createdAt: u.createdAt
        }));
      } catch (e) {
        console.error('Get all users error:', e);
        return [];
      }
    },

    // ===== Admin: Create New User =====
    async createUser(username, password, displayName, role = 'user') {
      if (!this.isAdmin()) {
        return { success: false, message: 'Bu işlem için yetkiniz yok.' };
      }

      const cleanUsername = username.trim().toLowerCase().replace(/[^a-z0-9_]/g, '');
      if (!cleanUsername || cleanUsername.length < 2) {
        return { success: false, message: 'Kullanıcı adı en az 2 karakter olmalı (harf, rakam, altçizgi).' };
      }

      if (!password || password.length < 3) {
        return { success: false, message: 'Şifre en az 3 karakter olmalıdır.' };
      }

      try {
        // Check if user already exists
        const checkRes = await fetch(`${DB_URL}/tus_v4/auth/${cleanUsername}.json`);
        const existing = await checkRes.json();
        if (existing) {
          return { success: false, message: 'Bu kullanıcı adı zaten kullanılıyor!' };
        }

        const newUser = {
          username: cleanUsername,
          displayName: displayName ? displayName.trim() : cleanUsername,
          role: role,
          passwordHash: await hashPassword(password.trim()),
          createdAt: new Date().toISOString()
        };

        const putRes = await fetch(`${DB_URL}/tus_v4/auth/${cleanUsername}.json`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newUser)
        });

        if (!putRes.ok) throw new Error('Kaydedilemedi');

        return { success: true, user: newUser };
      } catch (err) {
        console.error('Create user error:', err);
        return { success: false, message: 'Kullanıcı oluşturulurken hata: ' + err.message };
      }
    },

    // ===== Admin: Reset User Password =====
    async resetPassword(username, newPassword) {
      if (!this.isAdmin()) {
        return { success: false, message: 'Bu işlem için yetkiniz yok.' };
      }
      if (!newPassword || newPassword.length < 3) {
        return { success: false, message: 'Şifre en az 3 karakter olmalıdır.' };
      }

      try {
        const cleanUser = username.trim().toLowerCase();
        const hash = await hashPassword(newPassword.trim());
        const res = await fetch(`${DB_URL}/tus_v4/auth/${cleanUser}/passwordHash.json`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(hash)
        });
        if (!res.ok) throw new Error('Şifre güncellenemedi.');
        return { success: true, message: `${cleanUser} kullanıcısının şifresi başarıyla güncellendi.` };
      } catch (e) {
        return { success: false, message: e.message };
      }
    },

    // ===== Admin: Delete User =====
    async deleteUser(username) {
      if (!this.isAdmin()) {
        return { success: false, message: 'Bu işlem için yetkiniz yok.' };
      }
      const cleanUser = username.trim().toLowerCase();
      if (cleanUser === 'canberk') {
        return { success: false, message: 'Ana admin hesabı silinemez!' };
      }
      if (cleanUser === 'ilay') {
        return { success: false, message: 'İlay hesabı korumalıdır, silinemez.' };
      }

      try {
        const res = await fetch(`${DB_URL}/tus_v4/auth/${cleanUser}.json`, {
          method: 'DELETE'
        });
        if (!res.ok) throw new Error('Kullanıcı silinemedi.');
        // Also delete user's data tree
        await fetch(`${DB_URL}/tus_v4/users/${cleanUser}.json`, {
          method: 'DELETE'
        });
        if (this.usersCache) delete this.usersCache[cleanUser];
        return { success: true, message: `${cleanUser} hesabı başarıyla silindi.` };
      } catch (e) {
        return { success: false, message: e.message };
      }
    }
  };

  window.AuthService = AuthService;
})();
