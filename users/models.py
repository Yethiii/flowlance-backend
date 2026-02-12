from django.core.validators import MinValueValidator, MaxValueValidator
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

class Sector(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class SoftSkills(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class HardSkills(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.sector.name})"

class FreeLanceProfile(models.Model):

    gender_choices = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Other')
    )
    availability_choices = (
        ('FULL', 'Temps plein'),
        ('PART', 'Temps partiel'),
        ('NONE', 'Indisponible')
    )

    freelance_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='freelance_profile')
    freelance_birth_date = models.DateField()

    @property
    def age(self):
        today = date.today()
        birth = self.freelance_birth_date
        return (
                today.year - birth.year
                - ((today.month, today.day) < (birth.month, birth.day))
        )

    freelance_gender = models.CharField(choices=gender_choices,max_length=1, blank=False, null=False)
    freelance_location = models.CharField(max_length=200)
    freelance_full_remote = models.BooleanField(default=False)
    freelance_enterprise_number = models.CharField(max_length=50, blank=True, help_text="N° de TVA ou Entreprise")
    freelance_github_url = models.URLField(max_length=255,null=True, blank=True)
    freelance_linkedin_url = models.URLField(max_length=255,null=True, blank=True)
    freelance_website_url = models.URLField(max_length=255,null=True, blank=True)
    freelance_availability = models.CharField(choices=availability_choices, max_length=4)
    freelance_is_active = models.BooleanField(default=True)
    freelance_sectors = models.ManyToManyField(Sector, related_name='freelances', blank=True)
    freelance_soft_skills = models.ManyToManyField(SoftSkills, related_name='freelances', blank=True)
    freelance_cv_file = models.FileField(upload_to='cv_files/', null=True, blank=True)

    def __str__(self):
        return f"Freelance: {self.freelance_user.username}"


class FreelanceSkill(models.Model):
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE, related_name='skill_levels')
    skill = models.ForeignKey(HardSkills, on_delete=models.CASCADE)
    level = models.PositiveSmallIntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ],
        help_text="Niveau de 0 à 5"
    )
    class Meta:
        unique_together = ('profile', 'skill')

    def __str__(self):
        return f"{self.skill.name} : {self.level}/5"

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

class License(models.Model):
    license_types = (
        ('AM', 'Cyclomoteur'), ('A', 'Moto'), ('B', 'Auto'),
        ('C', 'Poids Lourds'), ('D', 'Transport personnes'),
        ('BE', 'Remorque'), ('CACES_1', 'Nacelle R486 C1'),
        ('CACES_3', 'Chariot R489 C3'), ('ENGIN', 'Engin de chantier'),
        ('AUTRE', 'Autre')
    )
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE, related_name='licenses')
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
        ('C1', 'Autonome'), ('LM', 'Langue Maternelle'),
    )
    profile = models.ForeignKey(FreeLanceProfile, on_delete=models.CASCADE)
    language = models.CharField(max_length=50)
    level = models.CharField(choices=level_choices, max_length=2)

class CompanyProfile(models.Model):

    SIZE_CHOICES = (
            ('SMALL', '1-10 employés'),
            ('MEDIUM', '11-50 employés'),
            ('LARGE', '50-250 employés'),
            ('CORP', 'Plus de 250 employés'),
    )

    company_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    company_size = models.CharField(max_length=10, choices=SIZE_CHOICES)
    company_name = models.CharField(max_length=200)
    company_street = models.CharField(max_length=200)
    company_number = models.CharField(max_length=10)
    company_postcode = models.CharField(max_length=200)
    company_city = models.CharField(max_length=200)
    company_country = models.CharField(max_length=200, default='Belgique')
    company_phone = models.CharField(max_length=20, blank=True)
    company_email = models.EmailField(max_length=255, blank=True)
    company_linkedin = models.URLField(max_length=255, null=True, blank=True)
    company_description = models.TextField(blank=True, help_text="Présentation de l'entreprise et de sa culture")
    company_website = models.URLField(max_length=255, null=True, blank=True)
    company_TVA = models.CharField(max_length=50, blank=True, verbose_name="N° de TVA")
    company_BCE = models.CharField(max_length=50, blank=True, verbose_name="N° BCE")
    company_sectors = models.ManyToManyField(Sector, related_name='companies', blank=True)
    company_is_verified = models.BooleanField(default=False)
    company_is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"Company: {self.company_name}"

class JobOffer(models.Model):
    offer_company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name='job_offers')
    offer_location = models.CharField(max_length=200)
    offer_title = models.CharField(max_length=200)
    offer_description = models.TextField()
    offer_sector = models.ForeignKey(Sector, on_delete=models.SET_NULL, null=True)
    offer_hardskills = models.ManyToManyField(HardSkills, related_name='required_hardskills', blank=True)
    offer_softskills = models.ManyToManyField(SoftSkills, related_name='required_softskills', blank=True)
    offer_created_at = models.DateTimeField(auto_now_add=True)
    offer_is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.offer_title} - {self.offer_company.company_name}"