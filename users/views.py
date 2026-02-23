from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import FreeLanceProfile, JobOffer
from .serializers import FreeLanceProfileSerializer, JobOfferSerializer
from .permissions import IsFreelanceRole, IsCompanyRole, IsOwnerOfProfile


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
