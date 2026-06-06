/**
 * breadcrumb.js — Dynamic breadcrumb swapping via ?from= URL parameter.
 *
 * Some album pages are reachable from multiple parent pages (e.g. Birds of Sarasota
 * appears under both Florida and Portfolio). When a parent page links here with
 * ?from=<key>, this script swaps the breadcrumb link to point back to that parent.
 * If no ?from= is present, the default breadcrumb in the HTML is used as-is.
 *
 * Usage: add <script src="/js/breadcrumb.js" defer></script> to any page that can
 * be reached from more than one parent. The linking page appends ?from=<key> to its href.
 */
(function () {
  const params = new URLSearchParams(window.location.search);
  const from = params.get('from');
  if (!from) return;

  const map = {
    // ── Photo keys ──────────────────────────────────────────────────────────
    home:              { label: 'My Photos',       url: '/' },
    portfolio:         { label: 'Portfolio',       url: '/photos/portfolio.html' },
    usa:               { label: 'USA',             url: '/photos/usa.html' },
    florida:           { label: 'Florida',         url: '/photos/usa/florida.html' },
    europe:            { label: 'Europe',          url: '/photos/europe.html' },
    caraibes:          { label: 'Caraïbes',        url: '/photos/caraibes.html' },
    murales:           { label: 'Murales',         url: '/photos/murales.html' },
    famille:           { label: 'Famille',         url: '/photos/famille.html' },
    california:        { label: 'California',      url: '/photos/usa/california.html' },
    'amusement-parks': { label: 'Amusement Parks', url: '/photos/usa/amusement-parks.html' },
    'europe-2013':     { label: 'Europe 2013',     url: '/photos/europe/europe-2013.html' },
    'lille-2014':      { label: 'Lille',           url: '/photos/europe/lille-2014.html' },
    'espagne-2018':    { label: 'Espagne 2018',    url: '/photos/europe/espagne-2018.html' },
    // ── Video keys ──────────────────────────────────────────────────────────
    videos:              { label: 'My Videos',        url: '/videos.html' },
    'videos-florida':    { label: 'Florida',          url: '/videos/florida.html' },
    'videos-europe':     { label: 'Europe',           url: '/videos/europe.html' },
    'videos-canada':     { label: 'Canada',           url: '/videos/canada.html' },
    'videos-fp':         { label: 'French Polynesia', url: '/videos/french-polynesia.html' },
    australia:           { label: 'Australia',        url: '/videos/australia.html' },
    'videos-famille':    { label: 'Famille',          url: '/videos/famille.html' },
    drone:               { label: 'Drone Videos',     url: '/videos/drone.html' },
    beaches:             { label: 'Beaches',          url: '/videos/drone/beaches.html' },
    biking:              { label: 'Biking',           url: '/videos/drone/biking.html' },
    'hot-springs':       { label: 'Hot Springs',      url: '/videos/drone/hot-springs.html' },
    pickleball:          { label: 'Pickleball',       url: '/videos/drone/pickleball.html' },
    'felix-et-anais':    { label: 'Félix et Anaïs',   url: '/videos/felix-et-anais.html' },
    'videos-de-felix':   { label: 'Vidéos de Félix',  url: '/videos/videos-de-felix.html' },
    olivier:             { label: 'Olivier',           url: '/videos/famille/olivier.html' },
  };

  const dest = map[from];
  if (!dest) return;

  const link = document.querySelector('.page-header__back');
  if (!link) return;

  link.textContent = dest.label;
  link.href = dest.url;
})();
