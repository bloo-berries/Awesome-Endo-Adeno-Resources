// Client-side Search (Phase 4b: empty-state suggestions + keyboard nav)
//
// Behavior:
//   - Focus an empty input -> show 6 suggested queries (from i18n keys
//     search_suggestion_1..6, falling back to defaults).
//   - Type 2+ chars -> debounced search (200ms) with synonym expansion and
//     weighted scoring (title 10, tags 5, summary 3, content 1).
//   - Up/Down arrows move focus across results.
//   - Enter on a focused result navigates.
//   - Esc clears input and closes the results panel.
//   - Click outside closes the panel.
(function() {
    var searchInput = document.getElementById('search-input');
    var resultsContainer = document.getElementById('search-results');
    if (!searchInput || !resultsContainer) return;

    var searchIndex = null;

    var defaultSuggestions = [
        'endo symptoms',
        'find a specialist',
        'adenomyosis vs endometriosis',
        'pelvic pain',
        'fertility',
        'what is adeno'
    ];

    function getSuggestion(i) {
        var fallback = defaultSuggestions[i - 1] || '';
        // i18n.js may have replaced placeholders; we resolve via the same key store
        // it uses, but as a no-build-time-coupling fallback we attempt to read from
        // a global cache i18n exposes, otherwise the default suggestion is used.
        try {
            if (window.__i18nTranslations) {
                var lang = localStorage.getItem('site-language') || 'en';
                var t = window.__i18nTranslations[lang] || window.__i18nTranslations.en || {};
                return t['search_suggestion_' + i] || fallback;
            }
        } catch (e) {}
        return fallback;
    }

    function loadIndex() {
        if (searchIndex !== null) return Promise.resolve(searchIndex);
        return fetch(window.__searchIndexURL || '/index.json')
            .then(function(r) { return r.json(); })
            .then(function(data) { searchIndex = data; return data; });
    }

    var synonyms = [
        ['period pain', 'dysmenorrhea', 'menstrual cramps', 'cramps'],
        ['endo', 'endometriosis'],
        ['adeno', 'adenomyosis'],
        ['painful sex', 'dyspareunia', 'painful intercourse'],
        ['heavy periods', 'menorrhagia', 'heavy bleeding', 'heavy menstrual bleeding'],
        ['bloating', 'endo belly', 'abdominal bloating'],
        ['cyst', 'endometrioma', 'chocolate cyst'],
        ['infertility', 'fertility', 'difficulty getting pregnant', 'subfertility'],
        ['fatigue', 'exhaustion', 'chronic fatigue'],
        ['bowel', 'rectal', 'intestinal', 'bowel endometriosis'],
        ['pelvic pain', 'chronic pelvic pain', 'cpp'],
        ['excision', 'laparoscopy', 'surgery', 'surgical'],
        ['hormone', 'hormonal', 'birth control', 'contraceptive'],
        ['diagnosis', 'diagnostic', 'diagnosed'],
        ['specialist', 'doctor', 'gynecologist', 'gynaecologist'],
        ['mental health', 'depression', 'anxiety', 'therapy'],
        ['medication', 'drug', 'medicine', 'treatment'],
        ['faq', 'frequently asked', 'questions'],
        ['tracker', 'tracking', 'symptom diary', 'symptom log']
    ];

    function expandQuery(query) {
        var q = query.toLowerCase();
        var terms = [q];
        synonyms.forEach(function(group) {
            var match = group.some(function(s) { return q.indexOf(s) !== -1; });
            if (match) {
                group.forEach(function(s) {
                    if (terms.indexOf(s) === -1) terms.push(s);
                });
            }
        });
        return terms;
    }

    function renderSuggestions() {
        var items = [1, 2, 3, 4, 5, 6].map(function(i) {
            var s = getSuggestion(i);
            return '<button type="button" class="search-suggestion" data-query="' +
                   s.replace(/"/g, '&quot;') + '">' +
                   '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>' +
                   '<span>' + s + '</span></button>';
        }).join('');
        resultsContainer.innerHTML =
            '<div class="search-suggestions-header" data-i18n="search_suggestions_header">Try searching for…</div>' +
            '<div class="search-suggestions">' + items + '</div>';
        resultsContainer.setAttribute('data-state', 'suggestions');
    }

    function search(query) {
        if (!searchIndex || !query) { closeResults(); return; }
        var terms = expandQuery(query);

        var scored = [];
        searchIndex.forEach(function(page) {
            var score = 0;
            var titleLower = (page.title || '').toLowerCase();
            var summaryLower = (page.summary || '').toLowerCase();
            var contentLower = (page.content || '').toLowerCase();
            var tagsLower = (page.tags || []).map(function(t) { return t.toLowerCase(); });

            terms.forEach(function(term) {
                if (titleLower.indexOf(term) !== -1) score += 10;
                tagsLower.forEach(function(tag) { if (tag.indexOf(term) !== -1) score += 5; });
                if (summaryLower.indexOf(term) !== -1) score += 3;
                if (contentLower.indexOf(term) !== -1) score += 1;
            });

            if (score > 0) scored.push({ page: page, score: score });
        });

        scored.sort(function(a, b) { return b.score - a.score; });
        var results = scored.slice(0, 8);

        if (results.length === 0) {
            resultsContainer.innerHTML = '<div class="search-no-results" data-i18n="no_results">No results found</div>';
            resultsContainer.setAttribute('data-state', 'no-results');
            return;
        }

        resultsContainer.innerHTML = results.map(function(r) {
            var summary = r.page.summary || '';
            if (summary.length > 120) summary = summary.substring(0, 120) + '...';
            var summaryHtml = summary ? '<span class="search-result-summary">' + summary + '</span>' : '';
            return '<a class="search-result-item" role="option" href="' + r.page.permalink + '">' +
                   '<span class="search-result-title">' + r.page.title + '</span>' +
                   summaryHtml +
                   '</a>';
        }).join('');
        resultsContainer.setAttribute('data-state', 'results');
    }

    function closeResults() {
        resultsContainer.innerHTML = '';
        resultsContainer.removeAttribute('data-state');
    }

    function selectableItems() {
        return Array.prototype.slice.call(
            resultsContainer.querySelectorAll('.search-result-item, .search-suggestion')
        );
    }

    function moveFocus(dir) {
        var items = selectableItems();
        if (!items.length) return;
        var current = document.activeElement;
        var idx = items.indexOf(current);
        if (idx === -1) {
            // Coming from the input
            idx = dir > 0 ? 0 : items.length - 1;
        } else {
            idx = (idx + dir + items.length) % items.length;
        }
        items[idx].focus();
    }

    // Show suggestions when input is focused (empty)
    searchInput.addEventListener('focus', function() {
        if (this.value.trim() === '') renderSuggestions();
    });

    var debounceTimer;
    searchInput.addEventListener('input', function() {
        var q = this.value.trim();
        clearTimeout(debounceTimer);
        if (q.length === 0) { renderSuggestions(); return; }
        if (q.length < 2) { closeResults(); return; }
        debounceTimer = setTimeout(function() {
            loadIndex().then(function() { search(q); });
        }, 200);
    });

    // Keyboard nav on the input
    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            closeResults();
            this.blur();
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            moveFocus(1);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            moveFocus(-1);
        }
    });

    // Keyboard nav inside the results panel
    resultsContainer.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowDown') { e.preventDefault(); moveFocus(1); }
        else if (e.key === 'ArrowUp') { e.preventDefault(); moveFocus(-1); }
        else if (e.key === 'Escape') {
            closeResults();
            searchInput.focus();
        } else if (e.key === 'Enter' && e.target.classList.contains('search-suggestion')) {
            e.preventDefault();
            var q = e.target.getAttribute('data-query');
            searchInput.value = q;
            loadIndex().then(function() { search(q); });
        }
    });

    // Click handler for suggestions (runs the query)
    resultsContainer.addEventListener('click', function(e) {
        var btn = e.target.closest('.search-suggestion');
        if (!btn) return;
        var q = btn.getAttribute('data-query');
        searchInput.value = q;
        searchInput.focus();
        loadIndex().then(function() { search(q); });
    });

    // Close when clicking outside the search region
    document.addEventListener('click', function(e) {
        if (!e.target.closest('#search-input') &&
            !e.target.closest('#search-results') &&
            !e.target.closest('.topbar-search')) {
            closeResults();
        }
    });
})();
