from django.contrib import admin
from .models import User, Sector, FreeLanceProfile, CompanyProfile, HardSkills, FreelanceSkill, SoftSkills, Language, \
    License, Education, JobOffer, JobApplication

class FreelanceSkillInline(admin.TabularInline):
    model = FreelanceSkill
    extra = 1

class EducationInline(admin.StackedInline):
    model = Education
    extra = 0

@admin.register(FreeLanceProfile)
class FreeLanceProfileAdmin(admin.ModelAdmin):
    inlines = [FreelanceSkillInline, EducationInline]

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


@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = (
        'get_email',
        'company_name',
        'is_ready_for_validation',
        'company_is_active'
    )

    list_filter = ('is_ready_for_validation', 'company_is_active')

    search_fields = ('company_user__email', 'company_name')

    actions = ['activate_selected_companies']

    def get_email(self, obj):
        return obj.company_user.email

    get_email.short_description = 'Utilisateur (E-mail)'

    @admin.action(description='Activer les entreprises sélectionnées (si prêtes)')
    def activate_selected_companies(self, request, queryset):
        ready_companies = queryset.filter(is_ready_for_validation=True)
        updated_count = ready_companies.update(company_is_active=True)
        self.message_user(request, f"{updated_count} entreprise(s) activée(s) avec succès.")

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.check_completion()

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ('freelance', 'job_offer', 'status', 'applied_at')
    list_filter = ('status', 'applied_at')
    search_fields = ('freelance__freelance_user__email', 'job_offer__job_title')

admin.site.register(User)
admin.site.register(Sector)
admin.site.register(HardSkills)
admin.site.register(Language)
admin.site.register(License)
admin.site.register(SoftSkills)
admin.site.register(JobOffer)