(function () {
    var STORAGE_KEY = 'stigaview_recent';
    var MAX_ENTRIES = 10;
    var SKIP = ['/', '/products/', '/stigs/', '/srgs/'];

    var path = window.location.pathname;

    if (SKIP.indexOf(path) === -1) {
        var title = document.title.replace(/ - STIG-A-View$/, '').trim();
        var entries = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
        entries = entries.filter(function (e) { return e.url !== path; });
        entries.unshift({ url: path, title: title });
        localStorage.setItem(STORAGE_KEY, JSON.stringify(entries.slice(0, MAX_ENTRIES)));
    }

    var container = document.getElementById('recent-visits');
    if (!container) return;

    var entries = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]');
    if (entries.length === 0) return;

    var h2 = document.createElement('h2');
    h2.textContent = 'Recently Visited';

    var ul = document.createElement('ul');
    ul.className = 'recent-visits-list';
    entries.forEach(function (e) {
        var li = document.createElement('li');
        var a = document.createElement('a');
        a.href = e.url;
        a.textContent = e.title;
        li.appendChild(a);
        ul.appendChild(li);
    });

    container.appendChild(h2);
    container.appendChild(ul);
})();
