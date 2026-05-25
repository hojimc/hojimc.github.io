/**
 * nav.js — Mobile hamburger menu toggle
 * Include on every page: <script src="/js/nav.js" defer></script>
 */
(function () {
  'use strict';

  const toggle = document.querySelector('.nav__toggle');
  const links  = document.getElementById('nav-links');
  if (!toggle || !links) return;

  function openMenu() {
    links.classList.add('nav__links--open');
    toggle.setAttribute('aria-expanded', 'true');
  }
  function closeMenu() {
    links.classList.remove('nav__links--open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  toggle.addEventListener('click', function () {
    if (links.classList.contains('nav__links--open')) {
      closeMenu();
    } else {
      openMenu();
    }
  });

  // Close when a nav link is clicked (navigating away)
  links.querySelectorAll('.nav__link').forEach(function (link) {
    link.addEventListener('click', closeMenu);
  });

  // Close on Escape key
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeMenu();
  });

  // Close when clicking outside the nav
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.nav')) closeMenu();
  });

})();
