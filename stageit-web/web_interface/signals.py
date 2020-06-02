from datetime import datetime as dt
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_eventstream import send_event

from web_interface.models import History, SerialPort


@receiver(post_save, sender=History)
def history_popup(sender, instance, created, **kwargs):
    now = dt.now()
    hour = now.hour
    minute = now.minute
    second = now.second

    serialport = SerialPort.objects.get(pkid=instance.fkserialport)
    title = serialport.description
    link = f'<a href="/history/{instance.pkid}">{instance.status}</a>'
    footer = f'{hour:02}:{minute:02}:{second:02}'
    send_event('notifications', 'notification', {'title': title, 'link': link, 'footer': footer})
