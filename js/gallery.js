(function () {
  var widget = document.querySelector('.pa-gallery-player-widget');
  if (!widget) return;

  // Insert shimmer skeleton in place of the hidden widget while publicalbum loads.
  var skeleton = document.createElement('div');
  skeleton.className = 'gallery-skeleton';
  widget.parentNode.insertBefore(skeleton, widget);

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

  // publicalbum replaces the <div> with an <iframe> that has no title attribute,
  // which fails the accessibility audit. Watch for the iframe and label it.
  var albumTitle = widget.getAttribute('data-title') || 'Photo gallery';
  var observer = new MutationObserver(function (mutations) {
    for (var i = 0; i < mutations.length; i++) {
      var nodes = mutations[i].addedNodes;
      for (var j = 0; j < nodes.length; j++) {
        var node = nodes[j];
        if (node.tagName === 'IFRAME' && !node.title) {
          node.title = albumTitle;
          node.addEventListener('load', function () {
            if (skeleton.parentNode) skeleton.parentNode.removeChild(skeleton);
            primeTouchAutoplay(node);
          });
          observer.disconnect();
          return;
        }
        if (node.querySelectorAll) {
          var iframes = node.querySelectorAll('iframe:not([title])');
          for (var k = 0; k < iframes.length; k++) {
            iframes[k].title = albumTitle;
            iframes[k].addEventListener('load', function () {
              if (skeleton.parentNode) skeleton.parentNode.removeChild(skeleton);
              primeTouchAutoplay(this);
            });
          }
          if (iframes.length) {
            observer.disconnect();
            return;
          }
        }
      }
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });

  // On mobile, the publicalbum widget (same-origin srcdoc iframe) requires a
  // touchmove event to have occurred before the play button can start autoplay.
  // Dispatching a synthetic 1px swipe at load time primes the widget invisibly —
  // 1px is well below the photo-navigation threshold so no visual change occurs.
  function primeTouchAutoplay(iframe) {
    if (!iframe || !('ontouchstart' in window)) return;
    setTimeout(function () {
      try {
        var doc = iframe.contentDocument;
        if (!doc || !doc.body) return;
        var w = doc.documentElement.clientWidth || iframe.clientWidth || 300;
        var h = doc.documentElement.clientHeight || iframe.clientHeight || 200;
        var cx = w / 2;
        var cy = h / 2;
        var el = doc.elementFromPoint(cx, cy) || doc.body;
        var t1 = new Touch({ identifier: 1, target: el, clientX: cx,     clientY: cy, pageX: cx,     pageY: cy });
        var t2 = new Touch({ identifier: 1, target: el, clientX: cx + 1, clientY: cy, pageX: cx + 1, pageY: cy });
        el.dispatchEvent(new TouchEvent('touchstart', { bubbles: true, cancelable: true, touches: [t1], targetTouches: [t1], changedTouches: [t1] }));
        el.dispatchEvent(new TouchEvent('touchmove',  { bubbles: true, cancelable: true, touches: [t2], targetTouches: [t2], changedTouches: [t2] }));
        el.dispatchEvent(new TouchEvent('touchend',   { bubbles: true, cancelable: true, touches: [],   targetTouches: [],   changedTouches: [t2] }));
      } catch (e) {}
    }, 400);
  }
}());
