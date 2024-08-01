# account/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Account
from django.core.mail import send_mail
@receiver(post_save, sender=Account)
def create_account_profile(sender, instance, created, **kwargs):
    if created:
        print(f'Profile created for {instance.account_name}')


@receiver(post_save, sender=Account)
def send_welcome_email(sender, instance, created, **kwargs):
    if created:
        send_mail(
            'Welcome to Our Site!',
            'Thank you for signing up.',
            'yogeshkrishnanseeniraj@example.com',
            [instance.email],
            fail_silently=False,
        )