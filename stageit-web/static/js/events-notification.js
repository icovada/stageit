var es = new ReconnectingEventSource('/events/notifications');

basecoat.notificationLimit = 3;



es.addEventListener('notification', function (e) {
    console.log(e.data);
    // create a notification
    var $notification = basecoat.notification('Notification heading', 'Notification message', 'Notification footer');
    // show the notification
    $notification.trigger('show');
}, false);
