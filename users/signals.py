import os
from django.db.models.signals import post_save, pre_save
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

@receiver(pre_save, sender=FreeLanceProfile)
def auto_delete_file_on_change(sender, instance, **kwargs):

    if not instance.pk:
        return False

    try:
        old_profile = FreeLanceProfile.objects.get(pk=instance.pk)
        old_file = old_profile.freelance_cv_file
    except FreeLanceProfile.DoesNotExist:
        return False

    new_file = instance.freelance_cv_file
    if not old_file == new_file and old_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)