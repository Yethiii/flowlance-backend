from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import FreeLanceProfile, JobOffer
from django.contrib.auth import get_user_model
from .serializers import FreeLanceProfileSerializer, JobOfferSerializer, UserRegistrationSerializer
from .permissions import IsFreelanceRole, IsCompanyRole, IsOwnerOfProfile

User = get_user_model()

class FreeLanceProfileViewSet(viewsets.ModelViewSet):

    queryset = FreeLanceProfile.objects.all()
    serializer_class = FreeLanceProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfProfile]


class JobOfferViewSet(viewsets.ModelViewSet):

    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsCompanyRole()]
        return [IsAuthenticated()]

class RegisterView(generics.CreateAPIView):

    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer