from django.contrib import admin
from .models import User, Sector, FreeLanceProfile, CompanyProfile, HardSkills, FreelanceSkill, SoftSkills, Language, \
    License, Education, JobOffer

class FreelanceSkillInline(admin.TabularInline):
    model = FreelanceSkill
    extra = 1

@admin.register(FreeLanceProfile)
class FreeLanceProfileAdmin(admin.ModelAdmin):
    inlines = [FreelanceSkillInline]

    list_display = (
        'freelance_user',
        'freelance_location',
        'freelance_availability',
        'is_ready_for_validation',
        'freelance_is_active'
    )

    list_filter = ('is_ready_for_validation', 'freelance_is_active', 'freelance_availability')

    search_fields = ('freelance_user__username', 'freelance_location')

    actions = ['activate_selected_profiles']

    @admin.action(description='Activer les profils sélectionnés (si prêts)')
    def activate_selected_profiles(self, request, queryset):
        ready_profiles = queryset.filter(is_ready_for_validation=True)
        updated_count = ready_profiles.update(freelance_is_active=True)
        self.message_user(request, f"{updated_count} profil(s) activé(s) avec succès.")

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.check_completion()

admin.site.register(User)
admin.site.register(Sector)
admin.site.register(CompanyProfile)
admin.site.register(HardSkills)
admin.site.register(Language)
admin.site.register(License)
admin.site.register(Education)
admin.site.register(SoftSkills)
admin.site.register(JobOffer)