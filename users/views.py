import requests
import PyPDF2
import json
from rest_framework import viewsets, generics, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import (
    FreeLanceProfile, JobOffer, FreelanceSkill, CompanyProfile,
    JobApplication, Sector, SoftSkills, Language, Education, Certification, License,
    HardSkills, Message
)
from django.contrib.auth import get_user_model
from .serializers import (
    FreeLanceProfileSerializer, JobOfferSerializer, UserRegistrationSerializer,
    FreelanceSkillSerializer, CompanyProfileSerializer, JobApplicationSerializer,
    SectorSerializer, SoftSkillSerializer, LanguageSerializer,
    EducationSerializer, CertificationSerializer, LicenseSerializer, HardSkillSerializer,
    CompanyJobApplicationSerializer, MessageSerializer
)
from .permissions import IsFreelanceRole, IsCompanyRole, IsOwnerOfProfile
from rest_framework.exceptions import PermissionDenied, ValidationError
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

User = get_user_model()

# --- 1. VUES DE BASE (Secteurs et Soft Skills) ---
class SectorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sector.objects.all()
    serializer_class = SectorSerializer
    permission_classes = [IsAuthenticated]

class SoftSkillsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SoftSkills.objects.all()
    serializer_class = SoftSkillSerializer
    permission_classes = [IsAuthenticated]


# --- 2. VUES DU PROFIL FREELANCE ---

class FreeLanceProfileViewSet(viewsets.ModelViewSet):
    serializer_class = FreeLanceProfileSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    # 1. On sépare les permissions
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # Tout utilisateur connecté peut LIRE un profil
            return [IsAuthenticated()]
        # Mais seul le vrai propriétaire peut MODIFIER son profil
        return [IsAuthenticated(), IsOwnerOfProfile()]

    # 2. On sépare les recherches
    def get_queryset(self):
        user = self.request.user

        # 1. Quand React demande "Mon Profil" (GET /api/freelances/)
        if self.action == 'list':
            return FreeLanceProfile.objects.filter(freelance_user=user)

        # 2. Quand une entreprise consulte un profil public via son ID (GET /api/freelances/<id>/)
        elif self.action == 'retrieve':
            # L'entreprise peut le voir s'il est actif, TOI tu peux le voir même s'il est inactif
            return FreeLanceProfile.objects.filter(
                Q(freelance_is_active=True) | Q(freelance_user=user)
            )

        # 3. Pour modifier (PUT, PATCH) ou supprimer (DELETE)
        return FreeLanceProfile.objects.filter(freelance_user=user)

    def perform_update(self, serializer):
        profil = serializer.save()
        profil.check_completion()

    @action(detail=False, methods=['post'])
    def deactivate(self, request):
        profil = self.get_queryset().first()
        if profil:
            profil.freelance_is_active = False
            profil.save()
            return Response({"message": "Compte suspendu avec succès."})
        return Response({"erreur": "Profil non trouvé"}, status=404)

    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        user = request.user
        user.delete()
        return Response(status=204)

class FreelanceSkillViewSet(viewsets.ModelViewSet):
    serializer_class = FreelanceSkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return FreelanceSkill.objects.filter(profile__freelance_user=self.request.user)

    def perform_create(self, serializer):
        from rest_framework.exceptions import ValidationError

        try:
            profil = FreeLanceProfile.objects.get(freelance_user=self.request.user)

            skill_name = self.request.data.get('skill')
            if FreelanceSkill.objects.filter(profile=profil, skill__name=skill_name).exists():
                raise ValidationError({"erreur": f"Vous avez déjà ajouté la compétence {skill_name}."})

            serializer.save(profile=profil)
            profil.check_completion()

        except ValidationError as v:
            raise v
        except Exception as e:
            print(f"CRASH DANS LA VUE HARD SKILL: {e}")
            raise ValidationError({"erreur_serveur": str(e)})

