from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FreeLanceProfileViewSet, JobOfferViewSet, RegisterView, FreelanceSkillViewSet, CompanyProfileViewSet, GenerateJobDescriptionView, GenerateCVAdviceView, JobApplicationViewSet, FreelanceDashboardView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

router = DefaultRouter()
router.register(r'freelances', FreeLanceProfileViewSet, basename='freelance')
router.register(r'jobs', JobOfferViewSet, basename='job')
router.register(r'my-skills', FreelanceSkillViewSet, basename='my-skills')
router.register(r'companies', CompanyProfileViewSet, basename='company')
router.register(r'job-offers', JobOfferViewSet, basename='joboffer')
router.register(r'applications', JobApplicationViewSet, basename='application')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('generate-job/', GenerateJobDescriptionView.as_view(), name='generate-job'),
    path('cv-advice/', GenerateCVAdviceView.as_view(), name='cv-advice'),
    path('dashboard/freelance/', FreelanceDashboardView.as_view(), name='freelance-dashboard'),
]