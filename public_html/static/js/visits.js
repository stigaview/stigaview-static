(function () {
    var PRODUCTS_KEY = 'stigaview_recent_products';
    var STIGS_KEY    = 'stigaview_recent_stigs';
    var MAX_ENTRIES  = 10;

    function pageType(path) {
        var parts = path.replace(/^\/|\/$/g, '').split('/');
        if (parts[0] !== 'products' || parts.length < 2) return null;
        if (parts.length === 2) return 'product';
        if (parts.length === 3) return 'stig';
        if (parts.length === 4 && parts[3] === 'onepage') return 'stig';
        return null; // control pages and anything deeper → skip
    }

    function record(key, path, title) {
        var entries = JSON.parse(localStorage.getItem(key) || '[]');
        entries = entries.filter(function (e) { return e.url !== path; });
        entries.unshift({ url: path, title: title });
        localStorage.setItem(key, JSON.stringify(entries.slice(0, MAX_ENTRIES)));
    }

    function renderSection(container, heading, key) {
        var entries = JSON.parse(localStorage.getItem(key) || '[]');
        if (entries.length === 0) return;

        var h2 = document.createElement('h2');
        h2.textContent = heading;

        var ul = document.createElement('ul');
        ul.className = 'recent-visits-list';
        entries.forEach(function (e) {
            var li = document.createElement('li');
            var a  = document.createElement('a');
            a.href = e.url;
            a.textContent = e.title;
            li.appendChild(a);
            ul.appendChild(li);
        });

        container.appendChild(h2);
        container.appendChild(ul);
    }

    var path  = window.location.pathname;
    var type  = pageType(path);

    if (type) {
        var title = document.title.replace(/ - STIG-A-View$/, '').trim();
        record(type === 'product' ? PRODUCTS_KEY : STIGS_KEY, path, title);
    }

    var container = document.getElementById('recent-visits');
    if (!container) return;

    renderSection(container, 'Recently Visited Products', PRODUCTS_KEY);
    renderSection(container, 'Recently Visited STIGs',    STIGS_KEY);
})();
