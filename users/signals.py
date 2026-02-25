from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import FreeLanceProfile, CompanyProfile

User = get_user_model()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):

    if created:
        if instance.role == 'FREELANCE':
            FreeLanceProfile.objects.create(freelance_user=instance)
        elif instance.role == 'COMPANY':
            CompanyProfile.objects.create(company_user=instance)