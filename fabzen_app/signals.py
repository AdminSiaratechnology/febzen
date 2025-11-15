from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import CustomUser,Client
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Logic to create a user profile or perform other actions
        if instance.role == 'client':
            Client.objects.create(user=instance)
            print(f'Creating profile for new client user: {instance.username}')

@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    if instance.role == 'client':
        instance.client.save()
        print(f'Saving profile for client user: {instance.username}')
