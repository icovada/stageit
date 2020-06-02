from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_eventstream import send_event

from web_interface.models import History

from datetime import datetime as dt

@receiver(post_save, sender=History)
def history_popup(sender, instance, created, **kwargs):
    now = dt.now()
    hour = now.hour
    minute = now.minute
    second = now.second

    title = instance.status
    link = f'<a href="/history/{instance.pkid}">Open</a>'
    footer = f'{hour}:{minute}:{second}'
    send_event('notifications', 'notification', {'title': title, 'link': link, 'footer': footer})
