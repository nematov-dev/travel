from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import PostMedia

@receiver(post_delete, sender=PostMedia)
def delete_media_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)