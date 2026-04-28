// Theme toggle
(function() {
  const themeToggle = document.getElementById('theme-toggle');
  if (!themeToggle) return;

  const stored = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const theme = stored || (prefersDark ? 'dark' : 'light');

  if (theme === 'dark') {
    document.documentElement.setAttribute('data-theme', 'dark');
    themeToggle.textContent = '☀️';
  }

  themeToggle.addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    if (current === 'dark') {
      document.documentElement.removeAttribute('data-theme');
      localStorage.setItem('theme', 'light');
      themeToggle.textContent = '🌙';
    } else {
      document.documentElement.setAttribute('data-theme', 'dark');
      localStorage.setItem('theme', 'dark');
      themeToggle.textContent = '☀️';
    }
  });
})();

// Reading count simulation (increment on visit)
(function() {
  const countEls = document.querySelectorAll('.read-count');
  countEls.forEach(el => {
    const key = el.dataset.key;
    if (!key) return;
    const stored = localStorage.getItem('read_' + key);
    const count = stored ? parseInt(stored, 10) : Math.floor(Math.random() * 200) + 50;
    localStorage.setItem('read_' + key, count + 1);
    el.textContent = (count + 1).toLocaleString();
  });
})();