class LanguageViewSet(viewsets.ModelViewSet):
    serializer_class = LanguageSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Language.objects.filter(profile__freelance_user=self.request.user)

    def perform_create(self, serializer):
        profil = FreeLanceProfile.objects.get(freelance_user=self.request.user)
        serializer.save(profile=profil)

class EducationViewSet(viewsets.ModelViewSet):
    serializer_class = EducationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Education.objects.filter(profile__freelance_user=self.request.user)

    def perform_create(self, serializer):
        profil = FreeLanceProfile.objects.get(freelance_user=self.request.user)
        serializer.save(profile=profil)

class CertificationViewSet(viewsets.ModelViewSet):
    serializer_class = CertificationSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Certification.objects.filter(profile__freelance_user=self.request.user)

    def perform_create(self, serializer):
        profil = FreeLanceProfile.objects.get(freelance_user=self.request.user)
        serializer.save(profile=profil)

class LicenseViewSet(viewsets.ModelViewSet):
    serializer_class = LicenseSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return License.objects.filter(profile__freelance_user=self.request.user)

    def perform_create(self, serializer):
        profil = FreeLanceProfile.objects.get(freelance_user=self.request.user)
        serializer.save(profile=profil)


# --- 3. VUES ENTREPRISE ET OFFRES ---
class CompanyProfileViewSet(viewsets.ModelViewSet):
    serializer_class = CompanyProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        user = self.request.user

        # 1. Quand React demande "Mon Profil Entreprise" (GET /api/companies/)
        if self.action == 'list':
            return CompanyProfile.objects.filter(company_user=user)

        # 2. Quand un freelance consulte un profil entreprise (GET /api/companies/<id>/)
        elif self.action == 'retrieve':
            # Le freelance le voit s'il est actif, l'entreprise le voit tout le temps
            return CompanyProfile.objects.filter(
                Q(company_is_active=True) | Q(company_user=user)
            )

        # 3. Pour modifier (PUT, PATCH) ou supprimer (DELETE)
        return CompanyProfile.objects.filter(company_user=user)

    def perform_update(self, serializer):
        profil = serializer.save()
        profil.check_completion()

    # 2. Action de Suspension
    @action(detail=False, methods=['post'])
    def deactivate(self, request):
        profil = self.get_queryset().first()
        if profil:
            profil.company_is_active = False
            profil.save()
            return Response({"message": "Compte entreprise suspendu avec succès."})
        return Response({"erreur": "Profil non trouvé"}, status=404)

    # 3. Action de Suppression définitive (Cascade)
    @action(detail=False, methods=['delete'])
    def delete_account(self, request):
        user = request.user
        user.delete()
        return Response(status=204)

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
            return JobOffer.objects.filter(offer_is_active=True, offer_company__company_is_active=True)

    def perform_create(self, serializer):
        user = self.request.user
        if user.role != 'COMPANY':
            raise PermissionDenied("Seules les entreprises peuvent publier des annonces.")
        company_profile = user.company_profile
        if not company_profile.company_is_active:
            raise PermissionDenied("Votre compte entreprise doit être validé par un administrateur avant de pouvoir publier.")
        serializer.save(offer_company=company_profile)

class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'FREELANCE':
            return JobApplication.objects.filter(freelance=user.freelance_profile)
        elif user.role == 'COMPANY':
            return JobApplication.objects.filter(job_offer__company=user.company_profile)
        return JobApplication.objects.none()

    def perform_create(self, serializer):
        if self.request.user.role != 'FREELANCE':
            raise PermissionDenied("Seuls les freelances peuvent postuler à une offre.")
        serializer.save()


