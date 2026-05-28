(function () {
  var widget = document.querySelector('.pa-gallery-player-widget');
  if (!widget) return;

  // On mobile, rewrite photo URLs to a smaller size before publicalbum reads them.
  // The CDN supports arbitrary resize params — w800-h450 is ~6x smaller than w1920-h1080.
  if (window.innerWidth <= 768) {
    var objects = widget.querySelectorAll('object[data]');
    for (var i = 0; i < objects.length; i++) {
      objects[i].setAttribute('data',
        objects[i].getAttribute('data').replace(/=w\d+-h\d+$/, '=w800-h450'));
    }
  }

  // Inject "View full album in Google Photos" link after the widget.
  var url = widget.getAttribute('data-link');
  if (url) {
    var p = document.createElement('p');
    p.className = 'gallery-cta';
    p.innerHTML = '<a href="' + url + '" target="_blank" rel="noopener">View full album in Google Photos ↗</a>';
    widget.parentNode.insertBefore(p, widget.nextSibling);
  }
}());
