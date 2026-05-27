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
 */
(function () {
  const params = new URLSearchParams(window.location.search);
  const from = params.get('from');
  if (!from) return;

  const map = {
    portfolio: { label: 'Portfolio',  url: '/photos/portfolio.html' },
    sarasota:  { label: 'Sarasota',   url: '/photos/usa/sarasota.html' },
    murales:   { label: 'Murales',    url: '/photos/murales.html' },
    home:      { label: 'My Photos',  url: '/' },
  };

  const dest = map[from];
  if (!dest) return;

  const link = document.querySelector('.page-header__back');
  if (!link) return;

  link.textContent = dest.label;
  link.href = dest.url;
})();
