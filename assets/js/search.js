// Client-side Search
(function() {
    var searchInput = document.getElementById('search-input');
    var resultsContainer = document.getElementById('search-results');
    if (!searchInput || !resultsContainer) return;

    var searchIndex = null;

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

    function search(query) {
        if (!searchIndex || !query) { resultsContainer.innerHTML = ''; return; }
        var terms = expandQuery(query);

        // Weighted scoring
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
            resultsContainer.innerHTML = '<div class="search-no-results">No results found</div>';
            return;
        }

        resultsContainer.innerHTML = results.map(function(r) {
            var summary = r.page.summary || '';
            if (summary.length > 120) summary = summary.substring(0, 120) + '...';
            var summaryHtml = summary ? '<span class="search-result-summary">' + summary + '</span>' : '';
            return '<a class="search-result-item" href="' + r.page.permalink + '">' +
                   '<span class="search-result-title">' + r.page.title + '</span>' +
                   summaryHtml +
                   '</a>';
        }).join('');
    }

    var debounceTimer;
    searchInput.addEventListener('input', function() {
        var q = this.value.trim();
        clearTimeout(debounceTimer);
        if (q.length < 2) { resultsContainer.innerHTML = ''; return; }
        debounceTimer = setTimeout(function() {
            loadIndex().then(function() { search(q); });
        }, 200);
    });

    searchInput.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            this.value = '';
            resultsContainer.innerHTML = '';
        }
    });

    document.addEventListener('click', function(e) {
        if (!e.target.closest('.sidebar-search')) {
            resultsContainer.innerHTML = '';
        }
    });
})();
