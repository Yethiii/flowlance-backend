from rest_framework import serializers
from .models import (
    User, Sector, SoftSkills, HardSkills,
    FreeLanceProfile, FreelanceSkill, CompanyProfile, JobOffer
)
from django.contrib.auth import get_user_model

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            role=validated_data.get('role', 'FREELANCE')
        )
        return user

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


class FreelanceSkillSerializer(serializers.ModelSerializer):
    skill_details = HardSkillSerializer(source='skill', read_only=True)

    class Meta:
        model = FreelanceSkill
        fields = ['id', 'skill', 'skill_details', 'level']


class FreeLanceProfileSerializer(serializers.ModelSerializer):
    skill_levels = FreelanceSkillSerializer(many=True, read_only=True)
    username = serializers.ReadOnlyField(source='freelance_user.username')

    class Meta:
        model = FreeLanceProfile
        fields = [
            'id', 'username', 'freelance_location', 'freelance_availability',
            'freelance_full_remote', 'skill_levels', 'freelance_soft_skills'
        ]


class JobOfferSerializer(serializers.ModelSerializer):
    company_name = serializers.ReadOnlyField(source='offer_company.company_name')

    class Meta:
        model = JobOffer
        fields = [
            'id', 'offer_company', 'company_name', 'offer_title',
            'offer_location', 'offer_description', 'offer_hardskills', 'offer_softskills'
        ]