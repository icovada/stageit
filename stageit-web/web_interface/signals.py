from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

from web_interface.models import Template

@receiver(post_save, sender=Template)
def create_user_profile(sender, instance, created, **kwargs):
    print("hello")

@receiver(post_save, sender=Template)
def save_user_profile(sender, instance, **kwargs):
    print("Hello")