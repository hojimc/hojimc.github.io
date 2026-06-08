(function () {
  'use strict';

  var path = window.location.pathname;
  var isVideos = path === '/videos.html' || path.indexOf('/videos/') === 0;

  var logo  = document.querySelector('.nav__logo');
  var inner = document.querySelector('.nav__inner');

  // Set active nav link based on current section
  document.querySelectorAll('.nav__link').forEach(function (link) {
    var href = link.getAttribute('href');
    var active = isVideos ? href === '/videos.html' : href === '/';
    link.classList.toggle('nav__link--active', active);
  });

  if (!logo || !inner) return;

  // Inject section label inside logo (CSS shows it on mobile only)
  var label = document.createElement('span');
  label.className = 'nav__section-label';
  label.textContent = isVideos ? 'My Videos' : 'My Photos';
  logo.appendChild(label);

  // Inject context switch button (CSS shows it on mobile only)
  var btn = document.createElement('a');
  btn.className = 'nav__mobile-btn';
  btn.href = isVideos ? '/' : '/videos.html';
  btn.textContent = isVideos ? 'My Photos' : 'My Videos';
  inner.appendChild(btn);

  // On mobile: logo navigates to section home rather than always to /
  function updateLogoHref() {
    logo.href = (window.innerWidth <= 768 && isVideos) ? '/videos.html' : '/';
  }
  updateLogoHref();
  window.addEventListener('resize', updateLogoHref);

}());
