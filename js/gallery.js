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
            enableMobileAutoplay(node);
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
              enableMobileAutoplay(this);
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

  // On mobile, the play button sets f=true but autoplay never starts because
  // Jh() (the autoplay gate) is only triggered from touchend — not from the
  // play button's click handler, and not from mousemove (which doesn't exist
  // on touch). We listen for any click inside the same-origin srcdoc iframe,
  // then dispatch a zero-movement touchstart+touchend. No touchmove means the
  // K (swiping) flag is never set, so no navigation occurs and Jh() sees
  // f && !K && items>1 and starts the timer.
  function enableMobileAutoplay(iframe) {
    if (!iframe || !('ontouchstart' in window)) return;
    setTimeout(function () {
      try {
        var doc = iframe.contentDocument;
        if (!doc || !doc.body) return;
        var w = doc.documentElement.clientWidth || iframe.clientWidth || 375;
        var h = doc.documentElement.clientHeight || iframe.clientHeight || 300;
        var cx = w / 2;
        var cy = h / 2;

        doc.addEventListener('click', function () {
          // Wait 50ms for the click handler (e.g. play button) to set f,
          // then fire touchstart+touchend at the same point. Jh() checks f
          // before starting — safe to fire on pause clicks too (f=false → no-op).
          setTimeout(function () {
            try {
              var target = doc.querySelector('.jx-gallery-player') || doc.body;
              var touch = new Touch({ identifier: Date.now(), target: target, clientX: cx, clientY: cy, pageX: cx, pageY: cy });
              target.dispatchEvent(new TouchEvent('touchstart', { bubbles: true, cancelable: true, touches: [touch], changedTouches: [touch] }));
              target.dispatchEvent(new TouchEvent('touchend',   { bubbles: true, cancelable: true, touches: [],      changedTouches: [touch] }));
            } catch (e) {}
          }, 50);
        });
      } catch (e) {}
    }, 400);
  }
}());
