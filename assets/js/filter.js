// Resource Card Filters + Sidebar Nav Filters
(function() {
    var cards = document.querySelectorAll('.resource-card[data-filter]');
    var sidebarLinks = document.querySelectorAll('[data-sidebar-filter]');
    var panels = document.querySelectorAll('.filter-panel[data-panel]');
    var homeDefault = document.getElementById('home-default');
    var featuredVideo = document.getElementById('featured-video');
    var pollSection = document.getElementById('poll-section');
    var carouselSection = document.getElementById('carousel-section');
    var ctaSection = document.getElementById('cta-section');
    var statsRow = document.querySelector('.statistics-row');
    if (!panels.length) return;

    var homeSections = [homeDefault, featuredVideo, pollSection, carouselSection, ctaSection, statsRow];
    var activeFilter = null;

    function applyFilter(filter) {
        if (activeFilter === filter) {
            activeFilter = null;
            cards.forEach(function(c) {
                c.classList.remove('card-active');
                c.setAttribute('aria-pressed', 'false');
            });
            sidebarLinks.forEach(function(l) { l.classList.remove('active'); });
            panels.forEach(function(p) { p.style.display = 'none'; });
            homeSections.forEach(function(s) { if (s) s.style.display = ''; });
            sessionStorage.removeItem('activeFilter');
            return;
        }

        activeFilter = filter;

        cards.forEach(function(c) {
            c.classList.remove('card-active');
            c.setAttribute('aria-pressed', 'false');
        });
        var matchingCard = document.querySelector('.resource-card[data-filter="' + filter + '"]');
        if (matchingCard) {
            matchingCard.classList.add('card-active');
            matchingCard.setAttribute('aria-pressed', 'true');
        }

        sidebarLinks.forEach(function(l) { l.classList.remove('active'); });
        var matchingLink = document.querySelector('[data-sidebar-filter="' + filter + '"]');
        if (matchingLink) matchingLink.classList.add('active');

        panels.forEach(function(p) {
            p.style.display = p.getAttribute('data-panel') === filter ? '' : 'none';
        });
        homeSections.forEach(function(s) { if (s) s.style.display = 'none'; });

        var target = document.getElementById('filtered-content');
        var container = document.querySelector('.content.container');
        if (target && container) {
            var headerHeight = document.querySelector('.theme-toggle-wrapper').offsetHeight;
            var targetTop = target.offsetTop - headerHeight - 8;
            container.scrollTo({ top: targetTop, behavior: 'smooth' });
        }

        var sidebar = document.getElementById('sidebar');
        var menuBtn = document.getElementById('mobile-menu-btn');
        var overlay = document.getElementById('mobile-overlay');
        if (sidebar && sidebar.classList.contains('open')) {
            sidebar.classList.remove('open');
            if (menuBtn) { menuBtn.classList.remove('active'); menuBtn.setAttribute('aria-expanded', 'false'); }
            if (overlay) overlay.classList.remove('active');
        }

        sessionStorage.setItem('activeFilter', filter);
    }

    // Restore filter state from sessionStorage
    var saved = sessionStorage.getItem('activeFilter');
    if (saved) {
        var panelExists = document.querySelector('.filter-panel[data-panel="' + saved + '"]');
        if (panelExists) applyFilter(saved);
    }

    cards.forEach(function(card) {
        card.addEventListener('click', function() {
            applyFilter(this.getAttribute('data-filter'));
        });
    });

    sidebarLinks.forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            applyFilter(this.getAttribute('data-sidebar-filter'));
        });
    });
})();
