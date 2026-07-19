/* Surgery Cost Tracker – fetch JSON, render cards, filtering, sorting, form submission */
(function() {
  'use strict';

  var PAGE_LOAD_TIME = Date.now();

  var cardsWrap = document.getElementById('sc-cards');
  if (!cardsWrap) return; // not on surgery-costs page

  var COUNTRY_META = {
    usa: ['\u{1F1FA}\u{1F1F8}', 'USA'],
    uk: ['\u{1F1EC}\u{1F1E7}', 'UK'],
    france: ['\u{1F1EB}\u{1F1F7}', 'France'],
    norway: ['\u{1F1F3}\u{1F1F4}', 'Norway'],
    canada: ['\u{1F1E8}\u{1F1E6}', 'Canada'],
    ireland: ['\u{1F1EE}\u{1F1EA}', 'Ireland'],
    lithuania: ['\u{1F1F1}\u{1F1F9}', 'Lithuania'],
    australia: ['\u{1F1E6}\u{1F1FA}', 'Australia'],
    newzealand: ['\u{1F1F3}\u{1F1FF}', 'New Zealand'],
    india: ['\u{1F1EE}\u{1F1F3}', 'India'],
    mexico: ['\u{1F1F2}\u{1F1FD}', 'Mexico'],
    greece: ['\u{1F1EC}\u{1F1F7}', 'Greece'],
    germany: ['\u{1F1E9}\u{1F1EA}', 'Germany'],
    portugal: ['\u{1F1F5}\u{1F1F9}', 'Portugal'],
    belgium: ['\u{1F1E7}\u{1F1EA}', 'Belgium'],
    turkey: ['\u{1F1F9}\u{1F1F7}', 'Turkey'],
    romania: ['\u{1F1F7}\u{1F1F4}', 'Romania'],
    denmark: ['\u{1F1E9}\u{1F1F0}', 'Denmark'],
    finland: ['\u{1F1EB}\u{1F1EE}', 'Finland'],
    china: ['\u{1F1E8}\u{1F1F3}', 'China'],
    poland: ['\u{1F1F5}\u{1F1F1}', 'Poland'],
    iceland: ['\u{1F1EE}\u{1F1F8}', 'Iceland'],
    pakistan: ['\u{1F1F5}\u{1F1F0}', 'Pakistan'],
    hongkong: ['\u{1F1ED}\u{1F1F0}', 'Hong Kong'],
    czechia: ['\u{1F1E8}\u{1F1FF}', 'Czechia'],
    netherlands: ['\u{1F1F3}\u{1F1F1}', 'Netherlands'],
    italy: ['\u{1F1EE}\u{1F1F9}', 'Italy'],
    spain: ['\u{1F1EA}\u{1F1F8}', 'Spain'],
    bulgaria: ['\u{1F1E7}\u{1F1EC}', 'Bulgaria'],
    notshared: ['\u{1F30D}', 'Not shared']
  };

  var BADGE_CLASS = {
    insured: 'b-insured',
    selfpay: 'b-selfpay',
    public: 'b-public',
    list: 'b-list',
    notshared: 'b-ns'
  };

  var DATA = [];
  var q = document.getElementById('sc-q');
  var fIns = document.getElementById('sc-f-ins');
  var fSort = document.getElementById('sc-f-sort');
  var countEl = document.getElementById('sc-count');
  var emptyEl = document.getElementById('sc-empty');
  var chipsEl = document.getElementById('sc-countries');

  var BATCH = 10;
  var moreWrap = document.getElementById('sc-more-wrap');
  var moreBtn = document.getElementById('sc-more');
  var state = { country: '', shown: BATCH };

  function esc(s) { return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;'); }
  function fmt(n) { return '$' + n.toLocaleString('en-US'); }

  /* ---- render a single report card as HTML ---- */
  function renderCard(r) {
    var badgeCls = BADGE_CLASS[r.insurance] || 'b-ns';
    var paidHL = esc(r.paid_display || '-');
    var provDetail = r.provider_detail ? '<p class="r-field"><span class="r-k">Provider detail</span><span class="r-v">' + esc(r.provider_detail) + '</span></p>' : '';
    var chargesHTML = '';
    if (r.charges_val) {
      chargesHTML = '<p class="r-field r-charges"><span class="r-k">Charges / quote</span><span class="r-v"><span class="fv">' + esc(r.charges_val) + '</span>' + (r.charges_note ? '<span class="ft">' + esc(r.charges_note) + '</span>' : '') + '</span></p>';
    }
    var paidHTML = '<p class="r-field r-paidrow"><span class="r-k">Patient paid</span><span class="r-v">';
    if (r.paid_val) {
      paidHTML += '<span class="fv hl">' + esc(r.paid_val) + '</span>';
    }
    if (r.paid_note) {
      paidHTML += '<span class="ft">' + esc(r.paid_note) + '</span>';
    }
    if (!r.paid_val && !r.paid_note) {
      paidHTML += '<span class="ft">-</span>';
    }
    paidHTML += '</span></p>';
    var notesHTML = r.notes ? '<p class="r-notes">' + esc(r.notes) + '</p>' : '';

    return '<details class="report" data-country="' + esc(r.country) + '" data-insurance="' + esc(r.insurance) + '" data-billed="' + r.billed + '" data-paid="' + r.paid + '">' +
      '<summary><div class="r-line1"><span class="r-tag">paid</span><span class="r-num hl">' + paidHL + '</span><span class="badge ' + badgeCls + '">' + esc(r.badge) + '</span></div>' +
      '<div class="r-line2"><span class="r-prov">' + esc(r.provider) + '</span><span class="r-loc">' + esc(r.location) + '</span></div></summary>' +
      '<div class="r-body">' + provDetail + chargesHTML + paidHTML + notesHTML + '</div></details>';
  }

  /* ---- build country chips ---- */
  function buildChips() {
    var byCountry = {};
    DATA.forEach(function(r) {
      (byCountry[r.country] = byCountry[r.country] || []).push(r);
    });
    var keys = Object.keys(byCountry).sort(function(a, b) {
      return byCountry[b].length - byCountry[a].length;
    });

    chipsEl.innerHTML = '';
    chipsEl.appendChild(makeChip('', 'All countries', null));
    keys.forEach(function(k) {
      var meta = COUNTRY_META[k] || ['\u{1F30D}', k];
      chipsEl.appendChild(makeChip(k, meta[0] + ' ' + meta[1], byCountry[k].length));
    });
    syncChips();
    return keys;
  }

  function makeChip(key, label, count) {
    var b = document.createElement('button');
    b.type = 'button';
    b.className = 'sc-chip';
    b.setAttribute('data-c', key);
    b.innerHTML = label + (count !== null ? ' <small>' + count + '</small>' : '');
    b.addEventListener('click', function() {
      state.country = (state.country === key && key !== '') ? '' : key;
      if (key === '') state.country = '';
      state.shown = BATCH;
      syncChips();
      apply();
      document.getElementById('sc-reports').scrollIntoView({ behavior: 'smooth' });
    });
    return b;
  }

  function syncChips() {
    Array.prototype.forEach.call(chipsEl.children, function(ch) {
      ch.classList.toggle('on', ch.getAttribute('data-c') === state.country);
    });
  }

  /* ---- pathway cards ---- */
  function pathStats(ins) {
    var subset = DATA.filter(function(r) { return r.insurance === ins; });
    var paids = subset.map(function(r) { return r.paid; }).filter(function(n) { return n >= 0; });
    var range = '';
    if (paids.length) {
      var mn = Math.min.apply(null, paids), mx = Math.max.apply(null, paids);
      range = 'paid <span class="hl">' + fmt(mn) + ' - ' + fmt(mx) + '</span>';
    }
    return { count: subset.length, range: range };
  }

  /* ---- headline stats ---- */
  function updateStats(countryKeys) {
    var cEl = document.getElementById('stat-count');
    if (cEl) cEl.textContent = DATA.length;
    var ic = document.getElementById('stat-inline-count');
    if (ic) ic.textContent = DATA.length;
    var cc = document.getElementById('stat-inline-countries');
    if (cc) cc.textContent = countryKeys.filter(function(k) { return k !== 'notshared'; }).length;

    ['insured', 'selfpay', 'public'].forEach(function(ins) {
      var st = pathStats(ins);
      var pc = document.getElementById('pc-' + ins);
      var pr = document.getElementById('pr-' + ins);
      if (pc) pc.textContent = st.count + ' reports';
      if (pr) pr.innerHTML = st.range;
    });

    var ins = pathStats('insured');
    function bare(st) {
      return st.range ? st.range.replace(/<[^>]+>/g, '').replace('paid ', '') : '';
    }
    var insEl = document.getElementById('stat-insured');
    if (insEl && ins.range) insEl.textContent = bare(ins);

    var spPaids = DATA.filter(function(r) { return r.insurance === 'selfpay'; })
      .map(function(r) { var p = r.paid; return p >= 0 ? p : r.billed; })
      .filter(function(n) { return n >= 0; });
    var spEl = document.getElementById('stat-selfpay');
    if (spEl && spPaids.length) {
      spEl.textContent = fmt(Math.min.apply(null, spPaids)) + ' - ' + fmt(Math.max.apply(null, spPaids));
    }
  }

  /* ---- filtering and sorting (all reports shown) ---- */
  function apply() {
    var term = q.value.trim().toLowerCase();
    var ins = fIns.value;
    var visible = DATA.filter(function(r) {
      var okC = !state.country || r.country === state.country;
      var okI = !ins || r.insurance === ins;
      var okQ = !term || (r.provider + ' ' + r.location + ' ' + r.notes + ' ' + r.provider_detail + ' ' + r.charges_val + ' ' + r.charges_note + ' ' + r.paid_note).toLowerCase().indexOf(term) !== -1;
      return okC && okI && okQ;
    });

    var sort = fSort.value;
    if (sort) {
      var parts = sort.split('-');
      var field = parts[0];
      var dir = parts[1];
      visible = visible.slice().sort(function(a, b) {
        var av = a[field], bv = b[field];
        var aU = av < 0, bU = bv < 0;
        if (aU && bU) return 0;
        if (aU) return 1;
        if (bU) return -1;
        return dir === 'asc' ? av - bv : bv - av;
      });
    }

    var slice = visible.slice(0, state.shown);
    var html = '';
    slice.forEach(function(r) { html += renderCard(r); });
    cardsWrap.innerHTML = html;
    cardsWrap.style.display = 'grid';

    var remaining = visible.length - state.shown;
    if (remaining > 0) {
      moreWrap.hidden = false;
      var next = Math.min(remaining, BATCH);
      moreBtn.textContent = 'Show ' + next + ' more of ' + remaining + ' remaining';
    } else {
      moreWrap.hidden = true;
    }

    emptyEl.hidden = visible.length !== 0;
    countEl.textContent = 'Showing ' + Math.min(state.shown, visible.length) + ' of ' + visible.length +
      ' report' + (visible.length === 1 ? '' : 's') +
      (visible.length !== DATA.length ? ' (filtered)' : '');
  }

  q.addEventListener('input', function() { state.shown = BATCH; apply(); });
  fIns.addEventListener('change', function() { state.shown = BATCH; apply(); });
  fSort.addEventListener('change', function() { state.shown = BATCH; apply(); });

  moreBtn.addEventListener('click', function() {
    state.shown += BATCH;
    apply();
  });

  Array.prototype.forEach.call(document.querySelectorAll('.sc-path'), function(btn) {
    btn.addEventListener('click', function() {
      fIns.value = btn.getAttribute('data-ins');
      state.country = '';
      state.shown = BATCH;
      syncChips();
      apply();
      document.getElementById('sc-reports').scrollIntoView({ behavior: 'smooth' });
    });
  });

  /* ---- form submission ---- */
  var form = document.getElementById('sc-form');
  var confirmEl = document.getElementById('sc-confirm');
  var dismissBtn = document.getElementById('sc-confirm-dismiss');

  if (form) {
    form.addEventListener('submit', function(e) {
      e.preventDefault();

      // Time-check: reject submissions within 3 seconds of page load
      if (Date.now() - PAGE_LOAD_TIME < 3000) return;

      // Honeypot check
      var honeypot = form.querySelector('[name="_gotcha"]');
      if (honeypot && honeypot.value) return;

      var data = new FormData(form);

      fetch(form.action, {
        method: 'POST',
        body: data,
        headers: { 'Accept': 'application/json' }
      }).then(function(response) {
        if (response.ok) {
          form.hidden = true;
          confirmEl.hidden = false;
          confirmEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        } else {
          alert('Something went wrong. Please try again or contact us directly.');
        }
      }).catch(function() {
        alert('Network error. Please check your connection and try again.');
      });
    });
  }

  if (dismissBtn) {
    dismissBtn.addEventListener('click', function() {
      confirmEl.hidden = true;
      form.hidden = false;
      form.reset();
    });
  }

  /* ---- Fetch data and initialize ---- */
  var dataUrl = window.__searchIndexURL ? window.__searchIndexURL.replace('index.json', 'data/surgery-reports.json') : '/data/surgery-reports.json';
  fetch(dataUrl)
    .then(function(res) { return res.json(); })
    .then(function(data) {
      DATA = data;
      var countryKeys = buildChips();
      updateStats(countryKeys);
      apply();
    });
})();
