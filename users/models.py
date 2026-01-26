from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date

class User(AbstractUser):
    role_choices = (
        ('FREELANCE','freelance'),
        ('COMPANY','company'),
        ('ADMIN','admin'),
    )

    role = models.CharField(max_length=10, choices=role_choices, default='FREELANCE')

    def __str__(self):
        return f"{self.username} ({self.role})"

class FreeLanceProfile(models.Model):

    gender_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Other')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    age = models.PositiveIntegerField(null=False, blank=False)
    gender = models.CharField(choices=gender_choices, blank=False, null=False)
    location = models.CharField(max_length=200)
    full_remote = models.BooleanField(default=False)
    enterprise_number = models.CharField(max_length=50, blank=True, help_text="N° de TVA ou Entreprise")
    github_url = models.URLField(max_length=255,null=True, blank=True)
    linkedin_url = models.URLField(max_length=255,null=True, blank=True)
    website_url = models.URLField(max_length=255,null=True, blank=True)
    availability = models.BooleanField(default=True)

    cv_file = models.FileField(upload_to='cv_files/', null=True, blank=True)

    def __str__(self):
        return f"Freelance: {self.user.username}"

class SoftSkills(models.Model):
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class HardSkills(models.Model):
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    level = models.PositiveSmallIntegerField(help_text="Niveau de 1 à 5")

class Education(models.Model):
    degree_choices = (
        ('SEC', 'Secondaire'),
        ('BAC', 'Bachelier / Licence'),
        ('MAS', 'Master'),
        ('DOC', 'Doctorat'),
        ('PRO', 'Formation Pro / Certifiante'),
    )
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE)
    degree_type = models.CharField(max_length=3, choices=degree_choices, default='BAC')
    diploma_name = models.CharField(max_length=255)
    school_name = models.CharField(max_length=100)
    year_obtained = models.PositiveIntegerField()
    proof_file = models.FileField(upload_to='educ/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

class Certification(models.Model):
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE)
    certification_name = models.CharField(max_length=255)
    expiry_date = models.DateField(null=True, blank=True)
    proof_file = models.FileField(upload_to='certs/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    @property
    def is_valid(self):
        if self.expiry_date and self.expiry_date < date.today():
            return False
        return self.is_verified

class DriverLicense(models.Model):
    license_types = (
        ('AM', 'Cyclomoteur'), ('A', 'Moto'), ('B', 'Auto'),
        ('C', 'Poids Lourds'), ('D', 'Transport personnes'),
        ('BE', 'Remorque'), ('CACES_1', 'Nacelle R486 C1'),
        ('CACES_3', 'Chariot R489 C3'), ('ENGIN', 'Engin de chantier'),
        ('AUTRE', 'Autre')
    )
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE)
    license_type = models.CharField(max_length=20, choices=license_types)
    valid_until = models.DateField(null=True, blank=True)
    proof_file = models.FileField(upload_to='licenses/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    @property
    def is_currently_valid(self):
        if self.valid_until and self.valid_until < date.today():
            return False
        return self.is_verified

class Language(models.Model):
    level_choices = (
        ('A1', 'Débutant'), ('A2', 'Élémentaire'),
        ('B1', 'Intermédiaire'), ('B2', 'Avancé'),
        ('C1', 'Autonome'), ('C2', 'Maîtrise/Maternel'),
    )
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE)
    language = models.CharField(max_length=50)
    level = models.CharField(choices=level_choices, default='')

class CompanyProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    availability = models.BooleanField(default=True)
    company_name = models.CharField(max_length=200)


    def __str__(self):
        return f"Company: {self.company_name}"