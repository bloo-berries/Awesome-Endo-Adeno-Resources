// Symptom Poll
(function() {
    var pollForm = document.getElementById('poll-form');
    var pollOptions = document.querySelectorAll('.poll-option input[type="checkbox"]');
    var pollSubmit = document.getElementById('poll-submit');
    var pollThanks = document.getElementById('poll-thanks');
    if (!pollSubmit) return;

    pollSubmit.addEventListener('click', async function() {
        var selected = [];
        pollOptions.forEach(function(opt) { if (opt.checked) selected.push(opt.value); });
        if (selected.length === 0) {
            var pollError = document.getElementById('poll-error');
            if (pollError) { pollError.style.display = 'block'; setTimeout(function() { pollError.style.display = 'none'; }, 3000); }
            return;
        }
        pollSubmit.disabled = true;
        pollSubmit.textContent = '...';
        try {
            await fetch('https://formspree.io/f/xdalyrze', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify({ poll_responses: selected.join(', '), source: 'awesome-endo-adeno' })
            });
        } catch (e) { console.error('Poll error:', e); }
        if (pollForm) pollForm.style.display = 'none';
        if (pollThanks) pollThanks.style.display = 'block';
        var suggestions = document.getElementById('poll-suggestions');
        if (suggestions) suggestions.style.display = 'block';
    });
})();
