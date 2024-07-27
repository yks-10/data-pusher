# account/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account

@receiver(post_save, sender=Account)
def create_account_profile(sender, instance, created, **kwargs):
    if created:
        print(f'Profile created for {instance.account_name}')
