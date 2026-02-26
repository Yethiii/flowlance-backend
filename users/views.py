from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import FreeLanceProfile, JobOffer, FreelanceSkill
from django.contrib.auth import get_user_model
from .serializers import FreeLanceProfileSerializer, JobOfferSerializer, UserRegistrationSerializer, FreelanceSkillSerializer
from .permissions import IsFreelanceRole, IsCompanyRole, IsOwnerOfProfile

User = get_user_model()

class FreeLanceProfileViewSet(viewsets.ModelViewSet):
    queryset = FreeLanceProfile.objects.all()
    serializer_class = FreeLanceProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfProfile]

class FreelanceSkillViewSet(viewsets.ModelViewSet):
    serializer_class = FreelanceSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FreelanceSkill.objects.filter(profile__freelance_user=self.request.user)

    def perform_create(self, serializer):
        profil = FreeLanceProfile.objects.get(freelance_user=self.request.user)
        # On remplace freelance=profil par profile=profil
        serializer.save(profile=profil)

class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsCompanyRole()]
        return [IsAuthenticated()]

# --- GUICHET 4 : L'Inscription ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer