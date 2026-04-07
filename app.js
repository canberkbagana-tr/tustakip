// ===== TUS Takip - Main Application (v3 - Firebase Sync + Weekly Report) =====

(function() {
  'use strict';

  // ===== Constants =====
  const STORAGE_KEYS = {
    entries: 'tus_entries',
    settings: 'tus_settings',
    books: 'tus_books'
  };

  const DEFAULT_SETTINGS = {
    reviewPercent: 20,
    dailyGoal: 100,
    shiftDays: 8,
    restDays: 3,
    studentName: ''
  };

  const MOTIVATIONAL_QUOTES = [
    "Her sayfa seni hedefe bir adım daha yaklaştırıyor!",
    "Bugün okuduğun her sayfa, yarının başarısıdır.",
    "Disiplin, motivasyonun bittiği yerde başlar.",
    "Küçük adımlar, büyük başarılar getirir.",
    "Hedefine odaklan, geri kalan gelecektir.",
    "Bugün yaptığın fedakarlık, yarın seni TUS kazananı yapacak!",
    "Çalışmak zordur ama pişmanlık daha zordur.",
    "Sen başarabilirsin! Her sayfa bir tuğla, TUS senin evin!",
    "Vazgeçme! En karanlık an, şafaktan hemen öncedir.",
    "Doktorlar asla pes etmez! 💪",
    "Bugün çalış, yarın gülümse!",
    "Bir sayfa daha, bir adım daha yakın!",
    "TUS sadece bir sınav değil, bir yaşam tarzı!",
    "Konsantrasyonunu koru, hedefe kilitle!",
    "Başarı, her gün tekrarlanan küçük çabaların toplamıdır."
  ];

  const TYPE_LABELS = {
    calisma: { text: 'Çalışma', emoji: '📚' },
    nobet: { text: 'Nöbet', emoji: '🏥' },
    tatil: { text: 'Tatil', emoji: '🌴' }
  };

  const DAY_NAMES = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'];

  // ===== State =====
  let entries = [];
  let books = [];
  let settings = { ...DEFAULT_SETTINGS };
  let dailyChart = null;
  let monthlyChart = null;
  let bookChart = null;
  let weeklyChart = null;
  let selectedBookColor = '#7c5cfc';
  let currentWeekOffset = 0; // 0 = this week, -1 = last week, etc.

  // ===== Helpers =====
  function loadData() {
    try {
      const se = localStorage.getItem(STORAGE_KEYS.entries);
      if (se) entries = JSON.parse(se);
      const sb = localStorage.getItem(STORAGE_KEYS.books);
      if (sb) books = JSON.parse(sb);
      const ss = localStorage.getItem(STORAGE_KEYS.settings);
      if (ss) settings = { ...DEFAULT_SETTINGS, ...JSON.parse(ss) };
    } catch (e) { console.error('Veri yükleme hatası:', e); }
  }

  function saveEntries() { localStorage.setItem(STORAGE_KEYS.entries, JSON.stringify(entries)); }
  function saveBooks() { localStorage.setItem(STORAGE_KEYS.books, JSON.stringify(books)); }
  function saveSettings() { localStorage.setItem(STORAGE_KEYS.settings, JSON.stringify(settings)); }

  function generateId() { return Date.now().toString(36) + Math.random().toString(36).substr(2, 5); }
  function getTotalPages() { return books.reduce((s, b) => s + (b.totalPages || 0), 0); }
  function getTotalTarget() { return Math.ceil(getTotalPages() * (1 + settings.reviewPercent / 100)); }
  function getTotalRead() { return entries.reduce((s, e) => s + (e.pages || 0), 0); }
  function getBookRead(bookId) { return entries.filter(e => e.bookId === bookId).reduce((s, e) => s + (e.pages || 0), 0); }
  function getBookById(bookId) { return books.find(b => b.id === bookId); }
  function getWorkingDaysPerMonth() { return 30 - settings.shiftDays - settings.restDays; }
  function getWorkingEntries() { return entries.filter(e => e.type === 'calisma' && e.pages > 0); }

  function formatDate(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' });
  }

  function formatFullDate(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  function getTodayStr() {
    const n = new Date();
    return n.getFullYear() + '-' + String(n.getMonth()+1).padStart(2,'0') + '-' + String(n.getDate()).padStart(2,'0');
  }

  function dateToStr(d) {
    return d.getFullYear() + '-' + String(d.getMonth()+1).padStart(2,'0') + '-' + String(d.getDate()).padStart(2,'0');
  }

  function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove('show'), 3000);
  }

  // ===== Firebase Sync =====
  async function syncFromFirebase() {
    if (!window.FirebaseSync) return;
    const data = await FirebaseSync.fetchAll();
    if (data) {
      if (data.entries && Array.isArray(data.entries)) { entries = data.entries; saveEntries(); }
      if (data.books && Array.isArray(data.books)) { books = data.books; saveBooks(); }
      if (data.settings) { settings = { ...DEFAULT_SETTINGS, ...data.settings }; saveSettings(); }
      loadSettingsToUI();
      populateBookSelectors();
      updateDashboard();
      renderBooksList();
      populateMonthFilter();
    }
    updateSyncStatus();
  }

  async function syncToFirebase() {
    if (!window.FirebaseSync) return;
    await FirebaseSync.saveAll({ entries, books, settings });
    updateSyncStatus();
  }

  function updateSyncStatus() {
    const el = document.getElementById('syncStatus');
    if (el && window.FirebaseSync) {
      el.innerHTML = FirebaseSync.getStatusHTML();
    }
  }

  // ===== Navigation =====
  function initNavigation() {
    document.querySelectorAll('.nav-tab').forEach(tab => {
      tab.addEventListener('click', () => {
        const page = tab.dataset.page;
        document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById(`page-${page}`).classList.add('active');
        if (page === 'stats') renderStats();
        if (page === 'logs') renderAllEntries();
        if (page === 'books') renderBooksList();
        if (page === 'weekly') renderWeeklyReport();
      });
    });
  }

  // ===== Book Selectors =====
  function populateBookSelectors() {
    ['entryBook', 'editBook', 'filterBook'].forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;
      const v = el.value;
      el.innerHTML = id === 'filterBook' ? '<option value="all">Tüm Kitaplar</option>' : '<option value="">Kitap seç...</option>';
      books.forEach(b => { const o = document.createElement('option'); o.value = b.id; o.textContent = `📖 ${b.name}`; el.appendChild(o); });
      if (v) el.value = v;
    });
  }

  // ===== Books Management =====
  function addBook(name, totalPages, color) {
    books.push({ id: generateId(), name: name.trim(), totalPages: parseInt(totalPages), color, createdAt: getTodayStr() });
    saveBooks(); syncToFirebase();
    populateBookSelectors(); renderBooksList(); updateDashboard();
    showToast(`"${name}" kitabı eklendi! 📖`, 'success');
  }

  function deleteBook(bookId) {
    const book = getBookById(bookId); if (!book) return;
    const n = entries.filter(e => e.bookId === bookId).length;
    if (!confirm(`"${book.name}" silinsin?${n ? `\n⚠️ ${n} kayıt da silinecek!` : ''}`)) return;
    books = books.filter(b => b.id !== bookId);
    entries = entries.filter(e => e.bookId !== bookId);
    saveBooks(); saveEntries(); syncToFirebase();
    populateBookSelectors(); renderBooksList(); updateDashboard(); populateMonthFilter();
    showToast('Kitap silindi 🗑️', 'info');
  }

  function renderBooksList() {
    const container = document.getElementById('booksList');
    document.getElementById('booksTotalPages').textContent = getTotalPages().toLocaleString('tr-TR');
    document.getElementById('booksWithReview').textContent = getTotalTarget().toLocaleString('tr-TR');
    if (books.length === 0) { container.innerHTML = '<div class="empty-state"><div class="empty-icon">📚</div><p>Henüz kitap eklenmemiş.</p></div>'; return; }
    container.innerHTML = books.map(book => {
      const read = getBookRead(book.id);
      const target = Math.ceil(book.totalPages * (1 + settings.reviewPercent / 100));
      const pct = target > 0 ? Math.min(100, (read / target) * 100) : 0;
      return `<div class="book-item" style="border-left-color:${book.color}"><div class="book-item-left"><div class="book-item-info"><div class="book-item-name">${book.name}</div><div class="book-item-meta"><span>${book.totalPages.toLocaleString('tr-TR')} sayfa</span><span>📖 ${read.toLocaleString('tr-TR')} okundu</span></div></div></div><div class="book-item-progress"><span class="book-item-percent" style="color:${book.color}">%${pct.toFixed(1)}</span><div class="book-mini-progress"><div class="book-mini-progress-fill" style="width:${pct}%;background:${book.color}"></div></div></div><div class="book-item-actions"><button onclick="app.deleteBook('${book.id}')" title="Sil">🗑️</button></div></div>`;
    }).join('');
  }

  // ===== Dashboard =====
  function updateDashboard() {
    const totalTarget = getTotalTarget(), totalRead = getTotalRead();
    const remaining = Math.max(0, totalTarget - totalRead);
    const percent = totalTarget > 0 ? Math.min(100, (totalRead / totalTarget) * 100) : 0;
    document.getElementById('totalRead').textContent = totalRead.toLocaleString('tr-TR');
    document.getElementById('totalTarget').textContent = totalTarget.toLocaleString('tr-TR');

    const we = getWorkingEntries();
    const dailyAvg = we.length > 0 ? Math.round(we.reduce((s, e) => s + e.pages, 0) / we.length) : 0;
    document.getElementById('dailyAverage').textContent = dailyAvg;

    if (dailyAvg > 0 && remaining > 0) {
      const wdpm = getWorkingDaysPerMonth(), twd = Math.ceil(remaining / dailyAvg);
      const tm = twd / wdpm, tcd = Math.ceil(tm * 30);
      const ed = new Date(); ed.setDate(ed.getDate() + tcd);
      document.getElementById('estimatedEnd').textContent = ed.toLocaleDateString('tr-TR', { day:'numeric', month:'short', year:'numeric' });
      document.getElementById('remainingDays').textContent = `~${tcd} gün kaldı`;
    } else if (remaining <= 0 && totalTarget > 0) {
      document.getElementById('estimatedEnd').textContent = '🎉 Tamamlandı!';
      document.getElementById('remainingDays').textContent = 'Tebrikler!';
    } else {
      document.getElementById('estimatedEnd').textContent = '-';
      document.getElementById('remainingDays').textContent = 'Veri bekleniyor';
    }

    document.getElementById('currentStreak').textContent = calculateStreak();
    document.getElementById('progressPercent').textContent = percent.toFixed(1) + '%';
    document.getElementById('progressBar').style.width = percent + '%';
    document.getElementById('pagesRead').textContent = totalRead.toLocaleString('tr-TR');
    document.getElementById('pagesRemaining').textContent = remaining.toLocaleString('tr-TR');
    renderBookProgressBars();
    renderRecentEntries();
  }

  function renderBookProgressBars() {
    const c = document.getElementById('bookProgressBars');
    if (books.length === 0) { c.innerHTML = '<div class="empty-state" style="padding:24px"><div class="empty-icon">📚</div><p>Henüz kitap eklenmemiş. Kitaplar sekmesinden ekle!</p></div>'; return; }
    c.innerHTML = books.map(b => {
      const read = getBookRead(b.id), target = Math.ceil(b.totalPages * (1 + settings.reviewPercent / 100));
      const pct = target > 0 ? Math.min(100, (read / target) * 100) : 0;
      return `<div class="book-progress-item"><div class="book-progress-color" style="background:${b.color}"></div><span class="book-progress-name" title="${b.name}">${b.name}</span><div class="book-progress-bar-wrap"><div class="book-progress-bar-fill" style="width:${pct}%;background:${b.color}"></div></div><span class="book-progress-stats">${read} / ${target} (%${pct.toFixed(0)})</span></div>`;
    }).join('');
  }

  function calculateStreak() {
    if (entries.length === 0) return 0;
    const dm = {}; entries.forEach(e => { if (e.pages > 0) dm[e.date] = (dm[e.date]||0) + e.pages; });
    let streak = 0; const today = new Date(getTodayStr() + 'T00:00:00');
    for (let i = 0; i < 365; i++) {
      const cd = new Date(today); cd.setDate(cd.getDate() - i);
      const ds = dateToStr(cd);
      if (dm[ds]) { streak++; } else if (i === 0) { continue; } else { break; }
    }
    return streak;
  }

  function calculateLongestStreak() {
    const ds = new Set(); entries.forEach(e => { if (e.pages > 0) ds.add(e.date); });
    const dates = [...ds].sort(); if (dates.length === 0) return 0;
    let longest = 1, current = 1;
    for (let i = 1; i < dates.length; i++) {
      const diff = (new Date(dates[i]+'T00:00:00') - new Date(dates[i-1]+'T00:00:00')) / 86400000;
      if (diff === 1) { current++; longest = Math.max(longest, current); } else { current = 1; }
    }
    return longest;
  }

  // ===== Entry Rendering =====
  function createEntryHTML(entry, index) {
    const ti = TYPE_LABELS[entry.type] || TYPE_LABELS.calisma;
    const book = entry.bookId ? getBookById(entry.bookId) : null;
    const bb = book ? `<span class="entry-book-badge" style="background:${book.color}" title="${book.name}">${book.name}</span>` : '';
    return `<div class="entry-item"><div class="entry-left"><span class="entry-date">${formatDate(entry.date)}</span>${bb}<span class="entry-pages">${entry.pages} sayfa</span><span class="entry-type ${entry.type}">${ti.emoji} ${ti.text}</span>${entry.note ? `<span class="entry-note" title="${entry.note}">${entry.note}</span>` : ''}</div><div class="entry-actions"><button onclick="app.editEntry(${index})" title="Düzenle">✏️</button><button class="delete-btn" onclick="app.deleteEntry(${index})" title="Sil">🗑️</button></div></div>`;
  }

  function renderRecentEntries() {
    const c = document.getElementById('recentEntries');
    const sorted = [...entries].sort((a, b) => b.date.localeCompare(a.date)).slice(0, 7);
    if (sorted.length === 0) { c.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div><p>Henüz kayıt yok. İlk kaydını ekle!</p></div>'; return; }
    c.innerHTML = sorted.map(e => createEntryHTML(e, entries.indexOf(e))).join('');
  }

  function renderAllEntries() {
    const c = document.getElementById('allEntries');
    let f = [...entries];
    const ft = document.getElementById('filterType').value, fm = document.getElementById('filterMonth').value, fb = document.getElementById('filterBook').value;
    if (ft !== 'all') f = f.filter(e => e.type === ft);
    if (fm !== 'all') f = f.filter(e => e.date.startsWith(fm));
    if (fb !== 'all') f = f.filter(e => e.bookId === fb);
    f.sort((a, b) => b.date.localeCompare(a.date));
    if (f.length === 0) { c.innerHTML = '<div class="empty-state"><div class="empty-icon">📭</div><p>Kayıt bulunamadı.</p></div>'; return; }
    c.innerHTML = f.map(e => createEntryHTML(e, entries.indexOf(e))).join('');
  }

  function populateMonthFilter() {
    const s = document.getElementById('filterMonth');
    const months = [...new Set(entries.map(e => e.date.substring(0,7)))].sort().reverse();
    s.innerHTML = '<option value="all">Tüm Aylar</option>';
    months.forEach(m => { const [y, mo] = m.split('-'); const d = new Date(parseInt(y), parseInt(mo)-1, 1); s.innerHTML += `<option value="${m}">${d.toLocaleDateString('tr-TR', {month:'long', year:'numeric'})}</option>`; });
  }

  // ===== Entry CRUD =====
  function addEntry(entry) {
    const ei = entries.findIndex(e => e.date === entry.date && e.bookId === entry.bookId);
    if (ei >= 0) { entries[ei] = entry; showToast('Kayıt güncellendi! ✅'); }
    else { entries.push(entry); showToast('Kayıt eklendi! 🎉'); }
    saveEntries(); syncToFirebase(); updateDashboard(); populateMonthFilter();
  }

  function deleteEntry(index) {
    if (!confirm('Bu kaydı silmek istediğine emin misin?')) return;
    entries.splice(index, 1); saveEntries(); syncToFirebase();
    updateDashboard(); renderAllEntries(); populateMonthFilter();
    showToast('Kayıt silindi 🗑️', 'info');
  }

  function editEntry(index) {
    const e = entries[index]; if (!e) return;
    document.getElementById('editIndex').value = index;
    document.getElementById('editDate').value = e.date;
    document.getElementById('editPages').value = e.pages;
    document.getElementById('editType').value = e.type;
    document.getElementById('editNote').value = e.note || '';
    if (e.bookId) document.getElementById('editBook').value = e.bookId;
    document.getElementById('editModal').classList.add('active');
  }

  function saveEdit() {
    const i = parseInt(document.getElementById('editIndex').value);
    entries[i] = {
      date: document.getElementById('editDate').value,
      bookId: document.getElementById('editBook').value || null,
      pages: parseInt(document.getElementById('editPages').value) || 0,
      type: document.getElementById('editType').value,
      note: document.getElementById('editNote').value.trim()
    };
    saveEntries(); syncToFirebase(); updateDashboard(); renderAllEntries();
    document.getElementById('editModal').classList.remove('active');
    showToast('Kayıt güncellendi! ✅');
  }

  // ===== Weekly Report =====
  function getWeekDates(offset) {
    const today = new Date();
    const dayOfWeek = today.getDay(); // 0=Sun, 1=Mon
    const monday = new Date(today);
    monday.setDate(today.getDate() - (dayOfWeek === 0 ? 6 : dayOfWeek - 1) + (offset * 7));
    const dates = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(monday);
      d.setDate(monday.getDate() + i);
      dates.push(dateToStr(d));
    }
    return dates;
  }

  function renderWeeklyReport() {
    const weekDates = getWeekDates(currentWeekOffset);
    const startDate = weekDates[0], endDate = weekDates[6];

    // Title
    const isThisWeek = currentWeekOffset === 0;
    document.getElementById('weekTitle').textContent = isThisWeek ? '📅 Bu Hafta' : `📅 ${formatDate(startDate)} Haftası`;
    document.getElementById('weekRange').textContent = `${formatFullDate(startDate)} — ${formatFullDate(endDate)}`;

    // Get entries for this week
    const weekEntries = entries.filter(e => e.date >= startDate && e.date <= endDate);
    const totalPages = weekEntries.reduce((s, e) => s + (e.pages || 0), 0);
    const workDays = new Set(weekEntries.filter(e => e.pages > 0).map(e => e.date)).size;
    const weeklyGoal = settings.dailyGoal * 7;
    const goalPct = weeklyGoal > 0 ? Math.min(100, (totalPages / weeklyGoal) * 100) : 0;

    // Stats
    document.getElementById('weeklyTotal').textContent = totalPages;
    document.getElementById('weeklyAvg').textContent = workDays > 0 ? Math.round(totalPages / workDays) : 0;
    document.getElementById('weeklyDays').textContent = workDays;
    document.getElementById('weeklyGoalPercent').textContent = goalPct.toFixed(0) + '%';
    document.getElementById('weeklyGoalSub').textContent = `hedef: ${weeklyGoal} sayfa`;

    // Chart
    renderWeeklyChart(weekDates, weekEntries);

    // Book breakdown
    renderWeeklyBookBreakdown(weekEntries);

    // Day details
    renderWeeklyDayDetails(weekDates, weekEntries);
  }

  function renderWeeklyChart(weekDates, weekEntries) {
    const ctx = document.getElementById('weeklyChart').getContext('2d');
    if (weeklyChart) weeklyChart.destroy();

    const labels = weekDates.map(d => {
      const date = new Date(d + 'T00:00:00');
      return DAY_NAMES[date.getDay()].substring(0, 3);
    });

    const data = weekDates.map(d => weekEntries.filter(e => e.date === d).reduce((s, e) => s + (e.pages || 0), 0));

    weeklyChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Sayfa',
          data,
          backgroundColor: data.map(v => v >= settings.dailyGoal ? 'rgba(74, 222, 128, 0.6)' : 'rgba(124, 92, 252, 0.6)'),
          borderColor: data.map(v => v >= settings.dailyGoal ? 'rgba(74, 222, 128, 1)' : 'rgba(124, 92, 252, 1)'),
          borderWidth: 1, borderRadius: 6,
        }, {
          label: 'Hedef', data: Array(7).fill(settings.dailyGoal),
          type: 'line', borderColor: 'rgba(251, 146, 60, 0.5)', borderDash: [5, 5], borderWidth: 2, pointRadius: 0, fill: false,
        }]
      },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#9a94c8', font: { size: 11 } } } },
        scales: {
          x: { ticks: { color: '#6b6490' }, grid: { color: 'rgba(120, 100, 255, 0.06)' } },
          y: { ticks: { color: '#6b6490' }, grid: { color: 'rgba(120, 100, 255, 0.06)' } }
        }
      }
    });
  }

  function renderWeeklyBookBreakdown(weekEntries) {
    const c = document.getElementById('weeklyBookBreakdown');
    if (books.length === 0 || weekEntries.length === 0) {
      c.innerHTML = '<div class="empty-state" style="padding:16px"><p>Bu hafta kayıt yok</p></div>';
      return;
    }
    const bookMap = {};
    weekEntries.forEach(e => { if (e.bookId) bookMap[e.bookId] = (bookMap[e.bookId] || 0) + (e.pages || 0); });
    const maxPages = Math.max(...Object.values(bookMap), 1);

    c.innerHTML = books.filter(b => bookMap[b.id]).map(b => {
      const pages = bookMap[b.id] || 0;
      const pct = (pages / maxPages) * 100;
      return `<div class="weekly-book-bar"><div class="weekly-book-color" style="background:${b.color}"></div><span class="weekly-book-name">${b.name}</span><div class="weekly-book-fill-wrap"><div class="weekly-book-fill" style="width:${pct}%;background:${b.color}"></div></div><span class="weekly-book-pages">${pages} sayfa</span></div>`;
    }).join('') || '<div class="empty-state" style="padding:16px"><p>Bu hafta kayıt yok</p></div>';
  }

  function renderWeeklyDayDetails(weekDates, weekEntries) {
    const c = document.getElementById('weeklyDayDetails');
    c.innerHTML = weekDates.map(d => {
      const date = new Date(d + 'T00:00:00');
      const dayName = DAY_NAMES[date.getDay()];
      const dayEntries = weekEntries.filter(e => e.date === d);
      const totalPages = dayEntries.reduce((s, e) => s + (e.pages || 0), 0);
      const hasData = totalPages > 0;
      const bookBadges = dayEntries.filter(e => e.bookId && e.pages > 0).map(e => {
        const b = getBookById(e.bookId);
        return b ? `<span class="entry-book-badge" style="background:${b.color}">${b.name}: ${e.pages}s</span>` : '';
      }).join('');

      return `<div class="weekly-day-card ${hasData ? 'has-data' : 'no-data'}"><span class="weekly-day-name">${dayName}</span><span class="weekly-day-date">${formatDate(d)}</span><div class="weekly-day-books">${bookBadges || '<span style="font-size:0.8rem;color:var(--text-muted)">—</span>'}</div><span class="weekly-day-pages">${hasData ? totalPages + ' sayfa' : '—'}</span></div>`;
    }).join('');
  }

  // ===== Statistics =====
  function renderStats() {
    renderDailyChart(); renderMonthlyChart(); renderBookChart();
    renderStreakInfo(); renderBestDays(); renderScenarios();
  }

  function renderDailyChart() {
    const ctx = document.getElementById('dailyChart').getContext('2d');
    const labels = [], data = [], goalLine = [], today = new Date();
    for (let i = 29; i >= 0; i--) {
      const d = new Date(today); d.setDate(d.getDate() - i);
      const ds = dateToStr(d);
      labels.push(d.toLocaleDateString('tr-TR', { day:'numeric', month:'short' }));
      data.push(entries.filter(e => e.date === ds).reduce((s, e) => s + (e.pages||0), 0));
      goalLine.push(settings.dailyGoal);
    }
    if (dailyChart) dailyChart.destroy();
    dailyChart = new Chart(ctx, { type:'bar', data:{ labels, datasets:[
      { label:'Okunan Sayfa', data, backgroundColor:'rgba(124,92,252,0.6)', borderColor:'rgba(124,92,252,1)', borderWidth:1, borderRadius:4 },
      { label:'Günlük Hedef', data:goalLine, type:'line', borderColor:'rgba(251,146,60,0.6)', borderDash:[5,5], borderWidth:2, pointRadius:0, fill:false }
    ]}, options:{ responsive:true, maintainAspectRatio:false, plugins:{ legend:{ labels:{ color:'#9a94c8', font:{size:11} }}}, scales:{ x:{ ticks:{color:'#6b6490',font:{size:10},maxRotation:45}, grid:{color:'rgba(120,100,255,0.06)'}}, y:{ ticks:{color:'#6b6490'}, grid:{color:'rgba(120,100,255,0.06)'}}}}});
  }

  function renderMonthlyChart() {
    const ctx = document.getElementById('monthlyChart').getContext('2d');
    const mm = {}; entries.forEach(e => { const m = e.date.substring(0,7); mm[m] = (mm[m]||0) + (e.pages||0); });
    const months = Object.keys(mm).sort();
    const labels = months.map(m => { const [y,mo] = m.split('-'); return new Date(parseInt(y),parseInt(mo)-1,1).toLocaleDateString('tr-TR',{month:'short',year:'2-digit'}); });
    if (monthlyChart) monthlyChart.destroy();
    if (months.length === 0) { monthlyChart = new Chart(ctx, {type:'bar',data:{labels:['Veri yok'],datasets:[{data:[0],backgroundColor:'rgba(124,92,252,0.3)'}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}}); return; }
    monthlyChart = new Chart(ctx, {type:'bar', data:{ labels, datasets:[{label:'Toplam Sayfa', data:months.map(m=>mm[m]), backgroundColor:ctx2=>{const g=ctx2.chart.ctx.createLinearGradient(0,0,0,280);g.addColorStop(0,'rgba(79,140,255,0.8)');g.addColorStop(1,'rgba(56,217,217,0.4)');return g;}, borderRadius:6}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:'#9a94c8',font:{size:11}}}},scales:{x:{ticks:{color:'#6b6490'},grid:{color:'rgba(120,100,255,0.06)'}},y:{ticks:{color:'#6b6490'},grid:{color:'rgba(120,100,255,0.06)'}}}}});
  }

  function renderBookChart() {
    const ctx = document.getElementById('bookChart').getContext('2d');
    if (bookChart) bookChart.destroy();
    if (books.length === 0) { bookChart = new Chart(ctx, {type:'doughnut',data:{labels:['Kitap yok'],datasets:[{data:[1],backgroundColor:['rgba(124,92,252,0.2)']}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}}}}); return; }
    const bd = books.map(b => ({name:b.name,read:getBookRead(b.id),color:b.color}));
    bookChart = new Chart(ctx, {type:'doughnut', data:{ labels:bd.map(b=>b.name), datasets:[{data:bd.map(b=>b.read||0), backgroundColor:bd.map(b=>b.color), borderColor:'rgba(10,10,26,0.8)', borderWidth:3}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{color:'#9a94c8',font:{size:11},padding:12}}}}});
  }

  function renderStreakInfo() {
    document.getElementById('streakNumber').textContent = calculateStreak();
    document.getElementById('longestStreak').textContent = calculateLongestStreak();
  }

  function renderBestDays() {
    const c = document.getElementById('bestDays');
    const dm = {}; entries.forEach(e => { if (e.pages > 0) dm[e.date] = (dm[e.date]||0) + e.pages; });
    const sorted = Object.entries(dm).map(([d,p])=>({date:d,pages:p})).sort((a,b)=>b.pages-a.pages).slice(0,5);
    if (sorted.length === 0) { c.innerHTML = '<div class="empty-state"><p>Henüz veri yok</p></div>'; return; }
    const medals = ['🥇','🥈','🥉','4️⃣','5️⃣'];
    c.innerHTML = sorted.map((e,i) => `<div class="best-day-item"><span class="best-day-rank">${medals[i]}</span><span class="best-day-date">${formatFullDate(e.date)}</span><span class="best-day-pages">${e.pages} sayfa</span></div>`).join('');
  }

  function renderScenarios() {
    const tbody = document.getElementById('scenariosBody');
    const rem = Math.max(0, getTotalTarget() - getTotalRead()), wdpm = getWorkingDaysPerMonth();
    const we = getWorkingEntries();
    const ca = we.length > 0 ? Math.round(we.reduce((s,e)=>s+e.pages,0)/we.length) : 0;
    tbody.innerHTML = [50,75,100,125,150].map(p => {
      const twd = Math.ceil(rem/p), tm = twd/wdpm, tcd = Math.ceil(tm*30);
      const ed = new Date(); ed.setDate(ed.getDate()+tcd);
      const ic = ca > 0 && Math.abs(p-ca) === Math.min(...[50,75,100,125,150].map(s=>Math.abs(s-ca)));
      return `<tr class="${ic?'highlighted':''}"><td>${p} sayfa/gün ${ic?'← Şu anki hız':''}</td><td>${twd} gün</td><td>~${tm.toFixed(1)} ay</td><td>${rem>0?ed.toLocaleDateString('tr-TR',{day:'numeric',month:'short',year:'numeric'}):'✅ Bitti!'}</td></tr>`;
    }).join('');
  }

  // ===== Settings =====
  function loadSettingsToUI() {
    document.getElementById('settingReviewPercent').value = settings.reviewPercent;
    document.getElementById('settingDailyGoal').value = settings.dailyGoal;
    document.getElementById('settingShiftDays').value = settings.shiftDays;
    document.getElementById('settingRestDays').value = settings.restDays;
    document.getElementById('settingStudentName').value = settings.studentName || '';
  }

  function saveSettingsFromUI() {
    settings.reviewPercent = parseInt(document.getElementById('settingReviewPercent').value) || 0;
    settings.dailyGoal = parseInt(document.getElementById('settingDailyGoal').value) || DEFAULT_SETTINGS.dailyGoal;
    settings.shiftDays = parseInt(document.getElementById('settingShiftDays').value) || 0;
    settings.restDays = parseInt(document.getElementById('settingRestDays').value) || 0;
    settings.studentName = document.getElementById('settingStudentName').value.trim();
    saveSettings(); syncToFirebase(); updateDashboard(); renderBooksList(); updateMotivation();
    showToast('Ayarlar kaydedildi! ⚙️');
  }

  // ===== Data Import/Export =====
  function exportData() {
    const blob = new Blob([JSON.stringify({ entries, books, settings, exportDate: new Date().toISOString(), version: '3.0' }, null, 2)], { type: 'application/json' });
    const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = `tus-takip-yedek-${getTodayStr()}.json`; a.click();
    showToast('Veriler dışa aktarıldı! 📤');
  }

  function importData(file) {
    const r = new FileReader();
    r.onload = function(e) {
      try {
        const d = JSON.parse(e.target.result);
        if (d.entries) { entries = d.entries; saveEntries(); }
        if (d.books) { books = d.books; saveBooks(); }
        if (d.settings) { settings = { ...DEFAULT_SETTINGS, ...d.settings }; saveSettings(); loadSettingsToUI(); }
        syncToFirebase(); populateBookSelectors(); updateDashboard(); renderBooksList(); populateMonthFilter();
        showToast('Veriler içe aktarıldı! 📥');
      } catch { showToast('Dosya okunamadı! ❌', 'error'); }
    };
    r.readAsText(file);
  }

  function clearAllData() {
    if (!confirm('⚠️ Tüm veriler silinecek!')) return;
    if (!confirm('Son onay: Gerçekten silinsin mi?')) return;
    entries = []; books = []; settings = { ...DEFAULT_SETTINGS };
    saveEntries(); saveBooks(); saveSettings(); syncToFirebase();
    loadSettingsToUI(); populateBookSelectors(); updateDashboard(); renderBooksList(); populateMonthFilter();
    showToast('Tüm veriler silindi 🗑️', 'info');
  }

  // ===== Motivation =====
  function updateMotivation() {
    const name = settings.studentName;
    let q = MOTIVATIONAL_QUOTES[Math.floor(Math.random() * MOTIVATIONAL_QUOTES.length)];
    if (name) q = `${name}, ${q.charAt(0).toLowerCase()}${q.slice(1)}`;
    document.getElementById('motivationText').textContent = q;
  }

  // ===== Init =====
  function init() {
    loadData();
    document.getElementById('entryDate').value = getTodayStr();
    initNavigation();

    // Color picker
    document.querySelectorAll('.color-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active'); selectedBookColor = this.dataset.color;
      });
    });

    // Add Book
    document.getElementById('addBookForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const n = document.getElementById('bookName').value.trim(), p = document.getElementById('bookPages').value;
      if (!n || !p) { showToast('Kitap adı ve sayfa gerekli!', 'error'); return; }
      addBook(n, p, selectedBookColor);
      document.getElementById('bookName').value = ''; document.getElementById('bookPages').value = '';
    });

    // Quick Add
    document.getElementById('quickAddForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const bookId = document.getElementById('entryBook').value;
      if (!bookId) { showToast('Bir kitap seç! 📖', 'error'); return; }
      addEntry({
        date: document.getElementById('entryDate').value, bookId,
        pages: parseInt(document.getElementById('entryPages').value) || 0,
        type: document.getElementById('entryType').value,
        note: document.getElementById('entryNote').value.trim()
      });
      document.getElementById('entryPages').value = ''; document.getElementById('entryNote').value = '';
      document.getElementById('entryDate').value = getTodayStr();
    });

    // Edit
    document.getElementById('editForm').addEventListener('submit', function(e) { e.preventDefault(); saveEdit(); });
    document.getElementById('cancelEdit').addEventListener('click', () => document.getElementById('editModal').classList.remove('active'));
    document.getElementById('editModal').addEventListener('click', function(e) { if (e.target === this) this.classList.remove('active'); });

    // Filters
    document.getElementById('filterType').addEventListener('change', renderAllEntries);
    document.getElementById('filterMonth').addEventListener('change', renderAllEntries);
    document.getElementById('filterBook').addEventListener('change', renderAllEntries);

    // Weekly navigation
    document.getElementById('prevWeek').addEventListener('click', () => { currentWeekOffset--; renderWeeklyReport(); });
    document.getElementById('nextWeek').addEventListener('click', () => { if (currentWeekOffset < 0) { currentWeekOffset++; renderWeeklyReport(); } });

    // Settings
    document.getElementById('saveSettings').addEventListener('click', saveSettingsFromUI);
    document.getElementById('syncNow').addEventListener('click', async () => {
      showToast('Senkronize ediliyor...', 'info');
      await syncFromFirebase(); showToast('Senkronizasyon tamamlandı! 🔄');
    });

    // Data management
    document.getElementById('exportData').addEventListener('click', exportData);
    document.getElementById('importDataBtn').addEventListener('click', () => document.getElementById('importDataFile').click());
    document.getElementById('importDataFile').addEventListener('change', function(e) { if (e.target.files[0]) { importData(e.target.files[0]); e.target.value = ''; } });
    document.getElementById('clearData').addEventListener('click', clearAllData);

    // Load UI
    loadSettingsToUI(); populateBookSelectors(); updateDashboard(); renderBooksList(); populateMonthFilter(); updateMotivation();

    // Firebase: load from cloud on startup
    syncFromFirebase();

    // Auto-sync every 30 seconds
    setInterval(async () => {
      await syncFromFirebase();
    }, 30000);

    // Sync on page focus (when user comes back to tab)
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) syncFromFirebase();
    });
  }

  // Public API
  window.app = { editEntry, deleteEntry, deleteBook };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
