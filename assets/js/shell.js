// shell.js - Page shell behaviors (extracted from base.html inline scripts)
// Sidebar open/close, theme toggle, language picker sync, back-to-top, bottom nav, people carousel arrows.

// Shared SVG icons (consumed by accordion.js, search.js, take-action.js, person-modal.js, quiz.js)
window.appIcons = {
    chevron: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>',
    check: '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" focusable="false"><polyline points="20 6 9 17 4 12"></polyline></svg>',
    refresh: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" focusable="false"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>',
    search: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>',
    copy: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
    close: '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>'
};

// Sidebar open/close
(function() {
    var menuBtn = document.getElementById('topbar-menu');
    var sidebar = document.getElementById('sidebar');
    var backdrop = document.getElementById('sidebar-backdrop');
    if (!menuBtn || !sidebar) return;

    function setOpen(open) {
        sidebar.setAttribute('data-open', open ? 'true' : 'false');
        if (backdrop) backdrop.setAttribute('data-open', open ? 'true' : 'false');
        menuBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
        document.body.style.overflow = open ? 'hidden' : '';
        if (open) {
            var firstLink = sidebar.querySelector('a, button');
            if (firstLink) firstLink.focus();
        }
    }

    menuBtn.addEventListener('click', function() {
        var isOpen = sidebar.getAttribute('data-open') === 'true';
        setOpen(!isOpen);
    });

    if (backdrop) backdrop.addEventListener('click', function() { setOpen(false); });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.getAttribute('data-open') === 'true') {
            setOpen(false);
            menuBtn.focus();
        }
    });

    var desktopMQ = window.matchMedia('(min-width: 64rem)');
    desktopMQ.addEventListener('change', function() {
        setOpen(false);
    });
})();

// Theme toggle
(function() {
    function toggle() {
        document.body.classList.toggle('dark-theme');
        var isDark = document.body.classList.contains('dark-theme');
        localStorage.setItem('theme', isDark ? 'dark' : 'light');
    }
    var btn1 = document.getElementById('toggle-theme-btn');
    var btn2 = document.getElementById('sidebar-toggle-theme');
    if (btn1) btn1.addEventListener('click', toggle);
    if (btn2) btn2.addEventListener('click', toggle);
})();

// Back-to-top
(function() {
    var btn = document.getElementById('back-to-top');
    if (!btn) return;
    function onScroll() {
        var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        btn.classList.toggle('visible', scrollTop > window.innerHeight * 0.75);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    btn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
})();

// Mark current page in bottom nav
(function() {
    var path = window.location.pathname.replace(/\/$/, '');
    document.querySelectorAll('.bottomnav-item').forEach(function(a) {
        var href = a.getAttribute('href').replace(/\/$/, '');
        var hrefPath;
        try { hrefPath = new URL(href, window.location.href).pathname.replace(/\/$/, ''); }
        catch (e) { hrefPath = href; }
        if (path === hrefPath) a.setAttribute('aria-current', 'page');
    });
})();

// Settings panel toggle
(function() {
    var btn = document.getElementById('settings-toggle');
    var panel = document.getElementById('settings-panel');
    if (!btn || !panel) return;

    function setOpen(open) {
        if (open) {
            panel.removeAttribute('hidden');
        } else {
            panel.setAttribute('hidden', '');
        }
        btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    }

    btn.addEventListener('click', function(e) {
        e.stopPropagation();
        var isOpen = !panel.hasAttribute('hidden');
        setOpen(!isOpen);
    });

    document.addEventListener('click', function(e) {
        if (!panel.hasAttribute('hidden') && !panel.contains(e.target) && e.target !== btn) {
            setOpen(false);
        }
    });

    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && !panel.hasAttribute('hidden')) {
            setOpen(false);
            btn.focus();
        }
    });
})();

// Notable People carousel scroll arrows
(function() {
    var track = document.querySelector('.home-people-track');
    if (!track) return;
    var prev = document.querySelector('.home-people-prev');
    var next = document.querySelector('.home-people-next');
    if (!prev || !next) return;
    var scrollAmt = function() { return track.clientWidth * 0.7; };
    prev.addEventListener('click', function() { track.scrollBy({ left: -scrollAmt(), behavior: 'smooth' }); });
    next.addEventListener('click', function() { track.scrollBy({ left: scrollAmt(), behavior: 'smooth' }); });
})();

// Shared clipboard utility (explicit export for codeblock.js and take-action.js)
function copyText(text) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
        return navigator.clipboard.writeText(text);
    }
    return new Promise(function(resolve, reject) {
        try {
            var ta = document.createElement('textarea');
            ta.value = text;
            ta.style.position = 'fixed';
            ta.style.opacity = '0';
            document.body.appendChild(ta);
            ta.select();
            document.execCommand('copy');
            document.body.removeChild(ta);
            resolve();
        } catch (e) { reject(e); }
    });
}
window.appUtils = { copyText: copyText };
