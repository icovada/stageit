from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from web_interface.models import Template

@receiver(post_save, sender=Template)
def history_inprogress(sender, instance, created, **kwargs):
    print(sender)
    print(instance)
    print(created)
    print(kwargs['update_fields'])
    print(kwargs['raw'])
    print("hello")

@receiver(post_save, sender=Template)
def history_completed(sender, instance, **kwargs):
    print("Hello")