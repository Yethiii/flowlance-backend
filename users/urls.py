from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    FreeLanceProfileViewSet, JobOfferViewSet, CompanyDashboardView,
    RegisterView, FreelanceSkillViewSet, CompanyProfileViewSet,
    GenerateJobDescriptionView, GenerateCVAdviceView, JobApplicationViewSet,
    FreelanceDashboardView, CurrentUserView,
    SectorViewSet, SoftSkillsViewSet, LanguageViewSet, EducationViewSet,
    CertificationViewSet, LicenseViewSet, HardSkillsViewSet, CompanyApplicationsView,
    UpdateApplicationStatusView, GenerateRejectionMessageView, ConversationView,
    NotificationCountView, ConversationListView

)

router = DefaultRouter()
router.register(r'freelances', FreeLanceProfileViewSet, basename='freelance')
router.register(r'my-skills', FreelanceSkillViewSet, basename='my-skills')
router.register(r'companies', CompanyProfileViewSet, basename='company')
router.register(r'job-offers', JobOfferViewSet, basename='joboffer')
router.register(r'applications', JobApplicationViewSet, basename='application')

router.register(r'sectors', SectorViewSet, basename='sector')
router.register(r'soft-skills', SoftSkillsViewSet, basename='softskill')
router.register(r'languages', LanguageViewSet, basename='language')
router.register(r'educations', EducationViewSet, basename='education')
router.register(r'certifications', CertificationViewSet, basename='certification')
router.register(r'licenses', LicenseViewSet, basename='license')
router.register(r'hard-skills', HardSkillsViewSet, basename='hardskill')


urlpatterns = [
    path('', include(router.urls)),
    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('generate-job/', GenerateJobDescriptionView.as_view(), name='generate-job'),
    path('cv-advice/', GenerateCVAdviceView.as_view(), name='cv-advice'),
    path('dashboard/freelance/', FreelanceDashboardView.as_view(), name='freelance-dashboard'),
    path('dashboard/company/', CompanyDashboardView.as_view(), name='company-dashboard'),
    path('company/applications/', CompanyApplicationsView.as_view(), name='company-applications'),
    path('applications/<int:pk>/status/', UpdateApplicationStatusView.as_view(), name='update-application-status'),
    path('generate-rejection/', GenerateRejectionMessageView.as_view(), name='generate-rejection'),
    path('messages/<int:other_user_id>/', ConversationView.as_view(), name='conversation'),
    path('notifications/', NotificationCountView.as_view(), name='notifications'),
    path('conversations/', ConversationListView.as_view(), name='conversations-list'),
]