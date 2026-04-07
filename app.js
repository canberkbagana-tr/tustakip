// ===== TUS Takip - Main Application (v2 - Book Tracking) =====

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

  // ===== State =====
  let entries = [];
  let books = [];
  let settings = { ...DEFAULT_SETTINGS };
  let dailyChart = null;
  let monthlyChart = null;
  let bookChart = null;
  let selectedBookColor = '#7c5cfc';

  // ===== Helpers =====
  function loadData() {
    try {
      const savedEntries = localStorage.getItem(STORAGE_KEYS.entries);
      if (savedEntries) entries = JSON.parse(savedEntries);

      const savedBooks = localStorage.getItem(STORAGE_KEYS.books);
      if (savedBooks) books = JSON.parse(savedBooks);

      const savedSettings = localStorage.getItem(STORAGE_KEYS.settings);
      if (savedSettings) settings = { ...DEFAULT_SETTINGS, ...JSON.parse(savedSettings) };
    } catch (e) {
      console.error('Veri yükleme hatası:', e);
    }
  }

  function saveEntries() {
    localStorage.setItem(STORAGE_KEYS.entries, JSON.stringify(entries));
  }

  function saveBooks() {
    localStorage.setItem(STORAGE_KEYS.books, JSON.stringify(books));
  }

  function saveSettings() {
    localStorage.setItem(STORAGE_KEYS.settings, JSON.stringify(settings));
  }

  function generateId() {
    return Date.now().toString(36) + Math.random().toString(36).substr(2, 5);
  }

  function getTotalPages() {
    return books.reduce((sum, b) => sum + (b.totalPages || 0), 0);
  }

  function getTotalTarget() {
    return Math.ceil(getTotalPages() * (1 + settings.reviewPercent / 100));
  }

  function getTotalRead() {
    return entries.reduce((sum, e) => sum + (e.pages || 0), 0);
  }

  function getBookRead(bookId) {
    return entries.filter(e => e.bookId === bookId).reduce((sum, e) => sum + (e.pages || 0), 0);
  }

  function getBookById(bookId) {
    return books.find(b => b.id === bookId);
  }

  function getWorkingDaysPerMonth() {
    return 30 - settings.shiftDays - settings.restDays;
  }

  function getWorkingEntries() {
    return entries.filter(e => e.type === 'calisma' && e.pages > 0);
  }

  function formatDate(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' });
  }

  function formatFullDate(dateStr) {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' });
  }

  function getTodayStr() {
    const now = new Date();
    return now.getFullYear() + '-' +
      String(now.getMonth() + 1).padStart(2, '0') + '-' +
      String(now.getDate()).padStart(2, '0');
  }

  function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => toast.classList.remove('show'), 3000);
  }

  // ===== Navigation =====
  function initNavigation() {
    const tabs = document.querySelectorAll('.nav-tab');
    tabs.forEach(tab => {
      tab.addEventListener('click', () => {
        const page = tab.dataset.page;
        tabs.forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
        document.getElementById(`page-${page}`).classList.add('active');

        if (page === 'stats') renderStats();
        if (page === 'logs') renderAllEntries();
        if (page === 'books') renderBooksList();
      });
    });
  }

  // ===== Book Selectors =====
  function populateBookSelectors() {
    const selectors = ['entryBook', 'editBook', 'filterBook'];
    selectors.forEach(id => {
      const el = document.getElementById(id);
      if (!el) return;

      const currentVal = el.value;
      if (id === 'filterBook') {
        el.innerHTML = '<option value="all">Tüm Kitaplar</option>';
      } else {
        el.innerHTML = '<option value="">Kitap seç...</option>';
      }

      books.forEach(b => {
        const opt = document.createElement('option');
        opt.value = b.id;
        opt.textContent = `📖 ${b.name}`;
        el.appendChild(opt);
      });

      if (currentVal) el.value = currentVal;
    });
  }

  // ===== Books Management =====
  function addBook(name, totalPages, color) {
    const book = {
      id: generateId(),
      name: name.trim(),
      totalPages: parseInt(totalPages),
      color: color,
      createdAt: getTodayStr()
    };
    books.push(book);
    saveBooks();
    populateBookSelectors();
    renderBooksList();
    updateDashboard();
    showToast(`"${book.name}" kitabı eklendi! 📖`, 'success');
  }

  function deleteBook(bookId) {
    const book = getBookById(bookId);
    if (!book) return;

    const bookEntries = entries.filter(e => e.bookId === bookId);
    let msg = `"${book.name}" kitabını silmek istediğine emin misin?`;
    if (bookEntries.length > 0) {
      msg += `\n\n⚠️ Bu kitaba ait ${bookEntries.length} kayıt da silinecek!`;
    }

    if (confirm(msg)) {
      books = books.filter(b => b.id !== bookId);
      entries = entries.filter(e => e.bookId !== bookId);
      saveBooks();
      saveEntries();
      populateBookSelectors();
      renderBooksList();
      updateDashboard();
      populateMonthFilter();
      showToast('Kitap silindi 🗑️', 'info');
    }
  }

  function renderBooksList() {
    const container = document.getElementById('booksList');
    const totalPagesEl = document.getElementById('booksTotalPages');
    const withReviewEl = document.getElementById('booksWithReview');

    const total = getTotalPages();
    totalPagesEl.textContent = total.toLocaleString('tr-TR');
    withReviewEl.textContent = getTotalTarget().toLocaleString('tr-TR');

    if (books.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📚</div>
          <p>Henüz kitap eklenmemiş. Yukarıdan ilk kitabını ekle!</p>
        </div>
      `;
      return;
    }

    container.innerHTML = books.map(book => {
      const read = getBookRead(book.id);
      const bookTarget = Math.ceil(book.totalPages * (1 + settings.reviewPercent / 100));
      const percent = bookTarget > 0 ? Math.min(100, (read / bookTarget) * 100) : 0;

      return `
        <div class="book-item" style="border-left-color: ${book.color}">
          <div class="book-item-left">
            <div class="book-item-info">
              <div class="book-item-name">${book.name}</div>
              <div class="book-item-meta">
                <span>${book.totalPages.toLocaleString('tr-TR')} sayfa</span>
                <span>📖 ${read.toLocaleString('tr-TR')} okundu</span>
              </div>
            </div>
          </div>
          <div class="book-item-progress">
            <span class="book-item-percent" style="color: ${book.color}">%${percent.toFixed(1)}</span>
            <div class="book-mini-progress">
              <div class="book-mini-progress-fill" style="width:${percent}%; background:${book.color}"></div>
            </div>
          </div>
          <div class="book-item-actions">
            <button onclick="app.deleteBook('${book.id}')" title="Sil">🗑️</button>
          </div>
        </div>
      `;
    }).join('');
  }

  // ===== Dashboard =====
  function updateDashboard() {
    const totalTarget = getTotalTarget();
    const totalRead = getTotalRead();
    const remaining = Math.max(0, totalTarget - totalRead);
    const percent = totalTarget > 0 ? Math.min(100, (totalRead / totalTarget) * 100) : 0;

    // Stat cards
    document.getElementById('totalRead').textContent = totalRead.toLocaleString('tr-TR');
    document.getElementById('totalTarget').textContent = totalTarget.toLocaleString('tr-TR');

    // Daily average
    const workEntries = getWorkingEntries();
    const dailyAvg = workEntries.length > 0
      ? Math.round(workEntries.reduce((s, e) => s + e.pages, 0) / workEntries.length)
      : 0;
    document.getElementById('dailyAverage').textContent = dailyAvg;

    // Estimated end
    if (dailyAvg > 0 && remaining > 0) {
      const workDaysPerMonth = getWorkingDaysPerMonth();
      const totalWorkDays = Math.ceil(remaining / dailyAvg);
      const totalMonths = totalWorkDays / workDaysPerMonth;
      const totalCalendarDays = Math.ceil(totalMonths * 30);

      const endDate = new Date();
      endDate.setDate(endDate.getDate() + totalCalendarDays);
      document.getElementById('estimatedEnd').textContent =
        endDate.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });
      document.getElementById('remainingDays').textContent = `~${totalCalendarDays} gün kaldı`;
    } else if (remaining <= 0 && totalTarget > 0) {
      document.getElementById('estimatedEnd').textContent = '🎉 Tamamlandı!';
      document.getElementById('remainingDays').textContent = 'Tebrikler!';
    } else {
      document.getElementById('estimatedEnd').textContent = '-';
      document.getElementById('remainingDays').textContent = 'Veri bekleniyor';
    }

    // Streak
    const streak = calculateStreak();
    document.getElementById('currentStreak').textContent = streak;

    // Progress bar
    document.getElementById('progressPercent').textContent = percent.toFixed(1) + '%';
    document.getElementById('progressBar').style.width = percent + '%';
    document.getElementById('pagesRead').textContent = totalRead.toLocaleString('tr-TR');
    document.getElementById('pagesRemaining').textContent = remaining.toLocaleString('tr-TR');

    // Per-book progress
    renderBookProgressBars();

    // Recent entries
    renderRecentEntries();
  }

  function renderBookProgressBars() {
    const container = document.getElementById('bookProgressBars');

    if (books.length === 0) {
      container.innerHTML = `
        <div class="empty-state" style="padding:24px">
          <div class="empty-icon">📚</div>
          <p>Henüz kitap eklenmemiş. Kitaplar sekmesinden ekle!</p>
        </div>
      `;
      return;
    }

    container.innerHTML = books.map(book => {
      const read = getBookRead(book.id);
      const bookTarget = Math.ceil(book.totalPages * (1 + settings.reviewPercent / 100));
      const percent = bookTarget > 0 ? Math.min(100, (read / bookTarget) * 100) : 0;

      return `
        <div class="book-progress-item">
          <div class="book-progress-color" style="background:${book.color}"></div>
          <span class="book-progress-name" title="${book.name}">${book.name}</span>
          <div class="book-progress-bar-wrap">
            <div class="book-progress-bar-fill" style="width:${percent}%; background:${book.color}"></div>
          </div>
          <span class="book-progress-stats">${read} / ${bookTarget} (%${percent.toFixed(0)})</span>
        </div>
      `;
    }).join('');
  }

  function calculateStreak() {
    if (entries.length === 0) return 0;

    // Aggregate pages per date
    const dateMap = {};
    entries.forEach(e => {
      if (e.pages > 0) {
        dateMap[e.date] = (dateMap[e.date] || 0) + e.pages;
      }
    });

    let streak = 0;
    const today = new Date(getTodayStr() + 'T00:00:00');

    for (let i = 0; i < 365; i++) {
      const checkDate = new Date(today);
      checkDate.setDate(checkDate.getDate() - i);
      const dateStr = checkDate.getFullYear() + '-' +
        String(checkDate.getMonth() + 1).padStart(2, '0') + '-' +
        String(checkDate.getDate()).padStart(2, '0');

      if (dateMap[dateStr]) {
        streak++;
      } else if (i === 0) {
        continue;
      } else {
        break;
      }
    }
    return streak;
  }

  function calculateLongestStreak() {
    if (entries.length === 0) return 0;

    const dateSet = new Set();
    entries.forEach(e => { if (e.pages > 0) dateSet.add(e.date); });
    const dates = [...dateSet].sort();
    if (dates.length === 0) return 0;

    let longest = 1;
    let current = 1;

    for (let i = 1; i < dates.length; i++) {
      const prev = new Date(dates[i - 1] + 'T00:00:00');
      const curr = new Date(dates[i] + 'T00:00:00');
      const diffDays = (curr - prev) / (1000 * 60 * 60 * 24);

      if (diffDays === 1) {
        current++;
        longest = Math.max(longest, current);
      } else {
        current = 1;
      }
    }
    return longest;
  }

  // ===== Entry Rendering =====
  function createEntryHTML(entry, index, showActions = true) {
    const typeInfo = TYPE_LABELS[entry.type] || TYPE_LABELS.calisma;
    const book = entry.bookId ? getBookById(entry.bookId) : null;

    const bookBadge = book
      ? `<span class="entry-book-badge" style="background:${book.color}" title="${book.name}">${book.name}</span>`
      : '';

    const actionsHTML = showActions ? `
      <div class="entry-actions">
        <button onclick="app.editEntry(${index})" title="Düzenle">✏️</button>
        <button class="delete-btn" onclick="app.deleteEntry(${index})" title="Sil">🗑️</button>
      </div>
    ` : '';

    return `
      <div class="entry-item">
        <div class="entry-left">
          <span class="entry-date">${formatDate(entry.date)}</span>
          ${bookBadge}
          <span class="entry-pages">${entry.pages} sayfa</span>
          <span class="entry-type ${entry.type}">${typeInfo.emoji} ${typeInfo.text}</span>
          ${entry.note ? `<span class="entry-note" title="${entry.note}">${entry.note}</span>` : ''}
        </div>
        ${actionsHTML}
      </div>
    `;
  }

  function renderRecentEntries() {
    const container = document.getElementById('recentEntries');
    const sorted = [...entries].sort((a, b) => b.date.localeCompare(a.date));
    const recent = sorted.slice(0, 7);

    if (recent.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📭</div>
          <p>Henüz kayıt yok. İlk kaydını ekle!</p>
        </div>
      `;
      return;
    }

    container.innerHTML = recent.map(e => {
      const origIndex = entries.indexOf(e);
      return createEntryHTML(e, origIndex);
    }).join('');
  }

  function renderAllEntries() {
    const container = document.getElementById('allEntries');
    const filterType = document.getElementById('filterType').value;
    const filterMonth = document.getElementById('filterMonth').value;
    const filterBook = document.getElementById('filterBook').value;

    let filtered = [...entries];

    if (filterType !== 'all') {
      filtered = filtered.filter(e => e.type === filterType);
    }

    if (filterMonth !== 'all') {
      filtered = filtered.filter(e => e.date.startsWith(filterMonth));
    }

    if (filterBook !== 'all') {
      filtered = filtered.filter(e => e.bookId === filterBook);
    }

    filtered.sort((a, b) => b.date.localeCompare(a.date));

    if (filtered.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">📭</div>
          <p>Bu filtrelere uygun kayıt bulunamadı.</p>
        </div>
      `;
      return;
    }

    container.innerHTML = filtered.map(e => {
      const origIndex = entries.indexOf(e);
      return createEntryHTML(e, origIndex);
    }).join('');
  }

  function populateMonthFilter() {
    const select = document.getElementById('filterMonth');
    const months = [...new Set(entries.map(e => e.date.substring(0, 7)))].sort().reverse();

    select.innerHTML = '<option value="all">Tüm Aylar</option>';
    months.forEach(m => {
      const [y, mo] = m.split('-');
      const date = new Date(parseInt(y), parseInt(mo) - 1, 1);
      const label = date.toLocaleDateString('tr-TR', { month: 'long', year: 'numeric' });
      select.innerHTML += `<option value="${m}">${label}</option>`;
    });
  }

  // ===== Entry CRUD =====
  function addEntry(entry) {
    // No more date-uniqueness: same date + different books = multiple entries
    // But same date + same book = update
    const existingIndex = entries.findIndex(e => e.date === entry.date && e.bookId === entry.bookId);
    if (existingIndex >= 0) {
      entries[existingIndex] = entry;
      showToast('Kayıt güncellendi! ✅', 'success');
    } else {
      entries.push(entry);
      showToast('Kayıt eklendi! 🎉', 'success');
    }
    saveEntries();
    updateDashboard();
    populateMonthFilter();
  }

  function deleteEntry(index) {
    if (confirm('Bu kaydı silmek istediğine emin misin?')) {
      entries.splice(index, 1);
      saveEntries();
      updateDashboard();
      renderAllEntries();
      populateMonthFilter();
      showToast('Kayıt silindi 🗑️', 'info');
    }
  }

  function editEntry(index) {
    const entry = entries[index];
    if (!entry) return;

    document.getElementById('editIndex').value = index;
    document.getElementById('editDate').value = entry.date;
    document.getElementById('editPages').value = entry.pages;
    document.getElementById('editType').value = entry.type;
    document.getElementById('editNote').value = entry.note || '';
    if (entry.bookId) {
      document.getElementById('editBook').value = entry.bookId;
    }

    document.getElementById('editModal').classList.add('active');
  }

  function saveEdit() {
    const index = parseInt(document.getElementById('editIndex').value);
    entries[index] = {
      date: document.getElementById('editDate').value,
      bookId: document.getElementById('editBook').value || null,
      pages: parseInt(document.getElementById('editPages').value) || 0,
      type: document.getElementById('editType').value,
      note: document.getElementById('editNote').value.trim()
    };
    saveEntries();
    updateDashboard();
    renderAllEntries();
    document.getElementById('editModal').classList.remove('active');
    showToast('Kayıt güncellendi! ✅', 'success');
  }

  // ===== Statistics =====
  function renderStats() {
    renderDailyChart();
    renderMonthlyChart();
    renderBookChart();
    renderStreakInfo();
    renderBestDays();
    renderScenarios();
  }

  function renderDailyChart() {
    const ctx = document.getElementById('dailyChart').getContext('2d');

    // Last 30 days - aggregate across all books per day
    const labels = [];
    const data = [];
    const goalLine = [];
    const today = new Date();

    for (let i = 29; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(d.getDate() - i);
      const dateStr = d.getFullYear() + '-' +
        String(d.getMonth() + 1).padStart(2, '0') + '-' +
        String(d.getDate()).padStart(2, '0');

      labels.push(d.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' }));

      const dayTotal = entries
        .filter(e => e.date === dateStr)
        .reduce((sum, e) => sum + (e.pages || 0), 0);
      data.push(dayTotal);
      goalLine.push(settings.dailyGoal);
    }

    if (dailyChart) dailyChart.destroy();

    dailyChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [
          {
            label: 'Okunan Sayfa',
            data,
            backgroundColor: 'rgba(124, 92, 252, 0.6)',
            borderColor: 'rgba(124, 92, 252, 1)',
            borderWidth: 1,
            borderRadius: 4,
          },
          {
            label: 'Günlük Hedef',
            data: goalLine,
            type: 'line',
            borderColor: 'rgba(251, 146, 60, 0.6)',
            borderDash: [5, 5],
            borderWidth: 2,
            pointRadius: 0,
            fill: false,
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { labels: { color: '#9a94c8', font: { size: 11 } } }
        },
        scales: {
          x: {
            ticks: { color: '#6b6490', font: { size: 10 }, maxRotation: 45 },
            grid: { color: 'rgba(120, 100, 255, 0.06)' }
          },
          y: {
            ticks: { color: '#6b6490' },
            grid: { color: 'rgba(120, 100, 255, 0.06)' }
          }
        }
      }
    });
  }

  function renderMonthlyChart() {
    const ctx = document.getElementById('monthlyChart').getContext('2d');

    const monthMap = {};
    entries.forEach(e => {
      const m = e.date.substring(0, 7);
      if (!monthMap[m]) monthMap[m] = 0;
      monthMap[m] += e.pages || 0;
    });

    const months = Object.keys(monthMap).sort();
    const labels = months.map(m => {
      const [y, mo] = m.split('-');
      const d = new Date(parseInt(y), parseInt(mo) - 1, 1);
      return d.toLocaleDateString('tr-TR', { month: 'short', year: '2-digit' });
    });

    if (monthlyChart) monthlyChart.destroy();

    if (months.length === 0) {
      monthlyChart = new Chart(ctx, {
        type: 'bar',
        data: { labels: ['Veri yok'], datasets: [{ data: [0], backgroundColor: 'rgba(124, 92, 252, 0.3)' }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
      });
      return;
    }

    monthlyChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Toplam Sayfa',
          data: months.map(m => monthMap[m]),
          backgroundColor: (ctx) => {
            const gradient = ctx.chart.ctx.createLinearGradient(0, 0, 0, 280);
            gradient.addColorStop(0, 'rgba(79, 140, 255, 0.8)');
            gradient.addColorStop(1, 'rgba(56, 217, 217, 0.4)');
            return gradient;
          },
          borderRadius: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { labels: { color: '#9a94c8', font: { size: 11 } } } },
        scales: {
          x: { ticks: { color: '#6b6490' }, grid: { color: 'rgba(120, 100, 255, 0.06)' } },
          y: { ticks: { color: '#6b6490' }, grid: { color: 'rgba(120, 100, 255, 0.06)' } }
        }
      }
    });
  }

  function renderBookChart() {
    const ctx = document.getElementById('bookChart').getContext('2d');

    if (bookChart) bookChart.destroy();

    if (books.length === 0) {
      bookChart = new Chart(ctx, {
        type: 'doughnut',
        data: { labels: ['Kitap yok'], datasets: [{ data: [1], backgroundColor: ['rgba(124, 92, 252, 0.2)'] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
      });
      return;
    }

    const bookData = books.map(b => ({
      name: b.name,
      read: getBookRead(b.id),
      color: b.color
    }));

    bookChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: bookData.map(b => b.name),
        datasets: [{
          data: bookData.map(b => b.read || 0),
          backgroundColor: bookData.map(b => b.color),
          borderColor: 'rgba(10, 10, 26, 0.8)',
          borderWidth: 3,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'right',
            labels: { color: '#9a94c8', font: { size: 11 }, padding: 12 }
          }
        }
      }
    });
  }

  function renderStreakInfo() {
    document.getElementById('streakNumber').textContent = calculateStreak();
    document.getElementById('longestStreak').textContent = calculateLongestStreak();
  }

  function renderBestDays() {
    const container = document.getElementById('bestDays');

    // Aggregate pages per date
    const dateMap = {};
    entries.forEach(e => {
      if (e.pages > 0) {
        if (!dateMap[e.date]) dateMap[e.date] = 0;
        dateMap[e.date] += e.pages;
      }
    });

    const sorted = Object.entries(dateMap)
      .map(([date, pages]) => ({ date, pages }))
      .sort((a, b) => b.pages - a.pages);

    const top5 = sorted.slice(0, 5);

    if (top5.length === 0) {
      container.innerHTML = '<div class="empty-state"><p>Henüz veri yok</p></div>';
      return;
    }

    const medals = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'];
    container.innerHTML = top5.map((e, i) => `
      <div class="best-day-item">
        <span class="best-day-rank">${medals[i]}</span>
        <span class="best-day-date">${formatFullDate(e.date)}</span>
        <span class="best-day-pages">${e.pages} sayfa</span>
      </div>
    `).join('');
  }

  function renderScenarios() {
    const tbody = document.getElementById('scenariosBody');
    const totalTarget = getTotalTarget();
    const totalRead = getTotalRead();
    const remaining = Math.max(0, totalTarget - totalRead);
    const workDaysPerMonth = getWorkingDaysPerMonth();

    const scenarios = [50, 75, 100, 125, 150];
    const workEntries = getWorkingEntries();
    const currentAvg = workEntries.length > 0
      ? Math.round(workEntries.reduce((s, e) => s + e.pages, 0) / workEntries.length)
      : 0;

    tbody.innerHTML = scenarios.map(pace => {
      const totalWorkDays = Math.ceil(remaining / pace);
      const totalMonths = totalWorkDays / workDaysPerMonth;
      const totalCalendarDays = Math.ceil(totalMonths * 30);

      const endDate = new Date();
      endDate.setDate(endDate.getDate() + totalCalendarDays);
      const endDateStr = endDate.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });

      const isClosest = currentAvg > 0 && Math.abs(pace - currentAvg) ===
        Math.min(...scenarios.map(s => Math.abs(s - currentAvg)));

      return `
        <tr class="${isClosest ? 'highlighted' : ''}">
          <td>${pace} sayfa/gün ${isClosest ? '← Şu anki hız' : ''}</td>
          <td>${totalWorkDays.toFixed(0)} gün</td>
          <td>~${totalMonths.toFixed(1)} ay</td>
          <td>${remaining > 0 ? endDateStr : '✅ Bitti!'}</td>
        </tr>
      `;
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

    saveSettings();
    updateDashboard();
    renderBooksList();
    updateMotivation();
    showToast('Ayarlar kaydedildi! ⚙️', 'success');
  }

  // ===== Data Import/Export =====
  function exportData() {
    const data = {
      entries,
      books,
      settings,
      exportDate: new Date().toISOString(),
      version: '2.0'
    };
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `tus-takip-yedek-${getTodayStr()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    showToast('Veriler dışa aktarıldı! 📤', 'success');
  }

  function importData(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      try {
        const data = JSON.parse(e.target.result);
        if (data.entries && Array.isArray(data.entries)) {
          entries = data.entries;
          saveEntries();
        }
        if (data.books && Array.isArray(data.books)) {
          books = data.books;
          saveBooks();
        }
        if (data.settings) {
          settings = { ...DEFAULT_SETTINGS, ...data.settings };
          saveSettings();
          loadSettingsToUI();
        }
        populateBookSelectors();
        updateDashboard();
        renderBooksList();
        populateMonthFilter();
        showToast('Veriler içe aktarıldı! 📥', 'success');
      } catch (err) {
        showToast('Dosya okunamadı! ❌', 'error');
      }
    };
    reader.readAsText(file);
  }

  function clearAllData() {
    if (confirm('⚠️ Tüm veriler silinecek! Bu işlem geri alınamaz. Emin misin?')) {
      if (confirm('Son kez onay: Gerçekten tüm verileri silmek istiyor musun?')) {
        entries = [];
        books = [];
        settings = { ...DEFAULT_SETTINGS };
        saveEntries();
        saveBooks();
        saveSettings();
        loadSettingsToUI();
        populateBookSelectors();
        updateDashboard();
        renderBooksList();
        populateMonthFilter();
        showToast('Tüm veriler silindi 🗑️', 'info');
      }
    }
  }

  // ===== Motivation =====
  function updateMotivation() {
    const name = settings.studentName;
    let quote = MOTIVATIONAL_QUOTES[Math.floor(Math.random() * MOTIVATIONAL_QUOTES.length)];
    if (name) {
      quote = `${name}, ${quote.charAt(0).toLowerCase()}${quote.slice(1)}`;
    }
    document.getElementById('motivationText').textContent = quote;
  }

  // ===== Init =====
  function init() {
    loadData();

    // Set today's date as default
    document.getElementById('entryDate').value = getTodayStr();

    // Navigation
    initNavigation();

    // Color picker for books
    document.querySelectorAll('.color-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        document.querySelectorAll('.color-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        selectedBookColor = this.dataset.color;
      });
    });

    // Add Book Form
    document.getElementById('addBookForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const name = document.getElementById('bookName').value.trim();
      const pages = document.getElementById('bookPages').value;
      if (!name || !pages) {
        showToast('Kitap adı ve sayfa sayısı gerekli! 📖', 'error');
        return;
      }
      addBook(name, pages, selectedBookColor);
      document.getElementById('bookName').value = '';
      document.getElementById('bookPages').value = '';
    });

    // Quick Add Form
    document.getElementById('quickAddForm').addEventListener('submit', function(e) {
      e.preventDefault();
      const bookId = document.getElementById('entryBook').value;
      if (!bookId) {
        showToast('Lütfen bir kitap seç! 📖', 'error');
        return;
      }

      const entry = {
        date: document.getElementById('entryDate').value,
        bookId: bookId,
        pages: parseInt(document.getElementById('entryPages').value) || 0,
        type: document.getElementById('entryType').value,
        note: document.getElementById('entryNote').value.trim()
      };

      if (!entry.date) {
        showToast('Tarih seçmelisin! 📅', 'error');
        return;
      }

      addEntry(entry);
      document.getElementById('entryPages').value = '';
      document.getElementById('entryNote').value = '';
      document.getElementById('entryDate').value = getTodayStr();
    });

    // Edit Form
    document.getElementById('editForm').addEventListener('submit', function(e) {
      e.preventDefault();
      saveEdit();
    });

    document.getElementById('cancelEdit').addEventListener('click', function() {
      document.getElementById('editModal').classList.remove('active');
    });

    document.getElementById('editModal').addEventListener('click', function(e) {
      if (e.target === this) this.classList.remove('active');
    });

    // Filters
    document.getElementById('filterType').addEventListener('change', renderAllEntries);
    document.getElementById('filterMonth').addEventListener('change', renderAllEntries);
    document.getElementById('filterBook').addEventListener('change', renderAllEntries);

    // Settings
    document.getElementById('saveSettings').addEventListener('click', saveSettingsFromUI);

    // Data management
    document.getElementById('exportData').addEventListener('click', exportData);
    document.getElementById('importDataBtn').addEventListener('click', function() {
      document.getElementById('importDataFile').click();
    });
    document.getElementById('importDataFile').addEventListener('change', function(e) {
      if (e.target.files[0]) {
        importData(e.target.files[0]);
        e.target.value = '';
      }
    });
    document.getElementById('clearData').addEventListener('click', clearAllData);

    // Load UI
    loadSettingsToUI();
    populateBookSelectors();
    updateDashboard();
    renderBooksList();
    populateMonthFilter();
    updateMotivation();
  }

  // ===== Public API =====
  window.app = {
    editEntry,
    deleteEntry,
    deleteBook
  };

  // Start
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

})();
