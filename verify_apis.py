import os
import django
import json

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "healthcare_project.settings")
django.setup()

from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

User = get_user_model()


def run_e2e_verification():
    print("=================================================================")
    print("🏥 HEALTHCARE BACKEND E2E API VERIFICATION TEST RUNNER")
    print("=================================================================\n")
    client = APIClient()

    # 1. AUTHENTICATION: REGISTER
    print("1. [AUTH] Registering a new doctor user...")
    reg_payload = {
        "name": "Dr. Strange",
        "email": "stephen.strange@multiverse.org",
        "password": "SanctumPassword123!",
    }
    # Clean previous if exists
    User.objects.filter(email=reg_payload["email"]).delete()

    res = client.post("/api/auth/register/", reg_payload, format="json")
    print(f"   Status: {res.status_code}")
    print(f"   Response: {json.dumps(res.data, indent=2)}")
    assert res.status_code == 201, "Registration failed"

    # 2. AUTHENTICATION: LOGIN
    print("\n2. [AUTH] Logging in to obtain JWT tokens...")
    login_payload = {
        "email": reg_payload["email"],
        "password": reg_payload["password"],
    }
    res = client.post("/api/auth/login/", login_payload, format="json")
    print(f"   Status: {res.status_code}")
    assert res.status_code == 200, "Login failed"
    access_token = res.data["data"]["tokens"]["access"]
    refresh_token = res.data["data"]["tokens"]["refresh"]
    print(f"   Access Token: {access_token[:25]}... (valid JWT)")
    print(f"   Refresh Token: {refresh_token[:25]}...")

    # Attach token to client headers
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

    # 3. AUTHENTICATION: CURRENT USER
    print("\n3. [AUTH] Checking GET /api/auth/me/...")
    res = client.get("/api/auth/me/")
    print(f"   Status: {res.status_code}, User: {res.data['data']['name']} ({res.data['data']['email']})")
    assert res.status_code == 200

    # 4. PATIENT MANAGEMENT: CREATE
    print("\n4. [PATIENTS] Creating a new patient...")
    patient_payload = {
        "name": "Peter Parker",
        "age": 22,
        "gender": "Male",
        "contact_number": "+1-212-555-0199",
        "email": "peter.parker@dailybugle.com",
        "address": "20 Ingram St, Queens, NY",
        "medical_history": "Spider bite, rapid cellular recovery, elevated heart rate.",
    }
    res = client.post("/api/patients/", patient_payload, format="json")
    print(f"   Status: {res.status_code}")
    assert res.status_code == 201, "Patient creation failed"
    patient_id = res.data["data"]["id"]
    print(f"   Created Patient ID: {patient_id}, Name: {res.data['data']['name']}")

    # 5. PATIENT MANAGEMENT: LIST
    print("\n5. [PATIENTS] Listing patients created by authenticated user...")
    res = client.get("/api/patients/")
    print(f"   Status: {res.status_code}, Total Count: {res.data['count']}")
    assert res.status_code == 200

    # 6. PATIENT MANAGEMENT: GET DETAIL
    print(f"\n6. [PATIENTS] Getting details of patient {patient_id}...")
    res = client.get(f"/api/patients/{patient_id}/")
    print(f"   Status: {res.status_code}, Name: {res.data['data']['name']}")
    assert res.status_code == 200

    # 7. PATIENT MANAGEMENT: UPDATE (PUT)
    print(f"\n7. [PATIENTS] Updating details of patient {patient_id} (PUT)...")
    update_payload = patient_payload.copy()
    update_payload["age"] = 23
    update_payload["medical_history"] = "Vitals fully stabilized. Excellent athletic condition."
    res = client.put(f"/api/patients/{patient_id}/", update_payload, format="json")
    print(f"   Status: {res.status_code}, Updated Age: {res.data['data']['age']}")
    assert res.status_code == 200 and res.data["data"]["age"] == 23

    # 8. DOCTOR MANAGEMENT: CREATE
    print("\n8. [DOCTORS] Adding a new doctor record...")
    doctor_payload = {
        "name": "Christine Palmer",
        "specialization": "Emergency Medicine & Surgery",
        "contact_number": "+1-212-555-0144",
        "email": "christine.palmer@metrogeneral.org",
        "years_of_experience": 11,
        "hospital_name": "Metro-General Hospital",
    }
    res = client.post("/api/doctors/", doctor_payload, format="json")
    print(f"   Status: {res.status_code}")
    assert res.status_code == 201, "Doctor creation failed"
    doctor_id = res.data["data"]["id"]
    print(f"   Created Doctor ID: {doctor_id}, Name: {res.data['data']['name']}")

    # 9. DOCTOR MANAGEMENT: LIST
    print("\n9. [DOCTORS] Listing all doctors...")
    res = client.get("/api/doctors/")
    print(f"   Status: {res.status_code}, Total Doctors: {res.data['count']}")
    assert res.status_code == 200

    # 10. DOCTOR MANAGEMENT: GET DETAIL
    print(f"\n10. [DOCTORS] Getting details of doctor {doctor_id}...")
    res = client.get(f"/api/doctors/{doctor_id}/")
    print(f"   Status: {res.status_code}, Specialization: {res.data['data']['specialization']}")
    assert res.status_code == 200

    # 11. DOCTOR MANAGEMENT: UPDATE
    print(f"\n11. [DOCTORS] Updating doctor {doctor_id}...")
    doc_update = doctor_payload.copy()
    doc_update["years_of_experience"] = 12
    res = client.put(f"/api/doctors/{doctor_id}/", doc_update, format="json")
    print(f"   Status: {res.status_code}, Experience: {res.data['data']['years_of_experience']}")
    assert res.status_code == 200 and res.data["data"]["years_of_experience"] == 12

    # 12. PATIENT-DOCTOR MAPPING: ASSIGN
    print("\n12. [MAPPINGS] Assigning doctor to patient (POST /api/mappings/)...")
    mapping_payload = {
        "patient": patient_id,
        "doctor": doctor_id,
        "notes": "Primary emergency medical oversight.",
    }
    res = client.post("/api/mappings/", mapping_payload, format="json")
    print(f"   Status: {res.status_code}")
    assert res.status_code == 201, "Mapping creation failed"
    mapping_id = res.data["data"]["id"]
    print(f"   Mapping Created: ID {mapping_id} (Patient {patient_id} <-> Doctor {doctor_id})")

    # 13. PATIENT-DOCTOR MAPPING: LIST ALL
    print("\n13. [MAPPINGS] Listing all patient-doctor mappings...")
    res = client.get("/api/mappings/")
    print(f"   Status: {res.status_code}, Total Mappings: {res.data['count']}")
    assert res.status_code == 200

    # 14. PATIENT-DOCTOR MAPPING: GET DOCTORS FOR SPECIFIC PATIENT
    print(f"\n14. [MAPPINGS] Getting all doctors assigned to patient {patient_id} (GET /api/mappings/{patient_id}/)...")
    res = client.get(f"/api/mappings/{patient_id}/")
    print(f"   Status: {res.status_code}, Assigned Doctors: {res.data['assigned_doctors_count']}")
    assert res.status_code == 200
    print(f"   Doctor Assigned: {res.data['data'][0]['doctor_name']} ({res.data['data'][0]['doctor_specialization']})")

    # 15. PATIENT-DOCTOR MAPPING: DELETE MAPPING
    print(f"\n15. [MAPPINGS] Removing doctor from patient (DELETE /api/mappings/{mapping_id}/)...")
    res = client.delete(f"/api/mappings/{mapping_id}/")
    print(f"   Status: {res.status_code}, Message: {res.data['message']}")
    assert res.status_code == 200

    # 16. PATIENT MANAGEMENT: DELETE PATIENT
    print(f"\n16. [PATIENTS] Deleting patient {patient_id} (DELETE /api/patients/{patient_id}/)...")
    res = client.delete(f"/api/patients/{patient_id}/")
    print(f"   Status: {res.status_code}, Message: {res.data['message']}")
    assert res.status_code == 200

    # 17. DOCTOR MANAGEMENT: DELETE DOCTOR
    print(f"\n17. [DOCTORS] Deleting doctor {doctor_id} (DELETE /api/doctors/{doctor_id}/)...")
    res = client.delete(f"/api/doctors/{doctor_id}/")
    print(f"   Status: {res.status_code}, Message: {res.data['message']}")
    assert res.status_code == 200

    # 18. SYSTEM HEALTH
    print("\n18. [SYSTEM] Checking health status (/api/health/)...")
    res = client.get("/api/health/")
    print(f"   Status: {res.status_code}, Health: {res.data['status']}, Database: {res.data['database']}")
    assert res.status_code == 200 and res.data["database"] == "ok"

    print("\n=================================================================")
    print("✨ ALL 18 ENDPOINT CHECKS EXECUTED & PASSED WITH 100% SUCCESS! ✨")
    print("=================================================================")


if __name__ == "__main__":
    run_e2e_verification()
