'use strict';

document.addEventListener('DOMContentLoaded', function () {
  var form = document.getElementById('main-form');
  if (!form) return;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    submitForm(form);
  });
});

function submitForm(form) {
  var submitBtn = document.getElementById('submit-btn');
  var logWrap   = document.getElementById('log-wrap');
  var logEl     = document.getElementById('log');
  var pwLabel   = document.getElementById('pw-label'); // hash page only

  // Gather form data into a plain object
  var data = {};
  var elements = form.elements;
  for (var i = 0; i < elements.length; i++) {
    var el = elements[i];
    if (!el.name || el.disabled) continue;
    if (el.type === 'radio' && !el.checked) continue;
    if (el.type === 'checkbox') {
      data[el.name] = el.checked;
    } else {
      data[el.name] = el.value;
    }
  }

  // Validate required fields
  var missing = [];
  var requiredEls = form.querySelectorAll('[required]');
  requiredEls.forEach(function (el) {
    if (!el.value.trim()) {
      missing.push(el.closest('.form__field'));
      el.classList.add('input--error');
    } else {
      el.classList.remove('input--error');
    }
  });
  if (missing.length) {
    showLog(logWrap, logEl, 'Please fill in all required fields (marked with *).', false);
    missing[0].querySelector('input, select, textarea').focus();
    return;
  }

  // Loading state
  submitBtn.disabled = true;
  submitBtn.classList.add('btn--loading');

  // Show log panel immediately with "Running…"
  logWrap.hidden = false;
  logEl.textContent = 'Running…';
  logEl.className = 'log';
  logWrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

  // Determine endpoint from action or current path
  var endpoint = window.location.pathname;

  fetch(endpoint, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  .then(function (res) { return res.json(); })
  .then(function (json) {
    var text = json.output || json.hash || '';
    showLog(logWrap, logEl, text, json.success !== false);

    // Hash page: update the heading with the password name
    if (pwLabel && data.password) {
      pwLabel.textContent = '“' + data.password + '”';
    }
  })
  .catch(function (err) {
    showLog(logWrap, logEl, 'Network error: ' + err.message, false);
  })
  .finally(function () {
    submitBtn.disabled = false;
    submitBtn.classList.remove('btn--loading');
  });
}

function showLog(logWrap, logEl, text, success) {
  logWrap.hidden = false;
  logEl.textContent = text;
  logEl.className = 'log ' + (success ? 'log--success' : 'log--error');
  logWrap.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Clear input error highlight on change
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.form__input').forEach(function (el) {
    el.addEventListener('input', function () {
      el.classList.remove('input--error');
    });
  });
});