# --- 4. AUTH & DASHBOARDS & IA ---
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        role = getattr(user, 'role', getattr(user, 'user_type', 'FREELANCE'))
        return Response({'id': user.id, 'email': user.email, 'role': role})

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

        cv_file = request.FILES.get('cv_file')
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
                return Response({"error": "L'IA a rejeté la demande.", "details": response.text}, status=500)

            result = response.json()
            advice_text = result['choices'][0]['message']['content']
            profil = request.user.freelance_profile
            profil.ai_cv_advice = advice_text
            profil.save(update_fields=['ai_cv_advice'])
            return Response({"cv_advice": advice_text})

        except requests.exceptions.RequestException as e:
            return Response({"error": "Problème réseau avec le serveur IA.", "details": str(e)}, status=500)


class FreelanceDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'FREELANCE':
            raise PermissionDenied("Seuls les freelances ont accès à ce dashboard.")

        freelance = user.freelance_profile
        matching_jobs = JobOffer.objects.filter(offer_sector__in=freelance.freelance_sectors.all()).distinct().order_by('-offer_created_at')[:3]

        if not matching_jobs:
            return Response({"dashboard": [], "message": "Aucune mission dans votre secteur pour le moment."})

        hard_skills = ", ".join([str(hs) for hs in freelance.skill_levels.all()])
        freelance_info = f"Localisation: {freelance.freelance_location}\nCompétences: {hard_skills}"

        jobs_prompt_text = ""
        for job in matching_jobs:
            jobs_prompt_text += f"\n--- OFFRE ID {job.id} ---\nTitre: {job.offer_title}\nDescription: {job.offer_description}\n"

        system_prompt = (
            "Tu es un coach carrière bienveillant et un algorithme de matching RH. "
            "Je vais te donner le profil d'un freelance et une liste de missions. "
            "Pour chaque mission, donne un score de compatibilité sur 100. "
            "Dans ton explication, adresse-toi DIRECTEMENT au freelance (utilise le vouvoiement 'vous'). "
            "Explique-lui de manière positive pourquoi cette mission pourrait lui convenir (ex: 'Cette annonce peut vous convenir car vous maîtrisez...'). "
            "Si le profil correspond un peu moins, reste encourageant. "
            "Réponds STRICTEMENT en JSON avec ce format exact : "
            "[{\"job_id\": 1, \"score\": 85, \"explication\": \"...\"}]"
        )
        user_prompt = f"=== MON PROFIL ===\n{freelance_info}\n\n=== MISSIONS DISPONIBLES ===\n{jobs_prompt_text}"

        headers = {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}", "Content-Type": "application/json"}
        data = {"model": "anthropic/claude-3-haiku", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            if response.status_code != 200:
                return Response({"error": "Erreur IA", "details": response.text}, status=500)

            result = response.json()
            analysis_text = result['choices'][0]['message']['content']

            try:
                clean_text = analysis_text.strip().strip("```json").strip("```").strip()
                dashboard_data = json.loads(clean_text)
                for match in dashboard_data:
                    if match.get('job_id'):
                        match['job_link'] = f"http://localhost:8000/job-offers/{match['job_id']}/"
            except json.JSONDecodeError:
                dashboard_data = {"analyse_brute": analysis_text}

            return Response({"dashboard": dashboard_data})

        except requests.exceptions.RequestException as e:
            return Response({"error": "Problème réseau", "details": str(e)}, status=500)


class CompanyDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'COMPANY':
            raise PermissionDenied("Seules les entreprises ont accès à ce dashboard.")

        company = user.company_profile
        my_offers = JobOffer.objects.filter(offer_company=company, offer_is_active=True)
        dashboard_results = []

        for offer in my_offers:
            potential_candidates = FreeLanceProfile.objects.filter(
                freelance_sectors=offer.offer_sector,
                freelance_is_active=True
            ).distinct()[:3]

            if not potential_candidates:
                continue

            candidates_data = ""
            for f in potential_candidates:
                skills = ", ".join([str(s) for s in f.skill_levels.all()])
                candidates_data += f"\n--- CANDIDAT ID {f.id} ---\nLocalisation: {f.freelance_location}\nCompétences: {skills}\n"

            system_prompt = (
                "Tu es un assistant de recrutement. Compare cette offre avec les candidats suivants. "
                "Donne un score sur 100 et une explication courte pour chaque candidat. "
                "Réponds STRICTEMENT en JSON : [{\"freelance_id\": 1, \"score\": 80, \"explication\": \"...\"}]"
            )
            user_prompt = f"=== OFFRE : {offer.offer_title} ===\n{offer.offer_description}\n\n=== CANDIDATS ===\n{candidates_data}"

            headers = {"Authorization": f"Bearer {settings.OPENROUTER_API_KEY}", "Content-Type": "application/json"}
            data = {"model": "anthropic/claude-3-haiku", "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]}

            try:
                response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
                if response.status_code == 200:
                    raw_content = response.json()['choices'][0]['message']['content']
                    clean_text = raw_content.strip().strip("```json").strip("```").strip()
                    matches = json.loads(clean_text)
                    for m in matches:
                        m['profile_link'] = f"http://localhost:8000/freelance-profiles/{m['freelance_id']}/"
                        try:
                            profil_trouve = FreeLanceProfile.objects.get(id=m['freelance_id'])
                            m['first_name'] = profil_trouve.first_name
                            m['last_name'] = profil_trouve.last_name
                        except:
                            m['first_name'] = "Candidat"
                            m['last_name'] = ""
                    dashboard_results.append({"job_title": offer.offer_title, "job_id": offer.id, "top_matches": matches})
            except:
                continue

        return Response({"company_dashboard": dashboard_results})

class HardSkillsViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = HardSkills.objects.all()
    serializer_class = HardSkillSerializer
    permission_classes = [IsAuthenticated]


class CompanyApplicationsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # On identifie l'entreprise
            company = request.user.company_profile
            # On cherche ses candidatures
            applications = JobApplication.objects.filter(job_offer__offer_company=company).order_by('-applied_at')

            # On utilise le NOUVEAU sérialiseur "riche"
            serializer = CompanyJobApplicationSerializer(applications, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": "Profil entreprise introuvable."}, status=404)


class UpdateApplicationStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            application = JobApplication.objects.get(pk=pk, job_offer__offer_company=request.user.company_profile)
            new_status = request.data.get('status')

            if new_status in ['ACCEPTED', 'REJECTED']:
                application.status = new_status
                application.save()
                return Response({"message": "Statut mis à jour avec succès", "status": new_status})
            return Response({"error": "Statut invalide"}, status=400)
        except JobApplication.DoesNotExist:
            return Response({"error": "Candidature introuvable"}, status=404)


class GenerateRejectionMessageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.role != 'COMPANY':
            raise PermissionDenied("Seules les entreprises peuvent générer ce message.")

        freelance_name = request.data.get('freelance_name', 'le candidat')
        job_title = request.data.get('job_title', 'la mission')
        draft_message = request.data.get('draft_message', '').strip()  # On récupère le texte tapé !

        # Si le recruteur a déjà tapé un brouillon, l'IA le corrige et l'améliore
        if draft_message:
            system_prompt = (
                "Tu es un responsable RH très professionnel et bienveillant. "
                f"Voici un brouillon de refus écrit par un recruteur pour le candidat '{freelance_name}' concernant la mission '{job_title}'. "
                "Ton rôle est de corriger, reformuler et améliorer ce brouillon pour qu'il soit poli, "
                "empathique, sans fautes, et qu'il garde le vouvoiement. "
                "Renvoie uniquement le message final prêt à être envoyé, sans fioritures ni guillemets."
            )
            user_prompt = f"Brouillon à améliorer :\n{draft_message}"

        # Si la case est vide, l'IA crée un message par défaut
        else:
            system_prompt = (
                "Tu es un responsable RH respectueux et bienveillant. "
                "Rédige un court message (3 à 4 phrases maximum) pour informer un candidat "
                f"que sa candidature n'a pas été retenue pour la mission '{job_title}'. "
                "Le message doit s'adresser directement au candidat (vouvoiement), "
                "être professionnel, empathique et l'encourager pour la suite. "
                "Commence directement le message par 'Bonjour' suivi de son prénom, sans objet."
            )
            user_prompt = f"Prénom du candidat : {freelance_name}"

        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "anthropic/claude-3-haiku",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        }

        try:
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            generated_text = result['choices'][0]['message']['content']
            return Response({"generated_message": generated_text})
        except Exception as e:
            return Response({"error": "Erreur lors de la génération IA.", "details": str(e)}, status=500)


class ConversationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, other_user_id):
        # On récupère tous les messages entre moi et l'autre utilisateur
        messages = Message.objects.filter(
            Q(sender=request.user, receiver_id=other_user_id) |
            Q(sender_id=other_user_id, receiver=request.user)
        ).order_by('timestamp')

        # Optionnel : Marquer les messages reçus comme "lus"
        Message.objects.filter(sender_id=other_user_id, receiver=request.user, is_read=False).update(is_read=True)

        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)

    def post(self, request, other_user_id):
        # On envoie un message à l'autre utilisateur
        content = request.data.get('content')
        if not content:
            return Response({"error": "Le message ne peut pas être vide."}, status=400)

        message = Message.objects.create(
            sender=request.user,
            receiver_id=other_user_id,
            content=content
        )
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=201)

    def delete(self, request, other_user_id):
        Message.objects.filter(
            Q(sender=request.user, receiver_id=other_user_id) |
            Q(sender_id=other_user_id, receiver=request.user)
        ).delete()
        return Response({"message": "Conversation supprimée"}, status=204)


class NotificationCountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        # 1. On compte les messages non lus destinés à cet utilisateur
        unread_messages = Message.objects.filter(receiver=user, is_read=False).count()

        # 2. On compte les candidatures en attente (si c'est une entreprise)
        pending_applications = 0
        if user.role == 'COMPANY' and hasattr(user, 'company_profile'):
            pending_applications = JobApplication.objects.filter(
                job_offer__offer_company=user.company_profile,
                status='PENDING'
            ).count()

        return Response({
            "unread_messages": unread_messages,
            "pending_applications": pending_applications
        })


class ConversationListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        messages = Message.objects.filter(Q(sender=user) | Q(receiver=user)).order_by('-timestamp')

        conversations = {}
        for msg in messages:
            other_user = msg.receiver if msg.sender == user else msg.sender

            if other_user.id not in conversations:
                name = "Utilisateur"
                job_title = "Candidature"  # <-- Le nouveau champ !

                # Récupérer le nom et la mission
                if other_user.role == 'FREELANCE' and hasattr(other_user, 'freelance_profile'):
                    name = f"{other_user.freelance_profile.first_name or 'Candidat'} {other_user.freelance_profile.last_name or ''}".strip()
                    if user.role == 'COMPANY':
                        app = JobApplication.objects.filter(job_offer__offer_company__company_user=user,
                                                            freelance__freelance_user=other_user).first()
                        if app: job_title = app.job_offer.offer_title

                elif other_user.role == 'COMPANY' and hasattr(other_user, 'company_profile'):
                    name = other_user.company_profile.company_name or "Entreprise"
                    if user.role == 'FREELANCE':
                        app = JobApplication.objects.filter(freelance__freelance_user=user,
                                                            job_offer__offer_company__company_user=other_user).first()
                        if app: job_title = app.job_offer.offer_title

                conversations[other_user.id] = {
                    "other_user_id": other_user.id,
                    "name": name,
                    "job_title": job_title,  # <-- On l'envoie à React
                    "role": other_user.role,
                    "last_message": msg.content,
                    "timestamp": msg.timestamp,
                    "unread_count": 0
                }

            if msg.receiver == user and not msg.is_read:
                conversations[other_user.id]["unread_count"] += 1

        return Response(list(conversations.values()))