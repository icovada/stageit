var es = new ReconnectingEventSource('/events/');

es.addEventListener('message', function (e) {
    console.log(e.data);
}, false);

es.addEventListener('reload', function (e) {
    location.reload()
}, false);

es.addEventListener('stream-reset', function (e) {
    // ... client fell behind, reinitialize ...
}, false);