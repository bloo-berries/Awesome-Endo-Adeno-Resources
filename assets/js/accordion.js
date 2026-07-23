// Table Accordion Conversion + Expand/Collapse All
(function() {
    var chevronSVG = window.appIcons ? window.appIcons.chevron : '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>';

    function stripTags(html) {
        var tmp = document.createElement('div');
        tmp.innerHTML = html;
        return tmp.textContent.trim();
    }

    function truncate(text, max) {
        if (text.length <= max) return text;
        return text.substring(0, max).replace(/\s+\S*$/, '') + '\u2026';
    }

    var tables = document.querySelectorAll('.content table');
    tables.forEach(function(table) {
        var thead = table.querySelector('thead');
        if (!thead) return;
        var headers = [];
        thead.querySelectorAll('th').forEach(function(th) {
            headers.push(th.textContent.trim());
        });
        if (headers.length < 2) return;

        var container = document.createElement('div');
        container.className = 'table-accordion';

        var rows = table.querySelectorAll('tbody tr');
        rows.forEach(function(row) {
            var cells = row.querySelectorAll('td');
            if (!cells.length) return;

            var details = document.createElement('details');
            details.setAttribute('data-accordion', 'table');

            var titleText = stripTags(cells[0].innerHTML);
            var badgeText = '';
            var previewText = '';
            if (cells.length >= 3) {
                badgeText = stripTags(cells[1].innerHTML);
                previewText = truncate(stripTags(cells[2].innerHTML), 120);
            } else if (cells.length === 2) {
                previewText = truncate(stripTags(cells[1].innerHTML), 120);
            }

            var summary = document.createElement('summary');
            var headerDiv = '<div class="accordion-card-header">';
            headerDiv += '<span class="accordion-card-title">' + titleText + '</span>';
            if (badgeText) headerDiv += '<span class="accordion-card-badge">' + badgeText + '</span>';
            headerDiv += '<span class="accordion-card-chevron">' + chevronSVG + '</span>';
            headerDiv += '</div>';
            if (previewText) headerDiv += '<p class="accordion-card-preview">' + previewText + '</p>';
            summary.innerHTML = headerDiv;
            details.appendChild(summary);

            if (cells.length > 1) {
                var dl = document.createElement('dl');
                dl.className = 'table-accordion-content';
                for (var i = 1; i < cells.length; i++) {
                    var rowDiv = document.createElement('div');
                    rowDiv.className = 'table-accordion-row';
                    var dt = document.createElement('dt');
                    dt.textContent = headers[i] || '';
                    var dd = document.createElement('dd');
                    dd.innerHTML = cells[i].innerHTML;
                    rowDiv.appendChild(dt);
                    rowDiv.appendChild(dd);
                    dl.appendChild(rowDiv);
                }
                details.appendChild(dl);
            }
            container.appendChild(details);
        });

        if (container.children.length > 0) {
            table.parentNode.replaceChild(container, table);
        }
    });

})();
