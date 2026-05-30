/**
 * breadcrumb.js — Dynamic breadcrumb swapping via ?from= URL parameter.
 *
 * Some album pages are reachable from multiple parent pages (e.g. Birds of Sarasota
 * appears under both Sarasota and Portfolio). When a parent page links here with
 * ?from=<key>, this script swaps the breadcrumb link to point back to that parent.
 * If no ?from= is present, the default breadcrumb in the HTML is used as-is.
 *
 * Usage: add <script src="/js/breadcrumb.js" defer></script> to any page that can
 * be reached from more than one parent. The linking page appends ?from=<key> to its href.
 *
 * Supported keys:
 *   portfolio → Portfolio (/photos/portfolio.html)
 *   sarasota  → Sarasota  (/photos/usa/sarasota.html)
 *   murales   → Murales   (/photos/murales.html)
 *   home      → My Photos (/)
 *   — video keys —
 *   videos         → My Videos      (/videos.html)
 *   drone          → Drone Videos   (/videos/drone.html)
 *   felix-et-anais → Félix et Anaïs (/videos/felix-et-anais.html)
 *   travel         → Travel Videos  (/videos/travel.html)
 *   other          → Other          (/videos/other.html)
 *   videos-de-felix → Vidéos de Félix (/videos/other/videos-de-felix.html)
 *   olivier        → Olivier        (/videos/other/olivier.html)
 */
(function () {
  const params = new URLSearchParams(window.location.search);
  const from = params.get('from');
  if (!from) return;

  const map = {
    home:           { label: 'My Photos',      url: '/' },
    portfolio:      { label: 'Portfolio',      url: '/photos/portfolio.html' },
    usa:            { label: 'USA',            url: '/photos/usa.html' },
    europe:         { label: 'Europe',         url: '/photos/europe.html' },
    caraibes:       { label: 'Caraïbes',       url: '/photos/caraibes.html' },
    murales:        { label: 'Murales',        url: '/photos/murales.html' },
    sarasota:       { label: 'Sarasota',       url: '/photos/usa/sarasota.html' },
    vacances:       { label: 'Vacances',       url: '/photos/usa/vacances.html' },
    california:     { label: 'California',     url: '/photos/usa/california.html' },
    'amusement-parks': { label: 'Amusement Parks', url: '/photos/usa/amusement-parks.html' },
    'europe-2013':  { label: 'Europe 2013',    url: '/photos/europe/europe-2013.html' },
    'lille-2014':   { label: 'Lille',          url: '/photos/europe/lille-2014.html' },
    'espagne-2018': { label: 'Espagne 2018',   url: '/photos/europe/espagne-2018.html' },
    videos:            { label: 'My Videos',       url: '/videos.html' },
    drone:             { label: 'Drone Videos',    url: '/videos/drone.html' },
    'felix-et-anais':  { label: 'Félix et Anaïs',  url: '/videos/felix-et-anais.html' },
    travel:            { label: 'Travel Videos',   url: '/videos/travel.html' },
    other:             { label: 'Other',            url: '/videos/other.html' },
    'videos-de-felix': { label: 'Vidéos de Félix', url: '/videos/other/videos-de-felix.html' },
    olivier:           { label: 'Olivier',          url: '/videos/other/olivier.html' },
  };

  const dest = map[from];
  if (!dest) return;

  const link = document.querySelector('.page-header__back');
  if (!link) return;

  link.textContent = dest.label;
  link.href = dest.url;
})();
