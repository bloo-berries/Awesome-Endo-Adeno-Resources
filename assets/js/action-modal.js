// Action Modal
(function() {
    var modal = document.getElementById('action-modal');
    if (!modal) return;

    function openModal() {
        modal.style.display = 'flex';
        setTimeout(function() { modal.classList.add('active'); }, 10);
        document.body.style.overflow = 'hidden';
        var first = modal.querySelector('button, [tabindex]:not([tabindex="-1"])');
        if (first) first.focus();
    }

    function closeModal() {
        modal.classList.remove('active');
        setTimeout(function() { modal.style.display = 'none'; document.body.style.overflow = ''; }, 300);
    }

    function showView(viewId) {
        modal.querySelectorAll('.modal-content').forEach(function(v) { v.style.display = 'none'; });
        var target = document.getElementById(viewId);
        if (target) { target.style.display = 'block'; target.scrollTop = 0; }
    }

    // CTA buttons
    ['cta-take-action', 'poll-take-action'].forEach(function(id) {
        var btn = document.getElementById(id);
        if (btn) btn.addEventListener('click', openModal);
    });

    // Close
    var closeBtn = document.getElementById('modal-close');
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', function(e) { if (e.target === modal) closeModal(); });

    // Action cards
    modal.querySelectorAll('.action-card').forEach(function(card) {
        card.addEventListener('click', function() {
            var action = this.getAttribute('data-action');
            if (action) showView(action + '-view');
        });
    });

    // Back buttons
    modal.querySelectorAll('.back-button').forEach(function(btn) {
        btn.addEventListener('click', function() { showView('main-cards-view'); });
    });

    // Symptom card expand/collapse
    var symptomCards = modal.querySelectorAll('.symptom-card');
    symptomCards.forEach(function(card, index) {
        var header = card.querySelector('.symptom-header');
        if (!header) return;
        header.addEventListener('click', function() {
            var grid = card.closest('.symptoms-grid');
            var cols = getComputedStyle(grid).gridTemplateColumns.split(' ').length;
            var rowStart = Math.floor(index / cols) * cols;
            var isExpanding = !card.classList.contains('expanded');
            for (var i = rowStart; i < rowStart + cols && i < symptomCards.length; i++) {
                symptomCards[i].classList.toggle('expanded', isExpanding);
                var h = symptomCards[i].querySelector('.symptom-header');
                if (h) h.setAttribute('aria-expanded', isExpanding);
            }
        });
    });

    // Symptom checklist counter
    var symptomCheckboxes = modal.querySelectorAll('.symptoms-checklist input[type="checkbox"]');
    var symptomCount = document.getElementById('symptom-count');
    function updateCount() {
        var checked = modal.querySelectorAll('.symptoms-checklist input[type="checkbox"]:checked').length;
        if (symptomCount) symptomCount.textContent = checked;
        var checkedSymptoms = Array.from(symptomCheckboxes).filter(function(cb) { return cb.checked; }).map(function(cb) { return cb.getAttribute('data-symptom'); });
        sessionStorage.setItem('endo-symptoms', JSON.stringify(checkedSymptoms));
    }
    symptomCheckboxes.forEach(function(cb) { cb.addEventListener('change', updateCount); });
    var saved = sessionStorage.getItem('endo-symptoms');
    if (saved) { try { JSON.parse(saved).forEach(function(s) { var cb = modal.querySelector('input[data-symptom="' + s + '"]'); if (cb) cb.checked = true; }); updateCount(); } catch(e) {} }

    // Find Specialist / Doctor Questions toggles
    var findBtn = document.getElementById('find-specialist-btn');
    var doctorBtn = document.getElementById('doctor-questions-btn');
    var specRes = document.getElementById('specialist-resources');
    var docQ = document.getElementById('doctor-questions');
    if (findBtn && specRes) {
        findBtn.addEventListener('click', function() {
            if (specRes.style.display === 'none' || specRes.style.display === '') {
                specRes.style.display = 'block'; if (docQ) docQ.style.display = 'none';
                this.textContent = 'Hide Specialist Resources';
                if (doctorBtn) doctorBtn.textContent = doctorBtn.getAttribute('data-i18n-original') || 'Prepare for Your Doctor Visit';
            } else { specRes.style.display = 'none'; this.textContent = 'Find a Specialist Near You'; }
        });
    }
    if (doctorBtn && docQ) {
        doctorBtn.addEventListener('click', function() {
            if (docQ.style.display === 'none' || docQ.style.display === '') {
                docQ.style.display = 'block'; if (specRes) specRes.style.display = 'none';
                this.textContent = 'Hide Doctor Questions';
                if (findBtn) findBtn.textContent = findBtn.getAttribute('data-i18n-original') || 'Find a Specialist Near You';
            } else { docQ.style.display = 'none'; this.textContent = 'Prepare for Your Doctor Visit'; }
        });
    }

    // Copy text with CSS class toggles
    modal.querySelectorAll('.copy-btn').forEach(function(btn) {
        btn.addEventListener('click', async function() {
            var p = this.parentElement.querySelector('p');
            if (!p) return;
            var original = btn.textContent;
            try {
                await navigator.clipboard.writeText(p.textContent);
                btn.textContent = 'Copied!';
                btn.classList.add('copy-success-state');
            } catch(e) {
                btn.textContent = 'Select & copy manually';
                btn.classList.add('copy-error-state');
                var range = document.createRange(); range.selectNodeContents(p);
                var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(range);
            }
            setTimeout(function() {
                btn.textContent = original;
                btn.classList.remove('copy-success-state', 'copy-error-state');
            }, 2000);
        });
    });

    // Escape key
    document.addEventListener('keydown', function(e) {
        if (modal.classList.contains('active') && e.key === 'Escape') closeModal();
    });
})();
