from django.urls import path, include
from rest_framework.routers import DefaultRouter

# J'ai ajouté CurrentUserView à la fin de tes imports
from .views import (
    FreeLanceProfileViewSet, JobOfferViewSet, CompanyDashboardView,
    RegisterView, FreelanceSkillViewSet, CompanyProfileViewSet,
    GenerateJobDescriptionView, GenerateCVAdviceView, JobApplicationViewSet,
    FreelanceDashboardView, CurrentUserView
)

router = DefaultRouter()
router.register(r'freelances', FreeLanceProfileViewSet, basename='freelance')
router.register(r'jobs', JobOfferViewSet, basename='job')
router.register(r'my-skills', FreelanceSkillViewSet, basename='my-skills')
router.register(r'companies', CompanyProfileViewSet, basename='company')
router.register(r'job-offers', JobOfferViewSet, basename='joboffer')
router.register(r'applications', JobApplicationViewSet, basename='application')

urlpatterns = [
    path('', include(router.urls)),

    path('users/me/', CurrentUserView.as_view(), name='current-user'),
    path('register/', RegisterView.as_view(), name='register'),
    path('generate-job/', GenerateJobDescriptionView.as_view(), name='generate-job'),
    path('cv-advice/', GenerateCVAdviceView.as_view(), name='cv-advice'),
    path('dashboard/freelance/', FreelanceDashboardView.as_view(), name='freelance-dashboard'),
    path('dashboard/company/', CompanyDashboardView.as_view(), name='company-dashboard'),
]