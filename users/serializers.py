from rest_framework import serializers
from .models import (
    User, Sector, SoftSkills, HardSkills,
    FreeLanceProfile, FreelanceSkill, CompanyProfile, JobOffer, JobApplication,
    Education, Language, Certification, License
)
from django.contrib.auth import get_user_model

User = get_user_model()


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


class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = '__all__'


class CertificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certification
        fields = '__all__'


class LicenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = License
        fields = '__all__'


class FreelanceSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.ReadOnlyField(source='skill.name')
    sector_name = serializers.ReadOnlyField(source='skill.sector.name')
    skill = serializers.SlugRelatedField(slug_field='name', queryset=HardSkills.objects.all())
    sector_id = serializers.IntegerField(write_only=True, required=False)

    class Meta:
        model = FreelanceSkill
        fields = ['id', 'skill', 'skill_name', 'sector_name', 'level', 'sector_id']

    def to_internal_value(self, data):
        skill_name = data.get('skill')
        sector_id = data.get('sector_id')
        if skill_name:
            skill_obj, _ = HardSkills.objects.get_or_create(name=skill_name, defaults={'sector_id': sector_id})
            data['skill'] = skill_obj.name
        return super().to_internal_value(data)


class FreeLanceProfileSerializer(serializers.ModelSerializer):
    skill_levels = FreelanceSkillSerializer(many=True, read_only=True)
    educations = EducationSerializer(many=True, read_only=True, source='education_set')
    languages = LanguageSerializer(many=True, read_only=True, source='language_set')
    certifications = CertificationSerializer(many=True, read_only=True, source='certification_set')
    licenses = LicenseSerializer(many=True, read_only=True)

    username = serializers.ReadOnlyField(source='freelance_user.email')

    class Meta:
        model = FreeLanceProfile
        fields = '__all__'


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