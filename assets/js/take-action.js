// /take-action/ - add copy buttons to template blockquotes (Phase 4c)
// Activates only on the take-action page. Each blockquote inside .content gets
// a Copy button that writes its plain text to the clipboard.
(function() {
    if (!/\/take-action\/?$/.test(window.location.pathname)) return;

    var content = document.getElementById('main-content') || document.querySelector('.content');
    if (!content) return;

    var blockquotes = content.querySelectorAll('blockquote');
    if (!blockquotes.length) return;

    function getCopyLabel() {
        try {
            var lang = localStorage.getItem('site-language') || 'en';
            var t = (window.__i18nTranslations || {})[lang] || (window.__i18nTranslations || {}).en || {};
            return t.copy_template || 'Copy';
        } catch (e) {
            return 'Copy';
        }
    }

    function getCopiedLabel() {
        try {
            var lang = localStorage.getItem('site-language') || 'en';
            var t = (window.__i18nTranslations || {})[lang] || (window.__i18nTranslations || {}).en || {};
            return t.copied || 'Copied';
        } catch (e) {
            return 'Copied';
        }
    }

    blockquotes.forEach(function(bq) {
        // Wrap blockquote so the button can be absolutely positioned
        if (bq.parentElement.classList.contains('copyable-block')) return;
        var wrap = document.createElement('div');
        wrap.className = 'copyable-block';
        bq.parentNode.insertBefore(wrap, bq);
        wrap.appendChild(bq);

        var btn = document.createElement('button');
        btn.className = 'copyable-btn';
        btn.type = 'button';
        btn.setAttribute('aria-label', getCopyLabel());
        btn.innerHTML =
            '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' +
            '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>' +
            '<path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>' +
            '</svg>' +
            '<span aria-live="polite">' + getCopyLabel() + '</span>';
        wrap.appendChild(btn);

        btn.addEventListener('click', function() {
            var label = btn.querySelector('span');
            var text = bq.innerText.trim();
            var done = function(success) {
                if (label) label.textContent = success ? getCopiedLabel() : getCopyLabel();
                btn.classList.toggle('copied', success);
                setTimeout(function() {
                    if (label) label.textContent = getCopyLabel();
                    btn.classList.remove('copied');
                }, 2000);
            };

            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(
                    function() { done(true); },
                    function() {
                        // Fallback: select the blockquote so the user can Cmd/Ctrl+C
                        var range = document.createRange();
                        range.selectNodeContents(bq);
                        var sel = window.getSelection();
                        sel.removeAllRanges();
                        sel.addRange(range);
                        done(false);
                    }
                );
            } else {
                var range = document.createRange();
                range.selectNodeContents(bq);
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                done(false);
            }
        });
    });
})();
