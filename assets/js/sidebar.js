// Sidebar collapsible groups (Phase 4a)
// Each .nav-group has a .nav-group-toggle button that collapses the group's <ul>.
// State persisted to localStorage as a comma-separated list of collapsed group IDs.
// Privacy: localStorage key 'sidebar-groups' is documented in /privacy/.
(function() {
    var STORAGE_KEY = 'sidebar-groups';
    var groups = document.querySelectorAll('.sidebar-nav .nav-group');
    if (!groups.length) return;

    function loadCollapsed() {
        try {
            var raw = localStorage.getItem(STORAGE_KEY);
            return raw ? raw.split(',').filter(Boolean) : [];
        } catch (e) {
            return [];
        }
    }

    function saveCollapsed(ids) {
        try { localStorage.setItem(STORAGE_KEY, ids.join(',')); } catch (e) {}
    }

    function setCollapsed(group, collapsed) {
        var toggle = group.querySelector('.nav-group-toggle');
        if (!toggle) return;
        group.setAttribute('data-collapsed', collapsed ? 'true' : 'false');
        toggle.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
    }

    // Apply persisted state on load; collapse groups 1 & 2 by default
    var DEFAULT_COLLAPSED = ['nav-group-1', 'nav-group-2'];
    var hasStored = false;
    try { hasStored = localStorage.getItem(STORAGE_KEY) !== null; } catch (e) {}
    var collapsed = hasStored ? loadCollapsed() : DEFAULT_COLLAPSED;
    groups.forEach(function(group) {
        var id = group.getAttribute('data-group-id');
        if (id && collapsed.indexOf(id) !== -1) setCollapsed(group, true);
    });

    // Wire toggle clicks
    groups.forEach(function(group) {
        var toggle = group.querySelector('.nav-group-toggle');
        if (!toggle) return;
        toggle.addEventListener('click', function() {
            var id = group.getAttribute('data-group-id');
            var isCollapsed = group.getAttribute('data-collapsed') === 'true';
            setCollapsed(group, !isCollapsed);

            // Update storage
            var current = loadCollapsed().filter(function(x) { return x !== id; });
            if (!isCollapsed && id) current.push(id);
            saveCollapsed(current);
        });
    });
})();
