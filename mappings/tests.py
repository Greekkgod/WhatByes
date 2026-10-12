from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from .models import PatientDoctorMapping

User = get_user_model()


class MappingAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            name="Clinic Staff",
            email="staff@clinic.org",
            password="Password123!",
        )
        self.client.force_authenticate(user=self.user)

        self.patient = Patient.objects.create(
            name="Jane Miller",
            contact_number="12345678",
            created_by=self.user,
        )
        self.doctor1 = Doctor.objects.create(
            name="Dr. Stephen Strange",
            specialization="Neurosurgeon",
            contact_number="999888777",
        )
        self.doctor2 = Doctor.objects.create(
            name="Dr. Leonard McCoy",
            specialization="Chief Medical Officer",
            contact_number="888777666",
        )

    def test_assign_doctor_to_patient(self):
        url = reverse("mapping-list-create")
        payload = {
            "patient": self.patient.id,
            "doctor": self.doctor1.id,
            "notes": "Follow-up consultation scheduled.",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["data"]["patient_id"], self.patient.id)
        self.assertEqual(response.data["data"]["doctor_id"], self.doctor1.id)
        self.assertTrue(PatientDoctorMapping.objects.filter(patient=self.patient, doctor=self.doctor1).exists())

    def test_prevent_duplicate_mapping(self):
        # Create initial mapping
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)

        url = reverse("mapping-list-create")
        payload = {
            "patient": self.patient.id,
            "doctor": self.doctor1.id,
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

    def test_list_all_mappings(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor2)

        url = reverse("mapping-list-create")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)

    def test_get_doctors_assigned_to_specific_patient(self):
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor2)

        url = reverse("mapping-detail-or-patient", kwargs={"lookup_id": self.patient.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["assigned_doctors_count"], 2)
        self.assertEqual(response.data["patient_id"], self.patient.id)

    def test_get_doctors_non_existent_patient_returns_404(self):
        url = reverse("mapping-detail-or-patient", kwargs={"lookup_id": 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_mapping_removes_doctor_from_patient(self):
        mapping = PatientDoctorMapping.objects.create(patient=self.patient, doctor=self.doctor1)
        url = reverse("mapping-detail-or-patient", kwargs={"lookup_id": mapping.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(PatientDoctorMapping.objects.filter(id=mapping.id).exists())

    def test_delete_non_existent_mapping(self):
        url = reverse("mapping-detail-or-patient", kwargs={"lookup_id": 88888})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
