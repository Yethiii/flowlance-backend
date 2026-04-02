from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import JobApplication, JobOffer, Message, Sector


User = get_user_model()


class ApiBusinessRulesTests(APITestCase):
    def _create_user(self, email, role):
        return User.objects.create_user(
            email=email,
            password="StrongPassword123!",
            role=role,
        )

    def test_register_rejects_duplicate_email(self):
        url = reverse("register")
        payload = {
            "email": "dup@example.com",
            "password": "StrongPassword123!",
            "role": "FREELANCE",
        }

        first_response = self.client.post(url, payload, format="json")
        second_response = self.client.post(url, payload, format="json")

        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.filter(email="dup@example.com").count(), 1)

    def test_freelance_cannot_create_company_job_offer(self):
        freelance = self._create_user("freelance@example.com", "FREELANCE")
        sector = Sector.objects.create(name="IT")
        self.client.force_authenticate(user=freelance)

        response = self.client.post(
            reverse("joboffer-list"),
            {
                "offer_title": "Backend Developer",
                "offer_description": "API work",
                "offer_location": "Brussels",
                "offer_sector": sector.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(JobOffer.objects.count(), 0)

    def test_message_is_persisted_when_sent(self):
        sender = self._create_user("sender@example.com", "FREELANCE")
        receiver = self._create_user("receiver@example.com", "COMPANY")
        self.client.force_authenticate(user=sender)

        response = self.client.post(
            reverse("conversation", kwargs={"other_user_id": receiver.id}),
            {"content": "Bonjour, je suis intéressé par votre mission."},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Message.objects.count(), 1)

        message = Message.objects.first()
        self.assertEqual(message.sender, sender)
        self.assertEqual(message.receiver, receiver)
        self.assertEqual(message.content, "Bonjour, je suis intéressé par votre mission.")

    def test_inactive_company_cannot_publish_job_offer(self):
        company_user = self._create_user("company@example.com", "COMPANY")
        sector = Sector.objects.create(name="Construction")
        self.client.force_authenticate(user=company_user)

        response = self.client.post(
            reverse("joboffer-list"),
            {
                "offer_title": "Chef de projet",
                "offer_description": "Pilotage de chantiers",
                "offer_location": "Liège",
                "offer_sector": sector.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(JobOffer.objects.count(), 0)

    def test_company_cannot_apply_to_job_offer(self):
        owner_company_user = self._create_user("owner@example.com", "COMPANY")
        sector = Sector.objects.create(name="Finance")
        offer = JobOffer.objects.create(
            offer_company=owner_company_user.company_profile,
            offer_title="Data Analyst",
            offer_description="Analyse financière",
            offer_location="Namur",
            offer_sector=sector,
        )

        company_requester = self._create_user("other-company@example.com", "COMPANY")
        self.client.force_authenticate(user=company_requester)

        response = self.client.post(
            reverse("application-list"),
            {"job_offer": offer.id, "cover_message": "Nous souhaitons candidater"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(JobApplication.objects.count(), 0)
