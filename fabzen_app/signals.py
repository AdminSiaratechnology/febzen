from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import CustomUser, Client

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created and instance.role == 'client':
        Client.objects.get_or_create(user=instance)

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'client':
        instance.client.save()
       