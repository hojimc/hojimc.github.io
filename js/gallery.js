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
  // Fix: navigate publicalbum's internal Closure object graph to find the carousel
  // widget (Wg) and call its slide-advance handlers (cgmove + cgfinish) directly,
  // bypassing the broken synthetic-touch-event path entirely.
  // Detection: watch the big overlay play button (last .jx-svg-round-button,
  // display:flex) — it changes to display:none when the user taps play.
  function enableMobileAutoplay(iframe) {
    if (!iframe || !('ontouchstart' in window)) return;
    setTimeout(function () {
      try {
        var doc = iframe.contentDocument;
        if (!doc) return;

        // --- Walk the Closure object graph to reach the Wg carousel instance ---
        // Path: .jx-swipe-base → lm key → touchstart listener → Ag → Dg → Wg
        var swipeBase = doc.querySelector('.jx-swipe-base');
        if (!swipeBase) return;

        var lmKey = null;
        var sbKeys = Object.getOwnPropertyNames(swipeBase);
        for (var i = 0; i < sbKeys.length; i++) {
          if (sbKeys[i].indexOf('closure_lm') === 0) { lmKey = sbKeys[i]; break; }
        }
        if (!lmKey) return;

        var lm = swipeBase[lmKey];
        var tsRaw = lm && lm.a && lm.a['touchstart'];
        if (!tsRaw) return;
        var tsL = Array.isArray(tsRaw) ? tsRaw[0] : tsRaw;
        if (!tsL) return;

        // Find Ag instance: the listener scope object whose .a === swipeBase
        var agInst = null;
        var tsProps = Object.getOwnPropertyNames(tsL);
        for (var i = 0; i < tsProps.length; i++) {
          var v = tsL[tsProps[i]];
          if (v && typeof v === 'object' && v.a === swipeBase) { agInst = v; break; }
        }
        if (!agInst || !agInst.O || !agInst.O.a) return;

        // Find Dg instance: a scope object on any of Ag's event listeners that has
        // an EventTarget O.a with cg* event types (registered by Wg on Dg)
        var dgInst = null;
        var agTypes = Object.keys(agInst.O.a);
        outer: for (var i = 0; i < agTypes.length && !dgInst; i++) {
          var agLRaw = agInst.O.a[agTypes[i]];
          var agLArr = Array.isArray(agLRaw) ? agLRaw : [agLRaw];
          for (var j = 0; j < agLArr.length && !dgInst; j++) {
            var lProps = Object.getOwnPropertyNames(agLArr[j] || {});
            for (var k = 0; k < lProps.length; k++) {
              var v = agLArr[j][lProps[k]];
              if (v && typeof v === 'object' && v.O && v.O.a) {
                var innerTypes = Object.keys(v.O.a);
                for (var m = 0; m < innerTypes.length; m++) {
                  if (innerTypes[m].indexOf('cg') === 0) { dgInst = v; break; }
                }
              }
              if (dgInst) break;
            }
          }
        }
        if (!dgInst || !dgInst.O || !dgInst.O.a) return;

        // Find Wg instance: scope on Dg's cgtart listener with h, l, R properties
        var wgInst = null;
        var cgtartRaw = dgInst.O.a['cgtart'];
        if (cgtartRaw) {
          var cgtartArr = Array.isArray(cgtartRaw) ? cgtartRaw : [cgtartRaw];
          var cgtProps = Object.getOwnPropertyNames(cgtartArr[0] || {});
          for (var k = 0; k < cgtProps.length; k++) {
            var v = (cgtartArr[0] || {})[cgtProps[k]];
            if (v && typeof v === 'object' && 'h' in v && 'l' in v && 'R' in v) { wgInst = v; break; }
          }
        }
        if (!wgInst) return;

        var cgmoveRaw = dgInst.O.a['cgmove'];
        var cgfinishRaw = dgInst.O.a['cgfinish'];
        if (!cgmoveRaw || !cgfinishRaw) return;
        var gcFn = (Array.isArray(cgmoveRaw) ? cgmoveRaw[0] : cgmoveRaw).listener;
        var fcFn = (Array.isArray(cgfinishRaw) ? cgfinishRaw[0] : cgfinishRaw).listener;
        if (!gcFn || !fcFn) return;

        // Use a fixed offset of 40% of viewport — always above the 20% threshold
        var offset = -(doc.documentElement.clientWidth || iframe.clientWidth || 390) * 0.4;
        var autoplayTimer = null;

        function advanceSlide() {
          try {
            gcFn.call(wgInst, { offset: offset });
            fcFn.call(wgInst, { offset: offset });
          } catch (e) {}
        }

        // Watch the big play button: display:flex → :none means user tapped play
        var allBtns = doc.querySelectorAll('.jx-svg-round-button');
        var bigBtn = null;
        for (var i = allBtns.length - 1; i >= 0; i--) {
          if (allBtns[i].style.display === 'flex') { bigBtn = allBtns[i]; break; }
        }
        if (!bigBtn) return;

        new MutationObserver(function () {
          if (bigBtn.style.display !== 'flex' && autoplayTimer === null) {
            autoplayTimer = setInterval(advanceSlide, 5000);
          } else if (bigBtn.style.display === 'flex' && autoplayTimer !== null) {
            clearInterval(autoplayTimer);
            autoplayTimer = null;
          }
        }).observe(bigBtn, { attributes: true, attributeFilter: ['style'] });

      } catch (e) {}
    }, 400);
  }
}());
