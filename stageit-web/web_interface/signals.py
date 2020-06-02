from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_eventstream import send_event

from web_interface.models import Template

@receiver(post_save, sender=Template)
def history_inprogress(sender, instance, created, **kwargs):
    send_event('notifications', 'notification', {'text':'hello'})
    send_event('test', 'reload', {})
    print(instance)
