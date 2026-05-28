// i18n Translation System
(function() {
    var translations = null;
    var currentLang = localStorage.getItem('site-language') || 'en';

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
        // Sync picker
        var picker = document.getElementById('lang-picker');
        if (picker) picker.value = lang;
        currentLang = lang;
        localStorage.setItem('site-language', lang);
    }

    fetch(window.__translationsURL || '/i18n/translations.json')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            translations = data;
            // Expose to other modules (e.g., search.js) for runtime lookups
            window.__i18nTranslations = data;
            applyTranslations(currentLang);
            var picker = document.getElementById('lang-picker');
            if (picker) {
                picker.value = currentLang;
                picker.addEventListener('change', function() {
                    applyTranslations(this.value);
                });
            }
        });
})();
