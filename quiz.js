// ===== TUS Takip - Gamified Daily Quiz Module (v4.1.0) =====
(function() {
  'use strict';

  const DB_URL = 'https://tustakip-default-rtdb.europe-west1.firebasedatabase.app';
  const QUESTIONS_URL = 'cikmis_sorular/fizyoloji_sorular.json';

  // Fallback questions if fetch fails
  const FALLBACK_QUESTIONS = [
    {
      id: "fizyoloji_q1",
      exam: "Nisan 2001 TUS",
      subject: "Fizyoloji",
      topic: "Hücre Bölünmesi (Mitoz)",
      question: "Kromozomlar hücre bölünmesinde hangi evrede ekvatoryal düzeyde dizilim gösterirler?",
      options: {
        A: "İnterfaz",
        B: "Profaz",
        C: "Metafaz",
        D: "Anafaz",
        E: "Telofaz"
      },
      answer: "C",
      explanation: "Ekvatoryal dizilim = Metafazın en önemli özelliğidir. Mitoz bölünmede kromozomların mikrotübüllere tutunarak hücrenin ekvatoral düzleminde (metafaz plağı) tek sıra halinde dizildiği evre metafazdır. Karyotip analizi de en belirgin bu evrede yapılır."
    },
    {
      id: "fizyoloji_q2",
      exam: "Eylül 1999 TUS",
      subject: "Fizyoloji",
      topic: "Hücre Zarı & Membran Proteinleri",
      question: "Aşağıdakilerden hangisi hücre membranının özelliği değildir?",
      options: {
        A: "Yapısında temel olarak proteinler ve fosfolipidler bulunur.",
        B: "Periferal proteinler iyon kanalı görevi görür.",
        C: "Hücre membranı asimetrik yapıdadır.",
        D: "Protein yapılı hormonlar için yüzeyde özelleşmiş reseptörler bulunur.",
        E: "Kolesterol oranı artan bölümlerinde akışkanlık azalır."
      },
      answer: "B",
      explanation: "Periferal proteinler membran boyunca uzanmazlar (transmembran değillerdir), lipid çift katmanının sadece bir yüzüne gevşek bağlıdırlar. Bu nedenle iyon kanalı veya taşıyıcı protein görevi İNTEGRAL (transmembran) proteinlere aittir."
    },
    {
      id: "fizyoloji_q3",
      exam: "Nisan 1997 TUS",
      subject: "Fizyoloji",
      topic: "Organeller & Genetik Materyal",
      question: "Nükleus DNA'sına gereksinim olmadan kendi kendine bölünebilen / çoğalabilen organel aşağıdakilerden hangisidir?",
      options: {
        A: "Mitokondri",
        B: "Lizozom",
        C: "Peroksizom",
        D: "Golgi cisimciği",
        E: "Granüllü endoplazmik retikulum"
      },
      answer: "A",
      explanation: "Mitokondri kendi dairesel çift sarmallı DNA'sına (mtDNA), kendi ribozomlarına ve tRNA'larına sahiptir. Nükleer DNA'dan bağımsız olarak replike olabilir ve ikiye bölünerek çoğalabilir. Anneden aktarılır (maternal kalıtım)."
    },
    {
      id: "fizyoloji_q4",
      exam: "Nisan 1994 TUS",
      subject: "Fizyoloji",
      topic: "Hücre İçi İyon Dengesi",
      question: "Hücre içinde en fazla kalsiyum (Ca²⁺) içeren / depolayan organeller aşağıdaki seçeneklerin hangisinde birlikte verilmiştir?",
      options: {
        A: "Çekirdek ve Golgi cisimciği",
        B: "Lizozom ve Peroksizom",
        C: "Ribozom ve Çekirdekçik",
        D: "Plazma zarı ve Sentrozom",
        E: "Mitokondri ve Endoplazmik retikulum"
      },
      answer: "E",
      explanation: "Hücrede serbest sitozolik kalsiyum çok düşüktür. Kalsiyumun başlıca depolandığı yer Agranüler / Düz Endoplazmik Retikulumdur (özellikle kas hücrelerinde Sarkoplazmik Retikulum). İkinci önemli kalsiyum deposu ve tamponlayıcısı ise Mitokondridir."
    },
    {
      id: "fizyoloji_q5",
      exam: "Eylül 2003 TUS",
      subject: "Fizyoloji",
      topic: "Sitoskeleton & Hücre Mimarisi",
      question: "Hücre iskeleti elemanlarından hangisi mikrovillüslerin yapısında demetler halinde bulunur ve fırçamsı kenarı oluşturur?",
      options: {
        A: "Mikrotübüller",
        B: "Ara filamanlar",
        C: "Aktin filamanları (Mikrofilamanlar)",
        D: "Nörofilamanlar",
        E: "Laminler"
      },
      answer: "C",
      explanation: "Mikrovillüslerin merkezinde paralel demetler halinde organize olmuş AKTİN filamanları yer alır (fimbrin ve villin ile bir arada tutulur). Mikrotübüller ise silya (titrek tüy) ve flagella yapısında 9+2 mikrotübül çifti düzeninde bulunur."
    }
  ];

  const RANKS = [
    { minXp: 0, title: "Stajyer Doktor", icon: "🩺", nextXp: 100 },
    { minXp: 100, title: "İntörn Doktor", icon: "🥼", nextXp: 300 },
    { minXp: 300, title: "TUS Asistanı", icon: "👨‍⚕️", nextXp: 800 },
    { minXp: 800, title: "Uzman Hekim", icon: "👑", nextXp: 2000 }
  ];

  const QuizModule = {
    allQuestions: [],
    mart2023Questions: [],
    manifest: null,
    currentQuizQuestions: [],
    currentIndex: 0,
    currentScore: 0,
    earnedXp: 0,
    hasAnswered: false,
    userStats: {
      streak: 0,
      lastPlayedDate: null,
      totalXp: 0,
      solvedCount: 0
    },

    // ===== Initialize Module =====
    async init() {
      await this.loadManifest();
      await this.loadQuestions();
      this.attachEventListeners();
      await this.loadUserStats();
      this.renderDashboardCard();
    },

    // ===== Load Question Bank Manifest =====
    async loadManifest() {
      try {
        const res = await fetch('cikmis_sorular/virtual_db/question_bank_manifest.json');
        if (res.ok) {
          this.manifest = await res.json();
          const poolEl = document.getElementById('quizCardPoolCount');
          if (poolEl && this.manifest && typeof this.manifest.totalQuestions === 'number') {
            poolEl.textContent = `${this.manifest.totalQuestions} Soru`;
          }
        }
      } catch (err) {
        console.warn('[Quiz] Manifest okuma hatası:', err);
      }
    },

    // ===== Get Active Username =====
    getActiveUsername() {
      if (window.AuthService && typeof window.AuthService.getActiveStudent === 'function') {
        const student = window.AuthService.getActiveStudent();
        if (student) return student;
      }
      if (window.AuthService && typeof window.AuthService.getCurrentUser === 'function') {
        const u = window.AuthService.getCurrentUser();
        if (u && u.username) return u.username;
      }
      try {
        const savedTarget = localStorage.getItem('tus_active_target_student');
        if (savedTarget) return savedTarget;
      } catch (e) {}
      return 'guest';
    },

    // ===== Helper: Local YYYY-MM-DD Date (Prevents UTC timezone midnight discrepancies) =====
    getLocalDateString() {
      const d = new Date();
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },

    // ===== Load Question Bank (Dynamically from Manifest & Mart 2023) =====
    async loadQuestions() {
      let combined = [];
      let martQuestions = [];

      // 1. If manifest is available, fetch all active subjects with questions
      if (this.manifest && this.manifest.subjects) {
        const subjects = Object.values(this.manifest.subjects);
        for (const sub of subjects) {
          if (sub.file && sub.questionCount > 0) {
            try {
              const res = await fetch(sub.file);
              if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                  if (sub.code === 'mart2023' || sub.isExamEdition) {
                    martQuestions = data;
                    console.log(`[Quiz] ${sub.name}: ${data.length} soru (Mart 2023 Özel Havuzu) yüklendi.`);
                  } else {
                    combined = combined.concat(data);
                    console.log(`[Quiz] ${sub.name}: ${data.length} soru yüklendi.`);
                  }
                }
              }
            } catch (err) {
              console.warn(`[Quiz] ${sub.name} soruları yüklenirken hata:`, err);
            }
          }
        }
      }

      // Ensure mart2023 questions are loaded even if manifest was cached/omitted
      if (martQuestions.length === 0) {
        try {
          const resMart = await fetch('cikmis_sorular/virtual_db/questions_mart2023.json');
          if (resMart.ok) {
            const dataMart = await resMart.json();
            if (Array.isArray(dataMart) && dataMart.length > 0) {
              martQuestions = dataMart;
              console.log(`[Quiz] Mart 2023: ${martQuestions.length} soru doğrudan yüklendi.`);
            }
          }
        } catch (e) {
          console.warn('[Quiz] Mart 2023 soruları doğrudan yüklenirken hata:', e);
        }
      }

      this.mart2023Questions = martQuestions;

      if (combined.length > 0) {
        this.allQuestions = combined;
        console.log(`[Quiz] Toplam ${this.allQuestions.length} soru Genel Havuzdan + ${this.mart2023Questions.length} soru Mart 2023'ten yüklendi.`);
        return;
      }

      // 2. Fallback candidates for general pool
      const fallbackUrls = [
        'cikmis_sorular/virtual_db/questions_fizyoloji.json',
        'cikmis_sorular/fizyoloji_sorular.json'
      ];
      for (const url of fallbackUrls) {
        try {
          const res = await fetch(url);
          if (res.ok) {
            const data = await res.json();
            if (Array.isArray(data) && data.length > 0) {
              this.allQuestions = data;
              return;
            }
          }
        } catch (err) {}
      }

      // 3. Hardcoded fallback
      this.allQuestions = FALLBACK_QUESTIONS;
    },

    // ===== Load User Quiz Stats (Firebase + LocalStorage fallback) =====
    async loadUserStats(overrideUsername) {
      const username = overrideUsername || this.getActiveUsername();
      const localKey = `tus_quiz_stats_${username}`;
      
      // Default initial stats
      this.userStats = {
        streak: 0,
        lastPlayedDate: null,
        totalXp: 0,
        solvedCount: 0,
        questionHistory: {}
      };

      // 1. Try LocalStorage
      try {
        const localData = localStorage.getItem(localKey);
        if (localData) {
          this.userStats = Object.assign(this.userStats, JSON.parse(localData));
        }
      } catch (e) {}

      // 2. Try Firebase (Lightweight: ~100 bytes) with cache-busting timestamp
      try {
        const res = await fetch(`${DB_URL}/tus_v4/users/${username}/quiz.json?t=${Date.now()}`);
        if (res.ok) {
          const cloudData = await res.json();
          if (cloudData && typeof cloudData === 'object') {
            this.userStats = Object.assign(this.userStats, cloudData);
            if (!this.userStats.questionHistory) {
              this.userStats.questionHistory = {};
            }
            localStorage.setItem(localKey, JSON.stringify(this.userStats));
          }
        }
      } catch (err) {
        console.warn('[Quiz] Firebase istatistik okuma hatası:', err);
      }

      this.updateStreakValidation();
    },

    // ===== Streak Calculation (Duolingo Style) =====
    updateStreakValidation() {
      if (!this.userStats.lastPlayedDate) return;

      const today = this.getLocalDateString();
      const last = new Date(this.userStats.lastPlayedDate);
      const now = new Date(today);
      const diffTime = now - last;
      const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

      if (diffDays > 1) {
        // Streak lost if more than 1 day missed
        this.userStats.streak = 0;
      }
    },

    // ===== Save User Stats (Firebase + LocalStorage) =====
    async saveUserStats() {
      const username = this.getActiveUsername();
      const localKey = `tus_quiz_stats_${username}`;

      try {
        localStorage.setItem(localKey, JSON.stringify(this.userStats));
      } catch (e) {}

      try {
        // Lightweight cloud sync (keeps Firebase footprint under 100 bytes)
        const cloudPayload = {
          streak: this.userStats.streak || 0,
          totalXp: this.userStats.totalXp || 0,
          solvedCount: this.userStats.solvedCount || 0,
          lastPlayedDate: this.userStats.lastPlayedDate || null
        };
        await fetch(`${DB_URL}/tus_v4/users/${username}/quiz.json`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(cloudPayload)
        });
      } catch (err) {
        console.warn('[Quiz] Firebase istatistik kaydetme hatası:', err);
      }
    },

    // ===== Get Doctor Rank Info =====
    getRankInfo(xp) {
      let currentRank = RANKS[0];
      for (let i = 0; i < RANKS.length; i++) {
        if (xp >= RANKS[i].minXp) {
          currentRank = RANKS[i];
        }
      }
      return currentRank;
    },

    // ===== Render Dashboard Hero Card =====
    renderDashboardCard() {
      const card = document.getElementById('quizDashboardCard');
      if (!card) return;

      const today = this.getLocalDateString();
      const isCompletedToday = this.userStats.lastPlayedDate === today;
      const rank = this.getRankInfo(this.userStats.totalXp);

      const streakEl = document.getElementById('quizCardStreak');
      const xpEl = document.getElementById('quizCardXp');
      const rankEl = document.getElementById('quizCardRank');
      const solvedEl = document.getElementById('quizCardSolvedCount');
      const poolEl = document.getElementById('quizCardPoolCount');
      const statusBadge = document.getElementById('quizCardStatusBadge');
      const startBtn = document.getElementById('quizCardStartBtn');

      if (streakEl) streakEl.textContent = `${this.userStats.streak || 0} Gün`;
      if (xpEl) xpEl.textContent = `${this.userStats.totalXp || 0} XP`;
      if (rankEl) rankEl.innerHTML = `${rank.icon} ${rank.title}`;
      if (solvedEl) solvedEl.textContent = `${this.userStats.solvedCount || 0} Soru`;
      if (poolEl && this.manifest && typeof this.manifest.totalQuestions === 'number') {
        poolEl.textContent = `${this.manifest.totalQuestions} Soru`;
      }

      if (statusBadge) {
        if (isCompletedToday) {
          statusBadge.innerHTML = '✅ Bugünkü TUS Dozu Alındı! (10/10 Soru Çözüldü 🔥)';
          statusBadge.className = 'quiz-status-badge completed';
        } else {
          statusBadge.innerHTML = '🔥 Günün 10 Sorusu Bekliyor! (5 Genel + 5 Mart 2023)';
          statusBadge.className = 'quiz-status-badge pending';
        }
      }

      if (startBtn) {
        if (isCompletedToday) {
          startBtn.innerHTML = '<span>Tekrar Pratik Yap (10 Soru)</span><span class="btn-arrow">🔄</span>';
        } else {
          startBtn.innerHTML = '<span>Quize Başla (10 Soru)</span><span class="btn-arrow">🚀</span>';
        }
      }
    },

    // ===== Start a 10-Question Hybrid Quiz (5 General + 5 Mart 2023) =====
    startQuiz() {
      if (!this.userStats.questionHistory) {
        this.userStats.questionHistory = {};
      }

      const today = this.getLocalDateString();
      const todayDate = new Date(today);

      // Helper to select 5 questions from a pool using Spaced Repetition (SRS)
      const selectFiveWithSRS = (pool, sectionType, sectionBadge) => {
        const reviewCandidates = [];
        const freshCandidates = [];
        const correctCandidates = [];

        pool.forEach(q => {
          const hist = this.userStats.questionHistory[q.id];
          if (!hist) {
            freshCandidates.push({ ...q });
          } else if (hist.status === 'wrong') {
            const lastDate = hist.lastDate ? new Date(hist.lastDate) : new Date('2020-01-01');
            const daysAgo = Math.floor((todayDate - lastDate) / (1000 * 60 * 60 * 24));
            reviewCandidates.push({
              ...q,
              _isReview: true,
              _daysAgo: daysAgo >= 1 ? daysAgo : 1
            });
          } else {
            correctCandidates.push({ ...q });
          }
        });

        // Shuffle candidate sub-pools
        reviewCandidates.sort(() => 0.5 - Math.random());
        freshCandidates.sort(() => 0.5 - Math.random());
        correctCandidates.sort(() => 0.5 - Math.random());

        const picked = [];
        // Priority 1: Pick up to 2 review (wrong) questions
        const reviewPickCount = Math.min(2, reviewCandidates.length);
        for (let i = 0; i < reviewPickCount; i++) {
          picked.push(reviewCandidates[i]);
        }

        // Priority 2: Fill remaining from fresh (unseen) questions
        while (picked.length < 5 && freshCandidates.length > 0) {
          picked.push(freshCandidates.shift());
        }

        // Priority 3: Fill from correct pool or review pool
        while (picked.length < 5 && correctCandidates.length > 0) {
          picked.push(correctCandidates.shift());
        }
        while (picked.length < 5 && reviewCandidates.length > 0) {
          const nextRev = reviewCandidates.shift();
          if (!picked.find(s => s.id === nextRev.id)) {
            picked.push(nextRev);
          }
        }

        // Fallback if pool is small
        if (picked.length < 5 && pool.length > 0) {
          const fallbackPool = [...pool].sort(() => 0.5 - Math.random());
          while (picked.length < 5 && fallbackPool.length > 0) {
            const cand = fallbackPool.shift();
            if (!picked.find(s => s.id === cand.id)) {
              picked.push({ ...cand });
            }
          }
        }

        // Tag each question with its section identifier
        return picked.slice(0, 5).map(q => ({
          ...q,
          _quizSection: sectionType,
          _sectionBadge: sectionBadge
        }));
      };

      // Pool 1: General question pool (all non-Mart 2023 questions)
      const generalPool = this.allQuestions.filter(q => q.exam !== 'Mart 2023 TUS' && (!q.id || !q.id.startsWith('mart2023')));
      const part1 = selectFiveWithSRS(
        generalPool.length > 0 ? generalPool : this.allQuestions,
        'general',
        '📚 Genel Soru Havuzu & Tekrar'
      );

      // Pool 2: Mart 2023 Gerçek TUS Sınavı pool
      const martPool = this.mart2023Questions && this.mart2023Questions.length > 0
        ? this.mart2023Questions
        : this.allQuestions.filter(q => q.exam === 'Mart 2023 TUS' || (q.id && q.id.startsWith('mart2023')));
      const part2 = selectFiveWithSRS(
        martPool.length > 0 ? martPool : this.allQuestions,
        'mart2023',
        '🔥 Güncel TUS • Mart 2023 Gerçek Sınavı'
      );

      // Combine into the 10-question hybrid set (1-5 General, 6-10 Mart 2023)
      this.currentQuizQuestions = [...part1, ...part2];
      this.currentIndex = 0;
      this.currentScore = 0;
      this.earnedXp = 0;
      this.hasAnswered = false;

      // Open Modal
      const modal = document.getElementById('quizModal');
      const resultsView = document.getElementById('quizResultsView');
      const questionView = document.getElementById('quizQuestionView');

      if (resultsView) resultsView.style.display = 'none';
      if (questionView) questionView.style.display = 'block';
      if (modal) modal.style.display = 'flex';

      this.renderCurrentQuestion();
    },

    // ===== Render Current Question =====
    renderCurrentQuestion() {
      const q = this.currentQuizQuestions[this.currentIndex];
      if (!q) return;

      this.hasAnswered = false;

      // Progress Bar & Indicators
      const progressText = document.getElementById('quizProgressText');
      const progressBar = document.getElementById('quizProgressBarFill');
      const subjectTag = document.getElementById('quizSubjectTag');
      const examTag = document.getElementById('quizExamTag');
      const questionText = document.getElementById('quizQuestionContent');
      const optionsContainer = document.getElementById('quizOptionsContainer');
      const explanationBox = document.getElementById('quizExplanationBox');
      const nextBtn = document.getElementById('quizNextBtn');

      const pct = ((this.currentIndex + 1) / 10) * 100;
      if (progressText) progressText.textContent = `Soru ${this.currentIndex + 1} / 10`;
      if (progressBar) progressBar.style.width = `${pct}%`;

      if (subjectTag) subjectTag.textContent = `${q.subject} • ${q.topic || 'Genel'}`;
      if (examTag) examTag.textContent = q.exam || 'Çıkmış TUS';
      if (questionText) questionText.textContent = q.question;

      // Section Badge (General Pool vs Mart 2023 Real Exam)
      const sectionBadgeEl = document.getElementById('quizSectionBadge');
      if (sectionBadgeEl) {
        const isMart = q._quizSection === 'mart2023' || q.exam === 'Mart 2023 TUS' || (q.id && q.id.startsWith('mart2023'));
        sectionBadgeEl.className = `quiz-section-badge ${isMart ? 'mart2023' : 'general'}`;
        sectionBadgeEl.textContent = q._sectionBadge || (isMart ? '🔥 Güncel TUS • Mart 2023 Gerçek Sınavı' : '📚 Genel Soru Havuzu & Tekrar');
      }

      // Spaced Repetition Review Badge
      let reviewBadgeEl = document.getElementById('quizReviewAlertBadge');
      if (q._isReview) {
        const timeText = q._daysAgo >= 7 ? `${Math.round(q._daysAgo / 7)} hafta` : `${q._daysAgo} gün`;
        if (!reviewBadgeEl) {
          reviewBadgeEl = document.createElement('div');
          reviewBadgeEl.id = 'quizReviewAlertBadge';
          reviewBadgeEl.className = 'quiz-review-alert-badge';
          const questionBox = document.querySelector('.quiz-question-box');
          if (questionBox && questionBox.parentNode) {
            questionBox.parentNode.insertBefore(reviewBadgeEl, questionBox);
          }
        }
        reviewBadgeEl.innerHTML = `
          <span class="review-icon">🔄</span>
          <div class="review-content">
            <strong>${timeText} önce bu soruda yanılmıştın!</strong>
            <span>Bakalım konuyu pekiştirdin mi? Şimdi intikam vakti! 💪</span>
          </div>
        `;
        reviewBadgeEl.style.display = 'flex';
      } else if (reviewBadgeEl) {
        reviewBadgeEl.style.display = 'none';
      }

      // Reset High-Yield Side Drawer
      const drawer = document.getElementById('quizSideDrawer');
      const modalCard = document.getElementById('quizModalCard');
      if (drawer) drawer.style.display = 'none';
      if (modalCard) modalCard.classList.remove('has-drawer');

      if (explanationBox) {
        explanationBox.style.display = 'none';
        explanationBox.innerHTML = '';
      }
      if (nextBtn) nextBtn.style.display = 'none';

      // Build Option Buttons
      if (optionsContainer) {
        optionsContainer.innerHTML = '';
        const letters = ['A', 'B', 'C', 'D', 'E'];

        letters.forEach(letter => {
          const text = q.options[letter];
          if (!text) return;

          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'quiz-option-btn';
          btn.dataset.letter = letter;

          btn.innerHTML = `
            <span class="option-badge">${letter}</span>
            <span class="option-label">${text}</span>
            <span class="option-icon"></span>
          `;

          btn.addEventListener('click', () => this.handleOptionClick(letter, btn));
          optionsContainer.appendChild(btn);
        });
      }
    },

    // ===== Handle Option Click =====
    handleOptionClick(selectedLetter, clickedBtn) {
      if (this.hasAnswered) return;
      this.hasAnswered = true;

      const q = this.currentQuizQuestions[this.currentIndex];
      const isCorrect = selectedLetter === q.answer;
      const optionsContainer = document.getElementById('quizOptionsContainer');
      const explanationBox = document.getElementById('quizExplanationBox');
      const nextBtn = document.getElementById('quizNextBtn');

      // Update Spaced Repetition History
      if (!this.userStats.questionHistory) {
        this.userStats.questionHistory = {};
      }
      const prevHist = this.userStats.questionHistory[q.id] || { wrongCount: 0 };
      const today = new Date().toISOString().split('T')[0];

      if (isCorrect) {
        this.userStats.questionHistory[q.id] = {
          status: 'correct',
          lastDate: today,
          wrongCount: prevHist.wrongCount || 0
        };
      } else {
        this.userStats.questionHistory[q.id] = {
          status: 'wrong',
          lastDate: today,
          wrongCount: (prevHist.wrongCount || 0) + 1
        };
      }

      // Disable all options
      const allBtns = optionsContainer ? optionsContainer.querySelectorAll('.quiz-option-btn') : [];
      allBtns.forEach(btn => {
        btn.disabled = true;
        if (btn.dataset.letter === q.answer) {
          btn.classList.add('correct');
          const icon = btn.querySelector('.option-icon');
          if (icon) icon.textContent = '✓';
        }
      });

      if (isCorrect) {
        clickedBtn.classList.add('correct', 'pulse');
        this.currentScore++;
        this.earnedXp += 20;
        this.playCelebrationMini();
      } else {
        clickedBtn.classList.add('wrong', 'shake');
        const icon = clickedBtn.querySelector('.option-icon');
        if (icon) icon.textContent = '✕';
      }

      // Open High-Yield Side Drawer with Rich Cards
      this.formatAndRenderPearlDrawer(q, selectedLetter, isCorrect);
      const drawer = document.getElementById('quizSideDrawer');
      const modalCard = document.getElementById('quizModalCard');
      if (drawer) drawer.style.display = 'flex';
      if (modalCard) modalCard.classList.add('has-drawer');

      // Show Next Button
      if (nextBtn) {
        if (this.currentIndex >= 9) {
          nextBtn.innerHTML = '<span>Sonuçları Gör 🏆</span><span class="btn-arrow">→</span>';
        } else {
          nextBtn.innerHTML = '<span>Sonraki Soru</span><span class="btn-arrow">→</span>';
        }
        nextBtn.style.display = 'inline-flex';
      }
    },

    // ===== Format & Render High-Yield Pearl Drawer =====
    formatAndRenderPearlDrawer(q, selectedLetter, isCorrect) {
      const drawerContent = document.getElementById('quizSideDrawerContent');
      if (!drawerContent) return;

      const ansLetter = q.answer;
      const ansText = q.options && q.options[ansLetter] ? q.options[ansLetter] : '';
      let rawExpl = q.explanation || 'Bu soru için klinik açıklama hazırlanmaktadır.';

      // 1. Extract "Başka bir hoca şöyle sorabilirdi" (Alternative Question Pattern)
      let altQuestion = null;
      const altRegex = /(?:Not:\s*)?(?:Bu\s*soru,?\s*)?(?:başka\s*bir\s*hoca\s*tarafından\s*)?şöyle\s*de?\s*sorulabilirdi[:\)]?\s*([^\?\n\r]+(?:\?|[^\.\n\r]+\.))/i;
      const altMatch = rawExpl.match(altRegex);
      if (altMatch) {
        altQuestion = altMatch[1].trim();
        rawExpl = rawExpl.replace(altMatch[0], '').trim();
      }

      // 2. Clean leading/trailing punctuation and dangling parens
      rawExpl = rawExpl.replace(/^\s*[\)\:\-\*\+]\s*/, '').trim();

      // 3. Break into distinct high-yield flashcard points
      let points = [];
      if (rawExpl.includes('*') || rawExpl.includes('+')) {
        const parts = rawExpl.split(/[\*\+]/);
        for (let p of parts) {
          p = p.trim();
          if (p.length > 5) points.push(p);
        }
      } else {
        const sentences = rawExpl.split(/(?<=[.!?])\s+(?=[A-ZÇĞİÖŞÜ])/);
        for (let s of sentences) {
          s = s.trim();
          if (s.length > 5) points.push(s);
        }
      }

      if (points.length === 0) {
        points = [rawExpl];
      }

      const icons = ['💡', '⚡', '🔬', '📌', '🧬', '🩺', '🎯', '🧪'];
      let html = '';

      // Section 1: Doğru Cevap Kartı
      html += `
        <div class="pearl-answer-card">
          <div class="pearl-answer-badge">✓ Doğru Cevap: ${ansLetter}</div>
          <div class="pearl-answer-text">${ansText}</div>
        </div>
      `;

      // Section 2: "Başka Bir Hoca Şöyle Sorabilirdi" (Alternative Question Angle)
      if (altQuestion) {
        html += `
          <div class="pearl-alt-card">
            <div class="pearl-alt-header">
              <div class="pearl-alt-label">
                <span>🎯</span>
                <span>Başka Bir Hoca Şöyle Sorabilirdi</span>
              </div>
              <span class="pearl-alt-tag">Hoca Notu</span>
            </div>
            <p class="pearl-alt-q">"${altQuestion}"</p>
            <div class="pearl-alt-ai-footer">
              <span>🤖</span>
              <span>AI Destekli Soru Analizi & Varyasyon Kartı</span>
            </div>
          </div>
        `;
      }

      // Section 3: High-Yield Flashcard Notları
      html += `<div class="pearl-flashcards-wrap">`;
      points.forEach((pt, idx) => {
        const icon = icons[idx % icons.length];
        let formatted = pt.replace(/^([A-ZÇĞİÖŞÜa-zçğıöşü\s\(\)\-]{3,35}\s*[:=])/g, '<strong>$1</strong>');
        formatted = formatted.replace(/\(\s*o\s*/g, ' ').replace(/\s{2,}/g, ' ');

        html += `
          <div class="pearl-flashcard">
            <span class="pearl-card-icon">${icon}</span>
            <div class="pearl-card-body">${formatted}</div>
          </div>
        `;
      });
      html += `</div>`;

      drawerContent.innerHTML = html;
    },

    // ===== Next Question or Finish =====
    nextQuestion() {
      if (this.currentIndex < 9) {
        this.currentIndex++;
        this.renderCurrentQuestion();
      } else {
        this.finishQuiz();
      }
    },

    // ===== Finish Quiz & Celebrate =====
    async finishQuiz() {
      const today = this.getLocalDateString();
      const isFirstToday = this.userStats.lastPlayedDate !== today;

      // Update Streak
      if (isFirstToday) {
        const last = this.userStats.lastPlayedDate ? new Date(this.userStats.lastPlayedDate) : null;
        const now = new Date(today);
        const diffDays = last ? Math.floor((now - last) / (1000 * 60 * 60 * 24)) : 999;

        if (diffDays === 1) {
          this.userStats.streak += 1;
        } else {
          this.userStats.streak = 1;
        }
        this.userStats.lastPlayedDate = today;

        // Bonus XP for daily completion
        this.earnedXp += 50;
      }

      this.userStats.totalXp += this.earnedXp;
      this.userStats.solvedCount += 10;

      // Save to Firebase and Local
      await this.saveUserStats();
      this.renderDashboardCard();

      // Show Results View
      const questionView = document.getElementById('quizQuestionView');
      const resultsView = document.getElementById('quizResultsView');
      if (questionView) questionView.style.display = 'none';
      if (resultsView) resultsView.style.display = 'block';

      // Fill Results Data
      const scoreEl = document.getElementById('quizResultScore');
      const xpEl = document.getElementById('quizResultXp');
      const streakEl = document.getElementById('quizResultStreak');
      const rankEl = document.getElementById('quizResultRank');
      const messageEl = document.getElementById('quizResultMessage');

      if (scoreEl) scoreEl.textContent = `${this.currentScore} / 10`;
      if (xpEl) xpEl.textContent = `+${this.earnedXp} XP`;
      if (streakEl) streakEl.textContent = `${this.userStats.streak} Gün 🔥`;

      const rank = this.getRankInfo(this.userStats.totalXp);
      if (rankEl) rankEl.innerHTML = `${rank.icon} ${rank.title}`;

      if (messageEl) {
        if (this.currentScore === 10) {
          messageEl.textContent = '🌟 Efsanevi Başarı! 10\'da 10 Tam İsabet! Hem Genel Havuzu hem Güncel Mart 2023 TUS\'u fethettin!';
        } else if (this.currentScore >= 8) {
          messageEl.textContent = '🔥 Harika performans! Hem genel temelde hem Mart 2023 sınavında çok güçlüsün.';
        } else if (this.currentScore >= 5) {
          messageEl.textContent = '👏 Tebrikler! 10 soruluk maratonu başarıyla tamamladın. TUS soru kalıpları oturuyor.';
        } else {
          messageEl.textContent = '💪 Güzel mücadele! Yan paneldeki yüksek verimli kartları iyi oku, her soru sınavda +1 net!';
        }
      }

      // Fire confetti celebration
      this.triggerConfetti();
    },

    // ===== Confetti Animation =====
    triggerConfetti() {
      if (typeof confetti === 'function') {
        confetti({
          particleCount: 120,
          spread: 70,
          origin: { y: 0.6 }
        });
        setTimeout(() => {
          confetti({
            particleCount: 80,
            angle: 60,
            spread: 55,
            origin: { x: 0 }
          });
          confetti({
            particleCount: 80,
            angle: 120,
            spread: 55,
            origin: { x: 1 }
          });
        }, 300);
      }
    },

    playCelebrationMini() {
      if (typeof confetti === 'function') {
        confetti({
          particleCount: 25,
          spread: 40,
          origin: { y: 0.7 }
        });
      }
    },

    // ===== Close Modal =====
    closeModal() {
      const modal = document.getElementById('quizModal');
      const drawer = document.getElementById('quizSideDrawer');
      const modalCard = document.getElementById('quizModalCard');
      if (drawer) drawer.style.display = 'none';
      if (modalCard) modalCard.classList.remove('has-drawer');
      if (modal) modal.style.display = 'none';
      this.renderDashboardCard();
    },

    // ===== Open Question Pool Breakdown Modal =====
    openPoolModal() {
      const modal = document.getElementById('quizPoolModal');
      if (!modal) return;

      const totalVal = document.getElementById('poolTotalQuestionsVal');
      const activeVal = document.getElementById('poolActiveSubjectsVal');
      const grid = document.getElementById('poolSubjectsGrid');

      if (this.manifest) {
        if (totalVal) totalVal.textContent = this.manifest.totalQuestions || 0;
        if (activeVal) {
          const actCount = this.manifest.summary ? this.manifest.summary.activeSubjects : 1;
          activeVal.textContent = `${actCount} / 13`;
        }

        if (grid && this.manifest.subjects) {
          grid.innerHTML = '';
          const subKeys = Object.keys(this.manifest.subjects);

          // Sort so subjects with questions appear first
          subKeys.sort((a, b) => {
            const countA = this.manifest.subjects[a].questionCount || 0;
            const countB = this.manifest.subjects[b].questionCount || 0;
            return countB - countA;
          });

          subKeys.forEach(key => {
            const sub = this.manifest.subjects[key];
            const hasQ = (sub.questionCount || 0) > 0;
            const card = document.createElement('div');
            card.className = `pool-subject-card ${hasQ ? 'has-questions' : ''}`;
            if (hasQ) {
              card.style.borderLeft = `4px solid ${sub.color || '#10b981'}`;
            }

            let categoriesHtml = '';
            if (hasQ && sub.categories && Object.keys(sub.categories).length > 0) {
              const catTags = Object.entries(sub.categories)
                .map(([catName, count]) => `<span class="pool-cat-tag">${catName} (${count})</span>`)
                .join('');
              categoriesHtml = `<div class="pool-categories-tags">${catTags}</div>`;
            } else if (!hasQ) {
              categoriesHtml = `<span style="font-size:0.75rem; color:#64748b; font-style:italic;">Henüz soru yüklenmedi</span>`;
            }

            card.innerHTML = `
              <div class="pool-sub-header">
                <div class="pool-sub-title">
                  <span style="font-size:1.2rem;">${sub.icon || '📖'}</span>
                  <span>${sub.name}</span>
                </div>
                <div class="pool-sub-count">${sub.questionCount || 0} Soru</div>
              </div>
              ${categoriesHtml}
            `;
            grid.appendChild(card);
          });
        }
      }

      modal.style.display = 'flex';
    },

    // ===== Close Question Pool Modal =====
    closePoolModal() {
      const modal = document.getElementById('quizPoolModal');
      if (modal) modal.style.display = 'none';
    },

    // ===== Attach Event Listeners =====
    attachEventListeners() {
      const startBtn = document.getElementById('quizCardStartBtn');
      if (startBtn) {
        startBtn.addEventListener('click', () => this.startQuiz());
      }

      const closeBtn = document.getElementById('quizModalClose');
      if (closeBtn) {
        closeBtn.addEventListener('click', () => this.closeModal());
      }

      const sideDrawerClose = document.getElementById('quizSideDrawerClose');
      if (sideDrawerClose) {
        sideDrawerClose.addEventListener('click', () => {
          const drawer = document.getElementById('quizSideDrawer');
          const modalCard = document.getElementById('quizModalCard');
          if (drawer) drawer.style.display = 'none';
          if (modalCard) modalCard.classList.remove('has-drawer');
        });
      }

      const nextBtn = document.getElementById('quizNextBtn');
      if (nextBtn) {
        nextBtn.addEventListener('click', () => this.nextQuestion());
      }

      const finishDoneBtn = document.getElementById('quizFinishDoneBtn');
      if (finishDoneBtn) {
        finishDoneBtn.addEventListener('click', () => this.closeModal());
      }

      // Question Pool Breakdown Modal Listeners
      const poolPill = document.getElementById('quizCardPoolPill');
      if (poolPill) {
        poolPill.addEventListener('click', () => this.openPoolModal());
      }

      const poolModalClose = document.getElementById('quizPoolModalClose');
      if (poolModalClose) {
        poolModalClose.addEventListener('click', () => this.closePoolModal());
      }

      const poolModalDone = document.getElementById('quizPoolModalDoneBtn');
      if (poolModalDone) {
        poolModalDone.addEventListener('click', () => this.closePoolModal());
      }

      // Re-load stats when user changes or logs in
      window.addEventListener('tus-user-changed', async (e) => {
        const student = (e && e.detail && e.detail.student) || this.getActiveUsername();
        await this.loadUserStats(student);
        this.renderDashboardCard();
      });
    }
  };

  // Expose globally
  window.QuizModule = QuizModule;

  // Auto initialize on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => QuizModule.init());
  } else {
    QuizModule.init();
  }
})();
