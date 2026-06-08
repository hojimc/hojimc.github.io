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

  // On mobile, publicalbum's autoplay never starts after tapping the play button.
  // Root cause: the button tap fires touchend (which publicalbum intercepts and
  // likely calls preventDefault on, suppressing the synthetic click), then sets
  // f=true internally — but nothing subsequently triggers the autoplay timer.
  // Fix: intercept the play button's touchend in capture phase (before publicalbum
  // handles it), track play/pause state ourselves, and drive the carousel with our
  // own setInterval that dispatches a forward swipe every 5s. A left swipe
  // (finger moves left = next image) uses >20% of carousel width to clear
  // publicalbum's navigation threshold (Zg=0.2). Confirmed via prior testing that
  // synthetic touchstart+touchmove+touchend on .jx-gallery-player does reach and
  // trigger publicalbum's swipe handler.
  function enableMobileAutoplay(iframe) {
    if (!iframe || !('ontouchstart' in window)) return;
    setTimeout(function () {
      try {
        var doc = iframe.contentDocument;
        if (!doc || !doc.body) return;
        var playBtn = doc.querySelector('.jx-svg-round-button');
        if (!playBtn) return;

        var w = doc.documentElement.clientWidth || iframe.clientWidth || 375;
        var h = doc.documentElement.clientHeight || iframe.clientHeight || 300;
        var cx = w / 2;
        var cy = h / 2;
        var dx = Math.ceil(w * 0.25); // 25% — above the 20% navigation threshold

        var playing = false;
        var autoplayTimer = null;

        function swipeForward() {
          try {
            var target = doc.querySelector('.jx-gallery-player') || doc.body;
            var id = Date.now();
            var t1 = new Touch({ identifier: id, target: target, clientX: cx,      clientY: cy, pageX: cx,      pageY: cy });
            var t2 = new Touch({ identifier: id, target: target, clientX: cx - dx, clientY: cy, pageX: cx - dx, pageY: cy });
            target.dispatchEvent(new TouchEvent('touchstart', { bubbles: true, cancelable: true, touches: [t1], changedTouches: [t1] }));
            target.dispatchEvent(new TouchEvent('touchmove',  { bubbles: true, cancelable: true, touches: [t2], changedTouches: [t2] }));
            target.dispatchEvent(new TouchEvent('touchend',   { bubbles: true, cancelable: true, touches: [],   changedTouches: [t2] }));
          } catch (err) {}
        }

        // Capture phase: fires before publicalbum's touchend handler, ensuring we
        // track the toggle on every play/pause tap even if propagation is stopped.
        playBtn.addEventListener('touchend', function () {
          playing = !playing;
          if (playing) {
            autoplayTimer = setInterval(swipeForward, 5000);
          } else {
            clearInterval(autoplayTimer);
            autoplayTimer = null;
          }
        }, true);

      } catch (e) {}
    }, 400);
  }
}());
