/**
 * auth.js — Client-side password protection for static pages
 * ============================================================
 *
 * Usage: Add to any page's <head>:
 *   <script src="/js/auth.js" data-hash="YOUR_SHA256_HASH_HERE" defer></script>
 *
 * To generate a hash for a new password, paste this into your browser console
 * (on any page of the site) and press Enter:
 *
 *   (async () => {
 *     const buf = await crypto.subtle.digest(
 *       'SHA-256',
 *       new TextEncoder().encode('your-password-here')
 *     );
 *     console.log([...new Uint8Array(buf)].map(b => b.toString(16).padStart(2,'0')).join(''));
 *   })();
 *
 * Copy the hex string it logs and paste it as the data-hash attribute above.
 *
 * Security note:
 *   This is client-side auth — not suitable for highly sensitive data.
 *   It's appropriate for gating personal/family photos from casual visitors.
 *   The password itself is never stored; only its SHA-256 hash is in the HTML.
 */

(function () {
  'use strict';

  const script     = document.currentScript;
  const targetHash = (script.getAttribute('data-hash') || '').toLowerCase().trim();

  // No hash provided → page is public, do nothing
  if (!targetHash) return;

  // Use first 16 chars of hash as a unique sessionStorage key
  const sessionKey = 'auth_' + targetHash.slice(0, 16);

  // Already authenticated this browser session? Show page immediately.
  if (sessionStorage.getItem(sessionKey) === 'ok') return;

  // ── Build and inject the overlay ─────────────────────────────
  function buildOverlay() {
    const overlay = document.createElement('div');
    overlay.className = 'auth-overlay';
    overlay.id        = 'auth-overlay';
    overlay.setAttribute('role',       'dialog');
    overlay.setAttribute('aria-modal', 'true');
    overlay.setAttribute('aria-label', 'Password required');

    overlay.innerHTML = `
      <div class="auth-box">
        <div class="auth-icon">🔒</div>
        <h2 class="auth-title">Password required</h2>
        <p class="auth-subtitle">This page is private. Please enter the password to continue.</p>
        <form class="auth-form" id="auth-form" autocomplete="off" novalidate>
          <input
            type="password"
            class="auth-input"
            id="auth-input"
            placeholder="Enter password"
            autocomplete="current-password"
            required
          />
          <button type="submit" class="auth-btn">Enter &rarr;</button>
        </form>
        <p class="auth-error" id="auth-error" role="alert" aria-live="polite"></p>
      </div>
    `;

    document.body.appendChild(overlay);

    // Back link — lets users navigate away without knowing the password
    var backEl = document.querySelector('.page-header__back');
    if (backEl) {
      var authBack = document.createElement('a');
      authBack.href = backEl.getAttribute('href');
      authBack.className = 'auth-back';
      authBack.textContent = backEl.textContent.trim();
      overlay.querySelector('.auth-box').appendChild(authBack);
    }

    // Autofocus the password field
    const input   = overlay.querySelector('#auth-input');
    const errorEl = overlay.querySelector('#auth-error');
    setTimeout(function () { input.focus(); }, 60);

    // ── Form submit handler ──────────────────────────────────────
    overlay.querySelector('#auth-form').addEventListener('submit', async function (e) {
      e.preventDefault();
      const password = input.value;
      if (!password) return;

      try {
        const hash = await sha256(password);

        if (hash === targetHash) {
          // ✅ Correct password
          sessionStorage.setItem(sessionKey, 'ok');
          overlay.classList.add('auth-overlay--exit');
          setTimeout(function () { overlay.remove(); }, 350);

        } else {
          // ❌ Wrong password
          errorEl.textContent = 'Incorrect password — please try again.';
          input.classList.add('auth-input--shake');
          input.value = '';
          input.focus();
          setTimeout(function () {
            input.classList.remove('auth-input--shake');
          }, 500);
        }

      } catch (err) {
        errorEl.textContent = 'Something went wrong. Please reload and try again.';
        console.error('[auth.js]', err);
      }
    });
  }

  // ── SHA-256 via Web Crypto API (zero dependencies) ───────────
  async function sha256(message) {
    const data        = new TextEncoder().encode(message);
    const hashBuffer  = await crypto.subtle.digest('SHA-256', data);
    const hashArray   = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(function (b) {
      return b.toString(16).padStart(2, '0');
    }).join('');
  }

  // Run once DOM is available (script has defer, so DOM is ready)
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', buildOverlay);
  } else {
    buildOverlay();
  }

})();
