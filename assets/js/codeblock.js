// Code Block Copy Buttons
(function() {
    var codeblocks = document.querySelectorAll('pre code');
    codeblocks.forEach(function(codeblock) {
        var copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        var container = document.createElement('div');
        container.className = 'code-container';

        copyButton.addEventListener('click', function(e) {
            e.target.className = 'copy-success';
            setTimeout(function() { e.target.className = 'copy-button'; }, 1000);
            navigator.clipboard.writeText(codeblock.textContent);
        });

        codeblock.parentNode.insertBefore(container, codeblock);
        container.appendChild(codeblock);
        container.appendChild(copyButton);
    });
})();
