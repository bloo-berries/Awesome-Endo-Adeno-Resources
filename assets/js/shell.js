// shell.js - Page shell behaviors (extracted from base.html inline scripts)
// Sidebar open/close, theme toggle, language picker sync, back-to-top, bottom nav, people carousel arrows.

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

// Sync sidebar lang picker with topbar lang picker
(function() {
    var topbar = document.getElementById('lang-picker');
    var sidebar = document.getElementById('sidebar-lang-picker');
    if (!topbar || !sidebar) return;
    sidebar.value = topbar.value;
    topbar.addEventListener('change', function() { sidebar.value = topbar.value; });
    sidebar.addEventListener('change', function() {
        topbar.value = sidebar.value;
        topbar.dispatchEvent(new Event('change'));
    });
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
