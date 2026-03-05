import requests
import PyPDF2
from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import FreeLanceProfile, JobOffer, FreelanceSkill, CompanyProfile
from django.contrib.auth import get_user_model
from .serializers import FreeLanceProfileSerializer, JobOfferSerializer, UserRegistrationSerializer, FreelanceSkillSerializer, CompanyProfileSerializer
from .permissions import IsFreelanceRole, IsCompanyRole, IsOwnerOfProfile
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response

User = get_user_model()

class FreeLanceProfileViewSet(viewsets.ModelViewSet):
    queryset = FreeLanceProfile.objects.all()
    serializer_class = FreeLanceProfileSerializer
    permission_classes = [IsAuthenticated, IsOwnerOfProfile]

    def perform_update(self, serializer):
        profil = serializer.save()
        profil.check_completion()

class FreelanceSkillViewSet(viewsets.ModelViewSet):
    serializer_class = FreelanceSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FreelanceSkill.objects.filter(profile__freelance_user=self.request.user)

    def perform_create(self, serializer):
        profil = FreeLanceProfile.objects.get(freelance_user=self.request.user)
        serializer.save(profile=profil)
        profil.check_completion()

class JobOfferViewSet(viewsets.ModelViewSet):
    serializer_class = JobOfferSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    filterset_fields = ['offer_sector', 'offer_location']

    search_fields = ['offer_title', 'offer_description']

    ordering_fields = ['offer_created_at']
    ordering = ['-offer_created_at']

    def get_queryset(self):
        user = self.request.user

        if user.role == 'COMPANY':
            if hasattr(user, 'company_profile'):
                return JobOffer.objects.filter(offer_company=user.company_profile)
            return JobOffer.objects.none()

        else:
            return JobOffer.objects.filter(
                offer_is_active=True,
                offer_company__company_is_active=True
            )

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'COMPANY':
            raise PermissionDenied("Seules les entreprises peuvent publier des annonces.")

        company_profile = user.company_profile
        if not company_profile.company_is_active:
            raise PermissionDenied(
                "Votre compte entreprise doit être validé par un administrateur avant de pouvoir publier.")

        serializer.save(offer_company=company_profile)

class CompanyProfileViewSet(viewsets.ModelViewSet):
    queryset = CompanyProfile.objects.all()
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        profil = serializer.save()
        profil.check_completion()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

class JobOfferViewSet(viewsets.ModelViewSet):
    queryset = JobOffer.objects.all()
    serializer_class = JobOfferSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'COMPANY':
            raise PermissionDenied("Seules les entreprises peuvent publier des annonces.")

        company_profile = user.company_profile

        if not company_profile.company_is_active:
            raise PermissionDenied(
                "Votre compte entreprise doit être validé par un administrateur avant de pouvoir publier.")

        serializer.save(offer_company=company_profile)


class GenerateJobDescriptionView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != 'COMPANY' or not getattr(user.company_profile, 'company_is_active', False):
            raise PermissionDenied("Seules les entreprises validées peuvent utiliser l'assistant IA.")

        keywords = request.data.get('keywords', '')
        if not keywords:
            raise ValidationError({"keywords": "Veuillez fournir des mots-clés pour générer l'annonce."})

        system_prompt = (
            "Tu es un expert en recrutement RH de haut niveau. "
            "Rédige une offre d'emploi professionnelle, structurée et attractive "
            "en te basant EXCLUSIVEMENT sur les mots-clés fournis. "
            "N'invente pas d'avantages sociaux non mentionnés. "
            "Formate la réponse avec des paragraphes clairs."
        )

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json"
        }

        data = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voici les mots-clés : {keywords}"}
            ]
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )
            response.raise_for_status()

            result = response.json()
            generated_text = result['choices'][0]['message']['content']

            return Response({"generated_description": generated_text})

        except Exception as e:
            return Response({"error": "Erreur lors de la communication avec l'IA.", "details": str(e)}, status=500)


class GenerateCVAdviceView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != 'FREELANCE':
            raise PermissionDenied("Seuls les freelances peuvent accéder au coaching.")

        cv_file = request.FILES.get('cv_file')  # Note : On l'appelle 'cv_file' maintenant
        if not cv_file:
            raise ValidationError({"cv_file": "Veuillez fournir votre CV au format PDF."})

        if not cv_file.name.lower().endswith('.pdf'):
            raise ValidationError({"cv_file": "Le fichier doit obligatoirement être un PDF."})

        try:
            pdf_reader = PyPDF2.PdfReader(cv_file)
            extracted_text = ""
            for page in pdf_reader.pages:
                extracted_text += page.extract_text() + "\n"

            if not extracted_text.strip():
                raise ValidationError({"cv_file": "Le PDF semble vide ou est une image scannée sans texte détectable."})
        except Exception as e:
            raise ValidationError({"cv_file": f"Erreur lors de la lecture du PDF : {str(e)}"})

        system_prompt = (
            "Tu es un coach carrière bienveillant et un expert en recrutement IT. "
            "Analyse le contenu de ce CV (qui a été extrait d'un PDF). "
            "Fournis 3 conseils clairs, précis et actionnables pour l'améliorer "
            "(mise en valeur des compétences, mots-clés, clarté du profil). "
            "Garde un ton professionnel et encourageant."
        )

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "HTTP-Referer": "http://localhost:8000",
            "Content-Type": "application/json"
        }

        data = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Voici le contenu de mon CV :\n\n{extracted_text}"}
            ]
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            )

            if response.status_code != 200:
                return Response({
                    "error": "L'IA a rejeté la demande.",
                    "details": response.text
                }, status=500)

            result = response.json()
            advice_text = result['choices'][0]['message']['content']

            return Response({"cv_advice": advice_text})

        except requests.exceptions.RequestException as e:
            return Response({"error": "Problème réseau avec le serveur IA.", "details": str(e)}, status=500)