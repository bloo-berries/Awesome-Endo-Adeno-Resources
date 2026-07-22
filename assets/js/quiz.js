// Symptom Quiz - client-side only, no data stored or transmitted
(function() {
    var app = document.getElementById('quiz-app');
    if (!app) return;

    // i18n helper
    function t(key, fallback) {
        return window.__ti18n ? window.__ti18n(key, fallback) : fallback;
    }

    var SYMPTOMS_EN = [
        'Severe period pain that doesn\u2019t respond to over-the-counter medication',
        'Heavy or irregular periods, sometimes with clotting',
        'Pelvic pain between periods or during sex',
        'Painful bowel movements or urination, especially around your period',
        'Persistent fatigue that isn\u2019t explained by sleep or workload',
        'Bloating (\u2018endo belly\u2019) that comes and goes',
        'Difficulty getting pregnant after trying for 12+ months',
        'Sciatica-like pain down one or both legs',
        'Lower back pain that worsens with your cycle'
    ];

    function getSymptoms() {
        return SYMPTOMS_EN.map(function(fallback, i) {
            return t('quiz_symptom_' + i, fallback);
        });
    }

    function render() {
        var symptoms = getSymptoms();
        var html = '<div class="quiz-progress-wrap">' +
            '<div class="quiz-progress-bar"><div class="quiz-progress-fill" style="width:0%"></div></div>' +
            '<p class="quiz-counter" aria-live="polite"><span class="quiz-counter-num">0</span> ' + t('quiz_counter_suffix', 'of 9 selected') + '</p>' +
            '</div>';

        html += '<div class="quiz-cards">';
        symptoms.forEach(function(s, i) {
            var id = 'symptom-' + i;
            html += '<label class="quiz-card" for="' + id + '">' +
                '<input type="checkbox" id="' + id + '" value="' + i + '">' +
                '<span class="quiz-card-text">' + s + '</span>' +
                '<span class="quiz-card-check" aria-hidden="true">' +
                '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" focusable="false"><polyline points="20 6 9 17 4 12"></polyline></svg>' +
                '</span></label>';
        });
        html += '</div>';

        html += '<div class="quiz-results" aria-live="polite"></div>' +
            '<button type="button" class="quiz-reset" style="display:none">' +
            '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" focusable="false"><polyline points="1 4 1 10 7 10"></polyline><path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"></path></svg>' +
            ' ' + t('quiz_reset', 'Start over') + '</button>';

        app.innerHTML = html;

        var cards = app.querySelectorAll('.quiz-card');
        var counter = app.querySelector('.quiz-counter-num');
        var progressFill = app.querySelector('.quiz-progress-fill');
        var results = app.querySelector('.quiz-results');
        var resetBtn = app.querySelector('.quiz-reset');

        function update() {
            var count = app.querySelectorAll('.quiz-cards input:checked').length;
            counter.textContent = count;
            progressFill.style.width = Math.round((count / 9) * 100) + '%';

            cards.forEach(function(card) {
                var cb = card.querySelector('input');
                card.classList.toggle('checked', cb.checked);
            });

            if (count === 0) {
                results.innerHTML = '';
                results.classList.remove('has-content');
                resetBtn.style.display = 'none';
            } else if (count < 3) {
                results.innerHTML = '<div class="quiz-results-inner quiz-results-mild">' +
                    '<p class="quiz-results-heading">' + t('quiz_result_mild_heading', 'Worth mentioning to your doctor') + '</p>' +
                    '<p>' + t('quiz_result_mild_body', 'If these symptoms affect your quality of life, it\u2019s worth discussing them at your next appointment.') + '</p></div>';
                results.classList.add('has-content');
                resetBtn.style.display = '';
            } else {
                results.innerHTML = '<div class="quiz-results-inner quiz-results-match">' +
                    '<p class="quiz-results-heading">' + t('quiz_result_match_heading', 'This pattern is consistent with Endo or Adeno') + '</p>' +
                    '<p>' + t('quiz_result_match_body', 'Selecting ' + count + ' symptoms suggests a pattern worth investigating. Here are your recommended next steps:') + '</p>' +
                    '<div class="quiz-next-steps">' +
                    '<a href="diagnosis/" class="quiz-step-link"><span class="quiz-step-num">1</span><span class="quiz-step-text">' + t('quiz_step_diagnosis', 'Learn about diagnosis') + '</span></a>' +
                    '<a href="healthcare/" class="quiz-step-link"><span class="quiz-step-num">2</span><span class="quiz-step-text">' + t('quiz_step_specialist', 'Find a specialist') + '</span></a>' +
                    '<a href="tracker/" class="quiz-step-link"><span class="quiz-step-num">3</span><span class="quiz-step-text">' + t('quiz_step_tracker', 'Track your symptoms') + '</span></a>' +
                    '</div></div>';
                results.classList.add('has-content');
                resetBtn.style.display = '';
            }
        }

        cards.forEach(function(card) {
            card.addEventListener('change', update);
        });

        resetBtn.addEventListener('click', function() {
            app.querySelectorAll('.quiz-cards input:checked').forEach(function(cb) {
                cb.checked = false;
            });
            cards.forEach(function(card) { card.classList.remove('checked'); });
            update();
        });
    }

    render();

    // Re-render once translations are loaded (they arrive async from i18n.js)
    document.addEventListener('i18n:ready', function() { render(); });
})();
