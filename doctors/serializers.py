from rest_framework import serializers
from .models import Doctor


class DoctorSerializer(serializers.ModelSerializer):
    created_by_name = serializers.ReadOnlyField(source="created_by.name")

    class Meta:
        model = Doctor
        fields = [
            "id",
            "name",
            "specialization",
            "contact_number",
            "email",
            "years_of_experience",
            "hospital_name",
            "created_by",
            "created_by_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_by", "created_by_name", "created_at", "updated_at"]

    def validate_name(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Doctor name cannot be empty.")
        return stripped

    def validate_specialization(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Specialization is required.")
        return stripped

    def validate_contact_number(self, value):
        stripped = value.strip()
        if not stripped:
            raise serializers.ValidationError("Contact number is required.")
        return stripped

    def validate_years_of_experience(self, value):
        if value < 0:
            raise serializers.ValidationError("Years of experience cannot be negative.")
        return value
