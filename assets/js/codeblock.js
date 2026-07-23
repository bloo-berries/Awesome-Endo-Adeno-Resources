// Code Block Copy Buttons
(function() {
    var codeblocks = document.querySelectorAll('pre code');
    codeblocks.forEach(function(codeblock) {
        var copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        var container = document.createElement('div');
        container.className = 'code-container';

        copyButton.addEventListener('click', function(e) {
            var btn = e.currentTarget;
            (window.appUtils ? window.appUtils.copyText : copyText)(codeblock.textContent).then(function() {
                btn.className = 'copy-success';
                setTimeout(function() { btn.className = 'copy-button'; }, 1000);
            }).catch(function() {
                // Fallback: select text
                var range = document.createRange();
                range.selectNodeContents(codeblock);
                var sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
            });
        });

        codeblock.parentNode.insertBefore(container, codeblock);
        container.appendChild(codeblock);
        container.appendChild(copyButton);
    });
})();
