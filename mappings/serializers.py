from rest_framework import serializers
from .models import PatientDoctorMapping
from patients.models import Patient
from doctors.models import Doctor
from patients.serializers import PatientSerializer
from doctors.serializers import DoctorSerializer


class PatientDoctorMappingReadSerializer(serializers.ModelSerializer):
    """
    Detailed serializer representing a patient-doctor assignment,
    including embedded doctor and patient details.
    """
    patient_id = serializers.ReadOnlyField(source="patient.id")
    patient_name = serializers.ReadOnlyField(source="patient.name")
    doctor_id = serializers.ReadOnlyField(source="doctor.id")
    doctor_name = serializers.ReadOnlyField(source="doctor.name")
    doctor_specialization = serializers.ReadOnlyField(source="doctor.specialization")

    class Meta:
        model = PatientDoctorMapping
        fields = [
            "id",
            "patient_id",
            "patient_name",
            "doctor_id",
            "doctor_name",
            "doctor_specialization",
            "notes",
            "assigned_date",
            "created_at",
            "updated_at",
        ]


class PatientDoctorMappingCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to assign a doctor to a patient.
    Supports either 'patient' / 'doctor' or 'patient_id' / 'doctor_id'.
    """
    patient = serializers.PrimaryKeyRelatedField(
        queryset=Patient.objects.all(),
        required=False,
    )
    doctor = serializers.PrimaryKeyRelatedField(
        queryset=Doctor.objects.all(),
        required=False,
    )
    patient_id = serializers.IntegerField(required=False, write_only=True)
    doctor_id = serializers.IntegerField(required=False, write_only=True)
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    class Meta:
        model = PatientDoctorMapping
        fields = ["id", "patient", "doctor", "patient_id", "doctor_id", "notes"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        # Resolve patient
        patient = attrs.get("patient")
        patient_id = attrs.get("patient_id")
        if not patient and patient_id:
            try:
                patient = Patient.objects.get(id=patient_id)
                attrs["patient"] = patient
            except Patient.DoesNotExist:
                raise serializers.ValidationError({"patient_id": f"Patient with ID {patient_id} does not exist."})
        elif not patient:
            raise serializers.ValidationError({"patient": "Patient ID is required."})

        # Resolve doctor
        doctor = attrs.get("doctor")
        doctor_id = attrs.get("doctor_id")
        if not doctor and doctor_id:
            try:
                doctor = Doctor.objects.get(id=doctor_id)
                attrs["doctor"] = doctor
            except Doctor.DoesNotExist:
                raise serializers.ValidationError({"doctor_id": f"Doctor with ID {doctor_id} does not exist."})
        elif not doctor:
            raise serializers.ValidationError({"doctor": "Doctor ID is required."})

        # Check for duplicate assignment
        if PatientDoctorMapping.objects.filter(patient=attrs["patient"], doctor=attrs["doctor"]).exists():
            raise serializers.ValidationError(
                f"Doctor '{doctor.name}' is already assigned to Patient '{patient.name}'."
            )

        # Remove extra keys before create
        attrs.pop("patient_id", None)
        attrs.pop("doctor_id", None)

        return attrs
