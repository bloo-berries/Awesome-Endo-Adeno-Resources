// i18n Translation System - URL-based routing
(function() {
    var translations = null;
    var pageLang = window.__pageLang || 'en';
    var contentBase = window.__contentBase || '/';
    var baseURL = window.__baseURL || '/';

    // Set localStorage to match this page's language (so redirect script works)
    localStorage.setItem('site-language', pageLang);

    function applyTranslations(lang) {
        if (!translations || !translations[lang]) return;
        var t = translations[lang];
        var fallback = translations.en || {};
        document.querySelectorAll('[data-i18n]').forEach(function(el) {
            var key = el.getAttribute('data-i18n');
            var value = t[key] || fallback[key];
            if (!value) return;
            var attrs = el.getAttribute('data-i18n-attr');
            if (attrs) {
                attrs.split(',').forEach(function(attr) {
                    el.setAttribute(attr.trim(), value);
                });
            } else {
                el.textContent = value;
            }
            // Handle separate aria-label key
            var ariaKey = el.getAttribute('data-i18n-aria');
            if (ariaKey) {
                var ariaValue = t[ariaKey] || fallback[ariaKey];
                if (ariaValue) el.setAttribute('aria-label', ariaValue);
            }
        });
        // Update no-results text if visible
        var noResults = document.querySelector('.search-no-results');
        if (noResults && t.no_results) noResults.textContent = t.no_results;
        // Handle RTL for Arabic
        document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
    }

    function navigateToLang(newLang) {
        localStorage.setItem('site-language', newLang);
        var basePath = baseURL.replace(/^https?:\/\/[^\/]+/, '') || '/';
        var path = location.pathname;
        // Strip current lang prefix if present
        var afterBase = path.replace(basePath, '');
        var langMatch = afterBase.match(/^([a-z]{2})\//);
        if (langMatch) {
            afterBase = afterBase.replace(/^[a-z]{2}\//, '');
        }
        // Build new path
        var newPath;
        if (newLang === 'en') {
            newPath = basePath + afterBase;
        } else {
            newPath = basePath + newLang + '/' + afterBase;
        }
        // Ensure trailing slash
        if (newPath !== '/' && !newPath.endsWith('/')) newPath += '/';
        location.href = newPath;
    }

    function syncPickers(lang) {
        var topbar = document.getElementById('lang-picker');
        var sidebar = document.getElementById('sidebar-lang-picker');
        if (topbar) topbar.value = lang;
        if (sidebar) sidebar.value = lang;
    }

    function onPickerChange(e) {
        var newLang = e.target.value;
        if (newLang === pageLang) return;
        navigateToLang(newLang);
    }

    // Sync both pickers and attach handlers
    syncPickers(pageLang);
    var topbar = document.getElementById('lang-picker');
    var sidebar = document.getElementById('sidebar-lang-picker');
    if (topbar) topbar.addEventListener('change', onPickerChange);
    if (sidebar) sidebar.addEventListener('change', onPickerChange);

    fetch(window.__translationsURL || '/i18n/translations.json')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            translations = data;
            // Expose to other modules (e.g., search.js) for runtime lookups
            window.__i18nTranslations = data;
            applyTranslations(pageLang);
            syncPickers(pageLang);
            document.dispatchEvent(new Event('i18n:ready'));
        })
        .catch(function(err) { console.warn('i18n: failed to load translations', err); });

    // Shared i18n lookup helper for other modules
    window.__ti18n = function(key, fallback) {
        var t = (window.__i18nTranslations || {})[pageLang] || (window.__i18nTranslations || {}).en || {};
        return t[key] || fallback;
    };
})();
