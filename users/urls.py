from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FreeLanceProfileViewSet, JobOfferViewSet

router = DefaultRouter()
router.register(r'freelances', FreeLanceProfileViewSet, basename='freelance')
router.register(r'jobs', JobOfferViewSet, basename='job')

urlpatterns = [
    path('api/', include(router.urls)),
]