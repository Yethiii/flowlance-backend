from rest_framework import serializers
from .models import (
    User, Sector, SoftSkills, HardSkills,
    FreeLanceProfile, FreelanceSkill, CompanyProfile, JobOffer
)

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