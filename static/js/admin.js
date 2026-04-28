/**
 * 远山 - Admin JavaScript
 */

(function() {
  'use strict';

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    initFlashMessages();
    initConfirmDialogs();
  }

  // ===== Auto-dismiss Flash Messages =====
  function initFlashMessages() {
    const messages = document.querySelectorAll('.flash-message');
    messages.forEach(msg => {
      setTimeout(() => {
        msg.style.transition = 'opacity 0.5s, transform 0.3s';
        msg.style.opacity = '0';
        msg.style.transform = 'translateY(-8px)';
        setTimeout(() => msg.remove(), 500);
      }, 4000);
    });
  }

  // ===== Confirm Dialogs =====
  function initConfirmDialogs() {
    document.querySelectorAll('[data-confirm]').forEach(el => {
      el.addEventListener('click', function(e) {
        if (!confirm(this.dataset.confirm || '确定要执行此操作吗？')) {
          e.preventDefault();
        }
      });
    });
  }

})();
