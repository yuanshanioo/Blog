/**
 * 远山 - Frontend JavaScript
 * Theme: Mirages-style
 */

(function() {
  'use strict';

  // ===== DOM Ready =====
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    initTheme();
    initSettings();
    initSearch();
    initMobileMenu();
    initLazyImages();
  }

  // ===== Theme System =====
  function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'auto';

    if (savedTheme === 'auto') {
      applyAutoTheme();
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyAutoTheme);
    } else {
      document.documentElement.setAttribute('data-theme', savedTheme);
    }

    // Theme mode buttons
    document.querySelectorAll('.theme-mode-btn').forEach(btn => {
      btn.addEventListener('click', function() {
        const mode = this.dataset.mode;
        setTheme(mode);
        document.querySelectorAll('.theme-mode-btn').forEach(b => b.classList.remove('active'));
        this.classList.add('active');
      });
    });
  }

  function setTheme(mode) {
    localStorage.setItem('theme', mode);
    if (mode === 'auto') {
      applyAutoTheme();
    } else {
      document.documentElement.setAttribute('data-theme', mode);
    }
  }

  function applyAutoTheme() {
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    document.documentElement.setAttribute('data-theme', prefersDark ? 'dark' : 'light');
  }

  // ===== Reading Settings =====
  function initSettings() {
    const settingsToggle = document.getElementById('settings-toggle');
    const settingsDropdown = document.getElementById('settings-dropdown');
    const overlay = document.getElementById('overlay');

    if (settingsToggle && settingsDropdown) {
      settingsToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        settingsDropdown.classList.toggle('show');
        if (overlay) overlay.classList.toggle('show');
      });

      document.addEventListener('click', function(e) {
        if (!settingsDropdown.contains(e.target) && e.target !== settingsToggle) {
          settingsDropdown.classList.remove('show');
          if (overlay) overlay.classList.remove('show');
        }
      });
    }

    // Font size
    const fontRange = document.getElementById('font-range');
    const fontInc = document.getElementById('font-inc');
    const fontDec = document.getElementById('font-dec');

    function setFontSize(size) {
      size = Math.max(80, Math.min(120, size));
      document.documentElement.setAttribute('data-size', size);
      localStorage.setItem('fontSize', size);
      if (fontRange) fontRange.value = size;
    }

    const savedSize = localStorage.getItem('fontSize') || '100';
    setFontSize(parseInt(savedSize));

    if (fontRange) {
      fontRange.addEventListener('input', function() {
        setFontSize(parseInt(this.value));
      });
    }
    if (fontInc) {
      fontInc.addEventListener('click', function() {
        const current = parseInt(document.documentElement.getAttribute('data-size') || '100');
        setFontSize(current + 5);
      });
    }
    if (fontDec) {
      fontDec.addEventListener('click', function() {
        const current = parseInt(document.documentElement.getAttribute('data-size') || '100');
        setFontSize(current - 5);
      });
    }

    // Font switch (serif/sans/kai/song)
    const fontBtns = document.querySelectorAll('.font-btn');
    const savedFont = localStorage.getItem('fontFamily') || 'sans';

    if (savedFont !== 'sans') {
      document.documentElement.setAttribute('data-font', savedFont);
    }

    fontBtns.forEach(btn => {
      btn.classList.toggle('active', btn.dataset.font === savedFont);
      btn.addEventListener('click', function() {
        const font = this.dataset.font;
        fontBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        if (font === 'sans') {
          document.documentElement.removeAttribute('data-font');
          localStorage.setItem('fontFamily', 'sans');
        } else {
          document.documentElement.setAttribute('data-font', font);
          localStorage.setItem('fontFamily', font);
        }
      });
    });

    // Restore active theme mode button
    const currentTheme = localStorage.getItem('theme') || 'auto';
    document.querySelectorAll('.theme-mode-btn').forEach(btn => {
      if (btn.dataset.mode === currentTheme) {
        btn.classList.add('active');
      }
    });
  }

  // ===== Search Toggle =====
  function initSearch() {
    const searchToggle = document.getElementById('search-toggle');
    if (searchToggle) {
      searchToggle.addEventListener('click', function() {
        window.location.href = '/search';
      });
    }
  }

  // ===== Mobile Menu =====
  function initMobileMenu() {
    const menuToggle = document.getElementById('menu-toggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const overlay = document.getElementById('overlay');

    if (menuToggle && mobileMenu) {
      menuToggle.addEventListener('click', function() {
        mobileMenu.classList.toggle('open');
        overlay.classList.toggle('show');
        menuToggle.textContent = mobileMenu.classList.contains('open') ? '✕' : '☰';
      });

      if (overlay) {
        overlay.addEventListener('click', function() {
          mobileMenu.classList.remove('open');
          overlay.classList.remove('show');
          if (menuToggle) menuToggle.textContent = '☰';
        });
      }
    }
  }

  // ===== Lazy Loading Images =====
  function initLazyImages() {
    if ('loading' in HTMLImageElement.prototype) {
      document.querySelectorAll('img[loading="lazy"]').forEach(img => {
        img.src = img.dataset.src || img.src;
      });
    }
  }

})();
