from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Doctor

User = get_user_model()


class DoctorAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="Admin Doc",
            email="admin@hospital.org",
            password="Password123!",
        )
        self.client.force_authenticate(user=self.user)

        self.doctor_data = {
            "name": "Gregory House",
            "specialization": "Diagnostic Medicine",
            "contact_number": "+1987654321",
            "email": "house@princetonplainsboro.edu",
            "years_of_experience": 20,
            "hospital_name": "Princeton-Plainsboro Teaching Hospital",
        }

    def test_create_doctor_authenticated(self):
        url = reverse("doctor-list-create")
        response = self.client.post(url, self.doctor_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "Gregory House")

    def test_create_doctor_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("doctor-list-create")
        response = self.client.post(url, self.doctor_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_all_doctors(self):
        Doctor.objects.create(
            name="Doctor A",
            specialization="Cardiology",
            contact_number="111",
        )
        Doctor.objects.create(
            name="Doctor B",
            specialization="Neurology",
            contact_number="222",
        )
        url = reverse("doctor-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_doctor_details(self):
        doc = Doctor.objects.create(
            name="Doctor Lisa Cuddy",
            specialization="Endocrinology",
            contact_number="333",
        )
        url = reverse("doctor-detail", kwargs={"pk": doc.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Doctor Lisa Cuddy")

    def test_update_doctor(self):
        doc = Doctor.objects.create(
            name="Dr. Eric Foreman",
            specialization="Neurology",
            contact_number="444",
        )
        url = reverse("doctor-detail", kwargs={"pk": doc.id})
        update_data = {
            "name": "Dr. Eric Foreman",
            "specialization": "Dean of Medicine",
            "contact_number": "444-999",
            "years_of_experience": 15,
        }
        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["specialization"], "Dean of Medicine")

    def test_delete_doctor(self):
        doc = Doctor.objects.create(
            name="Dr. Robert Chase",
            specialization="Surgeon",
            contact_number="555",
        )
        url = reverse("doctor-detail", kwargs={"pk": doc.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Doctor.objects.filter(id=doc.id).exists())
