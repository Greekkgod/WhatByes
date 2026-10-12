from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Patient

User = get_user_model()


class PatientAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            name="Doctor User 1",
            email="doc1@hospital.com",
            password="Password123!",
        )
        self.user2 = User.objects.create_user(
            name="Doctor User 2",
            email="doc2@hospital.com",
            password="Password123!",
        )
        self.client.force_authenticate(user=self.user1)

        self.patient_data = {
            "name": "John Doe",
            "age": 35,
            "gender": "Male",
            "contact_number": "+1234567890",
            "email": "johndoe@example.com",
            "address": "123 Health Ave, Medical City",
            "medical_history": "Mild hypertension, penicillin allergy.",
        }

    def test_create_patient_authenticated(self):
        url = reverse("patient-list-create")
        response = self.client.post(url, self.patient_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["name"], "John Doe")
        self.assertEqual(response.data["data"]["created_by"], self.user1.id)

    def test_create_patient_unauthenticated(self):
        self.client.force_authenticate(user=None)
        url = reverse("patient-list-create")
        response = self.client.post(url, self.patient_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_patients_scoped_to_authenticated_user(self):
        # Create patient for user1
        Patient.objects.create(
            name="Patient of User 1",
            contact_number="11111",
            created_by=self.user1,
        )
        # Create patient for user2
        Patient.objects.create(
            name="Patient of User 2",
            contact_number="22222",
            created_by=self.user2,
        )

        url = reverse("patient-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["data"][0]["name"], "Patient of User 1")

    def test_get_patient_details(self):
        patient = Patient.objects.create(
            name="Patient Alice",
            contact_number="55555",
            created_by=self.user1,
        )
        url = reverse("patient-detail", kwargs={"pk": patient.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "Patient Alice")

    def test_get_other_user_patient_forbidden_or_404(self):
        patient_other = Patient.objects.create(
            name="Other User Patient",
            contact_number="99999",
            created_by=self.user2,
        )
        url = reverse("patient-detail", kwargs={"pk": patient_other.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_patient(self):
        patient = Patient.objects.create(
            name="Old Name",
            contact_number="12345",
            created_by=self.user1,
        )
        url = reverse("patient-detail", kwargs={"pk": patient.id})
        update_data = {
            "name": "New Updated Name",
            "contact_number": "9876543210",
            "gender": "Female",
            "age": 28,
        }
        response = self.client.put(url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["data"]["name"], "New Updated Name")
        patient.refresh_from_db()
        self.assertEqual(patient.name, "New Updated Name")

    def test_delete_patient(self):
        patient = Patient.objects.create(
            name="Patient To Delete",
            contact_number="12345",
            created_by=self.user1,
        )
        url = reverse("patient-detail", kwargs={"pk": patient.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Patient.objects.filter(id=patient.id).exists())
