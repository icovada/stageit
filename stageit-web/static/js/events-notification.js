var es = new ReconnectingEventSource('/events/notifications');

basecoat.notificationLimit = 3;



es.addEventListener('notification', function (e) {
    console.log(e.data);
    // create a notification
    var data = JSON.parse(e.data);
    var $notification = basecoat.notification(data.title, data.link, data.footer);
    // show the notification
    $notification.trigger('show');
}, false);
