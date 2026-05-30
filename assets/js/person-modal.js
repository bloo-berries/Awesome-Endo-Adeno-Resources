// /notable-people/ — clickable person cards with modal bio popup
// Activates only on the notable-people page. Each .person-card[role="button"]
// opens a modal showing the person's avatar, name, role, condition, and bio.
(function() {
    if (!/\/notable-people\/?$/.test(window.location.pathname)) return;

    var cards = document.querySelectorAll('.person-card[role="button"]');
    if (!cards.length) return;

    // ── Helpers ──────────────────────────────────────────────────────────
    function t(key, fallback) {
        try {
            var lang = localStorage.getItem('site-language') || 'en';
            var tr = (window.__i18nTranslations || {})[lang] || (window.__i18nTranslations || {}).en || {};
            return tr[key] || fallback;
        } catch (e) { return fallback; }
    }

    var prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');

    // ── Build reusable modal shell (hidden) ─────────────────────────────
    var backdrop = document.createElement('div');
    backdrop.className = 'person-modal-backdrop';
    backdrop.setAttribute('hidden', '');

    var dialog = document.createElement('div');
    dialog.className = 'person-modal';
    dialog.setAttribute('role', 'dialog');
    dialog.setAttribute('aria-modal', 'true');
    dialog.setAttribute('aria-labelledby', 'person-modal-name');

    var closeBtn = document.createElement('button');
    closeBtn.className = 'person-modal-close';
    closeBtn.type = 'button';
    closeBtn.setAttribute('aria-label', t('close', 'Close'));
    closeBtn.innerHTML =
        '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" ' +
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
        '<line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

    var body = document.createElement('div');
    body.className = 'person-modal-body';

    dialog.appendChild(closeBtn);
    dialog.appendChild(body);
    backdrop.appendChild(dialog);
    document.body.appendChild(backdrop);

    var triggerCard = null;

    // ── Open ─────────────────────────────────────────────────────────────
    function open(card) {
        triggerCard = card;

        var avatarEl = card.querySelector('.person-avatar');
        var name = (card.querySelector('.person-name') || {}).textContent || '';
        var role = (card.querySelector('.person-role') || {}).textContent || '';
        var condition = (card.querySelector('.person-condition') || {}).textContent || '';
        var bio = card.getAttribute('data-bio') || '';
        var detail = card.getAttribute('data-detail') || '';

        // Clone avatar content (img or initials text)
        var avatarHTML = '';
        var img = avatarEl ? avatarEl.querySelector('img') : null;
        if (img) {
            avatarHTML = '<img src="' + img.src + '" alt="' + (img.alt || name) + '">';
        } else if (avatarEl) {
            avatarHTML = '<span class="person-modal-initials">' +
                avatarEl.textContent.trim() + '</span>';
        }

        // Copy the computed gradient from the card avatar for initials
        var avatarStyle = '';
        if (!img && avatarEl) {
            avatarStyle = ' style="background:' +
                getComputedStyle(avatarEl).backgroundImage + '"';
        }

        body.innerHTML =
            '<div class="person-modal-avatar"' + avatarStyle + '>' + avatarHTML + '</div>' +
            '<h2 id="person-modal-name" class="person-modal-name">' + name + '</h2>' +
            (role ? '<p class="person-modal-role">' + role + '</p>' : '') +
            (condition ? '<span class="person-modal-condition">' + condition + '</span>' : '') +
            (bio ? '<p class="person-modal-bio">' + bio + '</p>' : '') +
            (detail ? '<p class="person-modal-detail">' + detail + '</p>' : '');

        backdrop.removeAttribute('hidden');
        document.body.style.overflow = 'hidden';

        // Focus close button after a frame so transition can start
        requestAnimationFrame(function() {
            backdrop.classList.add('is-visible');
            closeBtn.focus();
        });
    }

    // ── Close ────────────────────────────────────────────────────────────
    function close() {
        backdrop.classList.remove('is-visible');
        document.body.style.overflow = '';

        var duration = prefersReducedMotion.matches ? 0 : 250;
        setTimeout(function() {
            backdrop.setAttribute('hidden', '');
            body.innerHTML = '';
            if (triggerCard) {
                triggerCard.focus();
                triggerCard = null;
            }
        }, duration);
    }

    // ── Event listeners ──────────────────────────────────────────────────
    closeBtn.addEventListener('click', close);

    backdrop.addEventListener('click', function(e) {
        if (e.target === backdrop) close();
    });

    document.addEventListener('keydown', function(e) {
        if (backdrop.hasAttribute('hidden')) return;

        if (e.key === 'Escape') {
            e.preventDefault();
            close();
            return;
        }

        // Focus trap
        if (e.key === 'Tab') {
            var focusable = dialog.querySelectorAll(
                'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
            );
            if (!focusable.length) return;
            var first = focusable[0];
            var last = focusable[focusable.length - 1];

            if (e.shiftKey) {
                if (document.activeElement === first) {
                    e.preventDefault();
                    last.focus();
                }
            } else {
                if (document.activeElement === last) {
                    e.preventDefault();
                    first.focus();
                }
            }
        }
    });

    // ── Card activation ──────────────────────────────────────────────────
    cards.forEach(function(card) {
        card.addEventListener('click', function() { open(card); });
        card.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                open(card);
            }
        });
    });
})();
