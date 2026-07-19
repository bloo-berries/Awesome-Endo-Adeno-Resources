// Symptom Tracker - IndexedDB-based, all data on device
(function() {
    var app = document.getElementById('tracker-app');
    if (!app) return;

    var DB_NAME = 'endo-tracker';
    var STORE = 'entries';
    var db = null;

    var SYMPTOMS = [
        'Pelvic Pain', 'Period Pain', 'Back Pain', 'Bloating',
        'Fatigue', 'Nausea', 'Painful Sex', 'Painful Bowel',
        'Heavy Bleeding', 'Irregular Bleeding', 'Headache', 'Mood Changes'
    ];

    var MOODS = ['Great', 'Good', 'Okay', 'Bad', 'Terrible'];

    function openDB(cb) {
        if (db) return cb(db);
        var req = indexedDB.open(DB_NAME, 1);
        req.onupgradeneeded = function(e) {
            var d = e.target.result;
            if (!d.objectStoreNames.contains(STORE)) {
                var store = d.createObjectStore(STORE, { keyPath: 'id', autoIncrement: true });
                store.createIndex('date', 'date', { unique: false });
            }
        };
        req.onsuccess = function(e) { db = e.target.result; cb(db); };
        req.onerror = function() { app.innerHTML = '<p>Unable to open database. Your browser may not support IndexedDB.</p>'; };
    }

    function addEntry(entry, cb) {
        openDB(function(d) {
            var tx = d.transaction(STORE, 'readwrite');
            tx.objectStore(STORE).add(entry);
            tx.oncomplete = cb;
        });
    }

    function deleteEntry(id, cb) {
        openDB(function(d) {
            var tx = d.transaction(STORE, 'readwrite');
            tx.objectStore(STORE).delete(id);
            tx.oncomplete = cb;
        });
    }

    function getAllEntries(cb) {
        openDB(function(d) {
            var tx = d.transaction(STORE, 'readonly');
            var req = tx.objectStore(STORE).index('date').openCursor(null, 'prev');
            var results = [];
            req.onsuccess = function(e) {
                var cursor = e.target.result;
                if (cursor) { results.push(cursor.value); cursor.continue(); }
                else cb(results);
            };
        });
    }

    function render() {
        var today = new Date().toISOString().split('T')[0];

        var html = '<div class="tracker-form">' +
            '<h3>Log Entry</h3>' +
            '<label class="tracker-label">Date<input type="date" id="tracker-date" value="' + today + '" class="tracker-input"></label>' +
            '<label class="tracker-label">Pain Level: <span id="pain-val">5</span>/10' +
            '<input type="range" id="tracker-pain" min="0" max="10" value="5" class="tracker-slider"></label>' +
            '<fieldset class="tracker-fieldset"><legend>Symptoms</legend><div class="tracker-symptom-grid">';

        SYMPTOMS.forEach(function(s) {
            html += '<label class="tracker-check"><input type="checkbox" value="' + s + '"><span>' + s + '</span></label>';
        });

        html += '</div></fieldset>' +
            '<fieldset class="tracker-fieldset"><legend>Mood</legend><div class="tracker-mood-row">';

        MOODS.forEach(function(m) {
            html += '<button type="button" class="tracker-mood-btn" data-mood="' + m + '">' + m + '</button>';
        });

        html += '</div></fieldset>' +
            '<label class="tracker-label">Bleeding<select id="tracker-bleeding" class="tracker-input">' +
            '<option value="">None</option><option value="light">Light</option><option value="moderate">Moderate</option><option value="heavy">Heavy</option></select></label>' +
            '<label class="tracker-label">Medications<input type="text" id="tracker-meds" placeholder="e.g. Ibuprofen, Visanne" class="tracker-input"></label>' +
            '<label class="tracker-label">Notes<textarea id="tracker-notes" rows="2" placeholder="How are you feeling?" class="tracker-input"></textarea></label>' +
            '<button id="tracker-save" class="tracker-save-btn">Save Entry</button>' +
            '</div>' +
            '<div class="tracker-history">' +
            '<h3>Pain Chart (Last 30 Days)</h3>' +
            '<div id="tracker-chart" class="tracker-chart"></div>' +
            '<div class="tracker-actions-row">' +
            '<h3>Past Entries</h3>' +
            '<button id="tracker-export" class="tracker-export-btn">Export CSV</button>' +
            '</div>' +
            '<div id="tracker-entries"></div>' +
            '</div>';

        app.innerHTML = html;

        // Pain slider
        var slider = document.getElementById('tracker-pain');
        var painVal = document.getElementById('pain-val');
        slider.addEventListener('input', function() { painVal.textContent = this.value; });

        // Mood buttons
        var selectedMood = '';
        var moodBtns = app.querySelectorAll('.tracker-mood-btn');
        moodBtns.forEach(function(btn) {
            btn.addEventListener('click', function() {
                moodBtns.forEach(function(b) { b.classList.remove('active'); });
                this.classList.add('active');
                selectedMood = this.getAttribute('data-mood');
            });
        });

        // Save
        document.getElementById('tracker-save').addEventListener('click', function() {
            var symptoms = [];
            app.querySelectorAll('.tracker-symptom-grid input:checked').forEach(function(cb) {
                symptoms.push(cb.value);
            });
            var meds = document.getElementById('tracker-meds').value.trim();
            var entry = {
                date: document.getElementById('tracker-date').value,
                painLevel: parseInt(slider.value),
                symptoms: symptoms,
                mood: selectedMood,
                bleeding: document.getElementById('tracker-bleeding').value,
                medications: meds ? meds.split(',').map(function(m) { return m.trim(); }) : [],
                notes: document.getElementById('tracker-notes').value.trim()
            };
            addEntry(entry, function() {
                loadEntries();
                // Reset form
                app.querySelectorAll('.tracker-symptom-grid input:checked').forEach(function(cb) { cb.checked = false; });
                moodBtns.forEach(function(b) { b.classList.remove('active'); });
                selectedMood = '';
                document.getElementById('tracker-meds').value = '';
                document.getElementById('tracker-notes').value = '';
                document.getElementById('tracker-bleeding').value = '';
                slider.value = 5;
                painVal.textContent = '5';
            });
        });

        // Export
        document.getElementById('tracker-export').addEventListener('click', function() {
            getAllEntries(function(entries) {
                if (!entries.length) return;
                var csv = 'Date,Pain Level,Symptoms,Mood,Bleeding,Medications,Notes\n';
                entries.forEach(function(e) {
                    csv += '"' + e.date + '",' + e.painLevel + ',"' +
                        (e.symptoms || []).join('; ') + '","' +
                        (e.mood || '') + '","' +
                        (e.bleeding || '') + '","' +
                        (e.medications || []).join('; ') + '","' +
                        (e.notes || '').replace(/"/g, '""') + '"\n';
                });
                var blob = new Blob([csv], { type: 'text/csv' });
                var a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'symptom-tracker-' + new Date().toISOString().split('T')[0] + '.csv';
                a.click();
                URL.revokeObjectURL(a.href);
            });
        });

        loadEntries();
    }

    function loadEntries() {
        getAllEntries(function(entries) {
            renderChart(entries);
            renderList(entries);
        });
    }

    function renderChart(entries) {
        var chart = document.getElementById('tracker-chart');
        if (!entries.length) { chart.innerHTML = '<p class="tracker-empty">No data yet. Add your first entry above.</p>'; return; }

        // Last 30 days
        var now = new Date();
        var thirtyAgo = new Date(now);
        thirtyAgo.setDate(thirtyAgo.getDate() - 30);
        var dateStr = thirtyAgo.toISOString().split('T')[0];

        var recent = entries.filter(function(e) { return e.date >= dateStr; });
        if (!recent.length) { chart.innerHTML = '<p class="tracker-empty">No entries in the last 30 days.</p>'; return; }

        // Group by date (take max pain per day)
        var byDate = {};
        recent.forEach(function(e) {
            if (!byDate[e.date] || e.painLevel > byDate[e.date]) byDate[e.date] = e.painLevel;
        });

        var dates = Object.keys(byDate).sort();
        var bars = '';
        dates.forEach(function(d) {
            var pct = (byDate[d] / 10) * 100;
            var label = d.slice(5); // MM-DD
            bars += '<div class="chart-bar-wrap" title="' + d + ': ' + byDate[d] + '/10">' +
                '<div class="chart-bar" style="height:' + pct + '%"></div>' +
                '<span class="chart-label">' + label + '</span></div>';
        });

        chart.innerHTML = '<div class="chart-container">' + bars + '</div>';
    }

    function renderList(entries) {
        var container = document.getElementById('tracker-entries');
        if (!entries.length) { container.innerHTML = '<p class="tracker-empty">No entries yet.</p>'; return; }

        var html = '';
        entries.slice(0, 20).forEach(function(e) {
            html += '<div class="tracker-entry-card">' +
                '<div class="tracker-entry-header">' +
                '<strong>' + e.date + '</strong>' +
                '<span class="tracker-pain-badge">Pain: ' + e.painLevel + '/10</span>' +
                '<button class="tracker-delete-btn" data-id="' + e.id + '" aria-label="Delete entry">&times;</button>' +
                '</div>';
            if (e.mood) html += '<div class="tracker-entry-detail">Mood: ' + e.mood + '</div>';
            if (e.symptoms && e.symptoms.length) html += '<div class="tracker-entry-detail">Symptoms: ' + e.symptoms.join(', ') + '</div>';
            if (e.bleeding) html += '<div class="tracker-entry-detail">Bleeding: ' + e.bleeding + '</div>';
            if (e.medications && e.medications.length) html += '<div class="tracker-entry-detail">Meds: ' + e.medications.join(', ') + '</div>';
            if (e.notes) html += '<div class="tracker-entry-detail tracker-entry-notes">' + e.notes + '</div>';
            html += '</div>';
        });

        container.innerHTML = html;

        // Delete handlers
        container.querySelectorAll('.tracker-delete-btn').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var id = parseInt(this.getAttribute('data-id'));
                deleteEntry(id, loadEntries);
            });
        });
    }

    render();
})();
