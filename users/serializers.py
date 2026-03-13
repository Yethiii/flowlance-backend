from rest_framework import serializers
from .models import (
    User, Sector, SoftSkills, HardSkills,
    FreeLanceProfile, FreelanceSkill, CompanyProfile, JobOffer, JobApplication, Education
)
from django.contrib.auth import get_user_model

User = get_user_model()


# --- 1. SERIALIZERS DE BASE (Outils) ---

class SectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sector
        fields = ['id', 'name']


class SoftSkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = SoftSkills
        fields = ['id', 'name']


class HardSkillSerializer(serializers.ModelSerializer):
    sector_name = serializers.ReadOnlyField(source='sector.name')

    class Meta:
        model = HardSkills
        fields = ['id', 'name', 'sector_name']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


# --- 2. SERIALIZERS COMPLEXES (Relations) ---

class FreelanceSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.ReadOnlyField(source='skill.name')
    skill = serializers.SlugRelatedField(
        slug_field='name',
        queryset=HardSkills.objects.all()
    )

    class Meta:
        model = FreelanceSkill
        fields = ['id', 'skill', 'skill_name', 'level']

    def to_internal_value(self, data):
        skill_name = data.get('skill')
        if skill_name:
            # On crée le HardSkill s'il n'existe pas déjà
            HardSkills.objects.get_or_create(name=skill_name)
        return super().to_internal_value(data)


class FreeLanceProfileSerializer(serializers.ModelSerializer):
    skill_levels = FreelanceSkillSerializer(many=True, read_only=True)
    # Déplacé ici car EducationSerializer est maintenant défini plus haut
    educations = EducationSerializer(many=True, read_only=True, source='education_set')
    username = serializers.ReadOnlyField(source='freelance_user.email')

    class Meta:
        model = FreeLanceProfile
        fields = '__all__'


# --- 3. ENTREPRISE & OFFRES ---

class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyProfile
        fields = '__all__'


class JobOfferSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='offer_company.company_name')

    class Meta:
        model = JobOffer
        fields = '__all__'
        read_only_fields = ('offer_company', 'offer_created_at', 'offer_is_active')


class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = ['id', 'job_offer', 'freelance', 'status', 'cover_message', 'applied_at']
        read_only_fields = ['id', 'freelance', 'status', 'applied_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['freelance'] = user.freelance_profile
        return super().create(validated_data)


# --- 4. AUTHENTIFICATION ---

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    PUBLIC_ROLES = (('FREELANCE', 'Freelance'), ('COMPANY', 'Entreprise'))
    role = serializers.ChoiceField(choices=PUBLIC_ROLES, default='FREELANCE')

    class Meta:
        model = User
        fields = ['email', 'password', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'FREELANCE')
        )
        return user