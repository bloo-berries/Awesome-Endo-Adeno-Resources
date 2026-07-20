// /notable-people/ - clickable person cards with modal bio popup
// Activates only on the notable-people page. Each .person-card[role="button"]
// opens a modal showing the person's avatar, name, role, condition, and bio.
(function() {
    var cards = document.querySelectorAll('.person-card[role="button"]');
    if (!cards.length) return;

    // ── Helpers ──────────────────────────────────────────────────────────
    function t(key, fallback) {
        return window.__ti18n ? window.__ti18n(key, fallback) : fallback;
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
    var cardsArray = Array.prototype.slice.call(cards);

    function currentIndex() {
        return triggerCard ? cardsArray.indexOf(triggerCard) : -1;
    }

    function navigateToCard(direction) {
        var idx = currentIndex();
        if (idx === -1) return;
        var next = idx + direction;
        if (next < 0) next = cardsArray.length - 1;
        if (next >= cardsArray.length) next = 0;
        triggerCard = cardsArray[next];
        open(triggerCard);
    }

    // ── i18n helper for data attributes ─────────────────────────────────
    function ti18n(key) {
        if (!key) return '';
        return window.__ti18n ? window.__ti18n(key, '') : '';
    }

    // ── Open ─────────────────────────────────────────────────────────────
    function open(card) {
        triggerCard = card;

        var avatarEl = card.querySelector('.person-avatar');
        var name = (card.querySelector('.person-name') || {}).textContent || '';
        var role = (card.querySelector('.person-role') || {}).textContent || '';
        var condition = (card.querySelector('.person-condition') || {}).textContent || '';
        // Use i18n translations for bio/detail when available
        var bioKey = card.getAttribute('data-i18n-bio');
        var detailKey = card.getAttribute('data-i18n-detail');
        var bio = ti18n(bioKey) || card.getAttribute('data-bio') || '';
        var detail = ti18n(detailKey) || card.getAttribute('data-detail') || '';
        var wiki = card.getAttribute('data-wiki') || '';
        var link = card.getAttribute('data-link') || '';

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
            (detail ? '<p class="person-modal-detail">' + detail + '</p>' : '') +
            (wiki ? '<a class="person-modal-wiki" href="' + wiki + '" target="_blank" rel="noopener noreferrer">Wikipedia \u2197</a>' : '') +
            (link ? '<a class="person-modal-wiki" href="' + link + '" target="_blank" rel="noopener noreferrer">' + t('read_more', 'Read more') + ' \u2197</a>' : '');

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

        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            navigateToCard(-1);
            return;
        }
        if (e.key === 'ArrowRight') {
            e.preventDefault();
            navigateToCard(1);
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

    // ── Swipe navigation (mobile) ───────────────────────────────────────
    var touchStartX = 0;
    var touchStartY = 0;

    dialog.addEventListener('touchstart', function(e) {
        var touch = e.changedTouches[0];
        touchStartX = touch.clientX;
        touchStartY = touch.clientY;
    }, { passive: true });

    dialog.addEventListener('touchend', function(e) {
        var touch = e.changedTouches[0];
        var dx = touch.clientX - touchStartX;
        var dy = touch.clientY - touchStartY;

        // Only trigger if horizontal swipe > 50px and more horizontal than vertical
        if (Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
            navigateToCard(dx < 0 ? 1 : -1);
        }
    }, { passive: true });

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

    // ── Auto-open from URL hash (e.g. #Daisy-Ridley) ─────────────────
    function openFromHash() {
        var hash = window.location.hash.replace('#', '');
        if (!hash) return;
        var target = decodeURIComponent(hash).replace(/-/g, ' ').toLowerCase();
        for (var i = 0; i < cards.length; i++) {
            var name = (cards[i].querySelector('.person-name') || {}).textContent || '';
            if (name.toLowerCase() === target) {
                cards[i].scrollIntoView({ block: 'center' });
                open(cards[i]);
                break;
            }
        }
    }
    openFromHash();
})();
