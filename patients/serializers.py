from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.name")
    created_by_email = serializers.ReadOnlyField(source="created_by.email")

    class Meta:
        model = Patient
        fields = [
            "id",
            "name",
            "age",
            "date_of_birth",
            "gender",
            "contact_number",
            "email",
            "address",
            "medical_history",
            "created_by",
            "created_by_name",
            "created_by_email",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_by",
            "created_by_name",
            "created_by_email",
            "created_at",
            "updated_at",
        ]

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Patient name cannot be empty.")
        return stripped

    def validate_contact_number(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Contact number is required.")
        return stripped

    def validate_age(self, value):
        if value is not None and (value < 0 or value > 150):
            raise serializers.ValidationError("Age must be between 0 and 150.")
        return value
