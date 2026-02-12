from django.contrib import admin
from .models import User, Sector, FreeLanceProfile, CompanyProfile, HardSkills, FreelanceSkill, SoftSkills, Language, License, Education, JobOffer

class FreelanceSkillInline(admin.TabularInline):
    model = FreelanceSkill
    extra = 1

@admin.register(FreeLanceProfile)
class FreeLanceProfileAdmin(admin.ModelAdmin):
    inlines = [FreelanceSkillInline]
    list_display = ('freelance_user', 'freelance_availability', 'freelance_is_active')

admin.site.register(User)
admin.site.register(Sector)
admin.site.register(CompanyProfile)
admin.site.register(HardSkills)
admin.site.register(Language)
admin.site.register(License)
admin.site.register(Education)
admin.site.register(SoftSkills)
admin.site.register(JobOffer)
