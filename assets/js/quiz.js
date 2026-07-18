// Symptom Quiz — client-side only, no data stored or transmitted
(function() {
    var app = document.getElementById('quiz-app');
    if (!app) return;

    var SYMPTOMS = [
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

    function render() {
        var html = '<div class="quiz-cards">';
        SYMPTOMS.forEach(function(s, i) {
            var id = 'symptom-' + i;
            html += '<label class="quiz-card" for="' + id + '">' +
                '<input type="checkbox" id="' + id + '" value="' + i + '">' +
                '<span>' + s + '</span></label>';
        });
        html += '</div>' +
            '<p class="quiz-counter" aria-live="polite">0 of 9 symptoms selected</p>' +
            '<div class="quiz-results" aria-live="polite"></div>' +
            '<button type="button" class="quiz-reset" style="display:none">Reset</button>';

        app.innerHTML = html;

        var cards = app.querySelectorAll('.quiz-card');
        var counter = app.querySelector('.quiz-counter');
        var results = app.querySelector('.quiz-results');
        var resetBtn = app.querySelector('.quiz-reset');

        function update() {
            var count = app.querySelectorAll('.quiz-cards input:checked').length;
            counter.textContent = count + ' of 9 symptoms selected';

            cards.forEach(function(card) {
                var cb = card.querySelector('input');
                card.classList.toggle('checked', cb.checked);
            });

            if (count === 0) {
                results.innerHTML = '';
                resetBtn.style.display = 'none';
            } else if (count < 3) {
                results.innerHTML = '<p>If these symptoms affect your quality of life, ' +
                    'it\u2019s worth discussing them with a doctor.</p>';
                resetBtn.style.display = '';
            } else {
                results.innerHTML = '<p>This pattern is consistent with Endometriosis or ' +
                    'Adenomyosis. Here are your next steps:</p><ul>' +
                    '<li><a href="diagnosis/">Getting a diagnosis</a></li>' +
                    '<li><a href="healthcare/">Finding the right doctor</a></li>' +
                    '<li><a href="tracker/">Track your symptoms</a></li></ul>';
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
})();
