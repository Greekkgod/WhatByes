from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from patients.models import Patient
from doctors.models import Doctor
from mappings.models import PatientDoctorMapping

User = get_user_model()


class Command(BaseCommand):
    help = "Seeds initial demo data (users, doctors, patients, mappings) for testing."

    def handle(self, *args, **options):
        self.stdout.write("Seeding sample healthcare data...")

        # Create demo user
        admin_user, created = User.objects.get_or_create(
            email="admin@healthcare.com",
            defaults={
                "name": "Healthcare Administrator",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("AdminPass123!")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("Created admin user: admin@healthcare.com / AdminPass123!"))

        staff_user, created = User.objects.get_or_create(
            email="staff@healthcare.com",
            defaults={"name": "Medical Officer John"},
        )
        if created:
            staff_user.set_password("StaffPass123!")
            staff_user.save()
            self.stdout.write(self.style.SUCCESS("Created staff user: staff@healthcare.com / StaffPass123!"))

        # Create Doctors
        doctors_data = [
            {
                "name": "Sarah Connor",
                "specialization": "Cardiology",
                "contact_number": "+1-555-0101",
                "email": "sarah.connor@hospital.com",
                "years_of_experience": 12,
                "hospital_name": "City Heart Institute",
            },
            {
                "name": "Gregory House",
                "specialization": "Diagnostic Medicine",
                "contact_number": "+1-555-0102",
                "email": "house@plainsboro.edu",
                "years_of_experience": 22,
                "hospital_name": "Princeton Plainsboro",
            },
            {
                "name": "Meredith Grey",
                "specialization": "General Surgery",
                "contact_number": "+1-555-0103",
                "email": "meredith.grey@grey-sloan.com",
                "years_of_experience": 14,
                "hospital_name": "Grey Sloan Memorial Hospital",
            },
        ]

        doctors = []
        for d_data in doctors_data:
            doc, _ = Doctor.objects.get_or_create(
                name=d_data["name"],
                defaults={**d_data, "created_by": staff_user},
            )
            doctors.append(doc)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(doctors)} doctors."))

        # Create Patients
        patients_data = [
            {
                "name": "Arthur Dent",
                "age": 42,
                "gender": "Male",
                "contact_number": "+1-555-0201",
                "email": "arthur@galaxy.org",
                "address": "42 West Country, Cottington",
                "medical_history": "Mild hypertension, anxiety, panic episodes.",
            },
            {
                "name": "Ellen Ripley",
                "age": 30,
                "gender": "Female",
                "contact_number": "+1-555-0202",
                "email": "ripley@weyland.com",
                "address": "Nostromo Deck B, Sector 4",
                "medical_history": "Respiratory recovery, post-traumatic stress.",
            },
        ]

        patients = []
        for p_data in patients_data:
            pat, _ = Patient.objects.get_or_create(
                name=p_data["name"],
                defaults={**p_data, "created_by": staff_user},
            )
            patients.append(pat)
        self.stdout.write(self.style.SUCCESS(f"Seeded {len(patients)} patients."))

        # Create Mappings
        if len(patients) >= 2 and len(doctors) >= 2:
            m1, _ = PatientDoctorMapping.objects.get_or_create(
                patient=patients[0],
                doctor=doctors[0],
                defaults={"notes": "Regular cardiology consultation and ECG check."},
            )
            m2, _ = PatientDoctorMapping.objects.get_or_create(
                patient=patients[0],
                doctor=doctors[1],
                defaults={"notes": "Diagnostic second opinion on panic symptoms."},
            )
            m3, _ = PatientDoctorMapping.objects.get_or_create(
                patient=patients[1],
                doctor=doctors[2],
                defaults={"notes": "Surgical post-op routine assessment."},
            )
            self.stdout.write(self.style.SUCCESS("Seeded 3 patient-doctor mappings."))

        self.stdout.write(self.style.SUCCESS("Data seeding completed successfully!"))
