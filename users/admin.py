from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Sector, HardSkills, FreeLanceProfile, CompanyProfile

admin.site.register(User)
admin.site.register(Sector)
admin.site.register(HardSkills)
admin.site.register(FreeLanceProfile)
admin.site.register(CompanyProfile)