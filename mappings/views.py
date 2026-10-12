from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import PatientDoctorMapping
from .serializers import (
    PatientDoctorMappingReadSerializer,
    PatientDoctorMappingCreateSerializer,
)
from patients.models import Patient
from doctors.models import Doctor


class MappingListCreateView(APIView):
    """
    Mapping List & Assignment Endpoint.
    - POST /api/mappings/ : Assign a doctor to a patient
    - GET  /api/mappings/ : Retrieve all patient-doctor mappings
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List All Patient-Doctor Mappings",
        description="Retrieve all patient-doctor mappings. Supports optional query filters: ?patient_id=<id> or ?doctor_id=<id>.",
        responses={200: PatientDoctorMappingReadSerializer(many=True)},
    )
    def get(self, request):
        mappings = PatientDoctorMapping.objects.select_related("patient", "doctor").all()

        patient_id = request.query_params.get("patient_id")
        if patient_id:
            mappings = mappings.filter(patient_id=patient_id)

        doctor_id = request.query_params.get("doctor_id")
        if doctor_id:
            mappings = mappings.filter(doctor_id=doctor_id)

        serializer = PatientDoctorMappingReadSerializer(mappings, many=True)
        return Response(
            {
                "success": True,
                "count": mappings.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Assign Doctor to Patient",
        description="Creates a mapping assigning a doctor to a specific patient.",
        request=PatientDoctorMappingCreateSerializer,
        responses={
            201: PatientDoctorMappingReadSerializer,
            400: OpenApiResponse(description="Validation error or duplicate mapping"),
        },
    )
    def post(self, request):
        serializer = PatientDoctorMappingCreateSerializer(data=request.data)
        if serializer.is_valid():
            mapping = serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Doctor assigned to patient successfully.",
                    "data": PatientDoctorMappingReadSerializer(mapping).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Failed to assign doctor to patient.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class MappingDetailOrPatientView(APIView):
    """
    Dual Endpoint handling:
    - GET /api/mappings/<patient_id>/ : Get all doctors assigned to a specific patient.
    - DELETE /api/mappings/<id>/       : Remove a doctor from a patient (by mapping id).
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Doctors Assigned to Patient",
        description="Retrieve all doctors assigned to a specific patient by patient ID.",
        responses={
            200: PatientDoctorMappingReadSerializer(many=True),
            404: OpenApiResponse(description="Patient not found"),
        },
    )
    def get(self, request, lookup_id):
        patient = get_object_or_404(Patient, pk=lookup_id)
        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related("doctor", "patient")
        serializer = PatientDoctorMappingReadSerializer(mappings, many=True)
        return Response(
            {
                "success": True,
                "patient_id": patient.id,
                "patient_name": patient.name,
                "assigned_doctors_count": mappings.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Remove Doctor Assignment (Delete Mapping)",
        description="Delete a patient-doctor mapping record by mapping ID.",
        responses={
            200: OpenApiResponse(description="Doctor assignment removed successfully"),
            404: OpenApiResponse(description="Mapping not found"),
        },
    )
    def delete(self, request, lookup_id):
        # First attempt deleting mapping by mapping ID
        try:
            mapping = PatientDoctorMapping.objects.get(pk=lookup_id)
            mapping_id = mapping.id
            mapping.delete()
            return Response(
                {
                    "success": True,
                    "message": f"Doctor assignment mapping #{mapping_id} removed successfully.",
                },
                status=status.HTTP_200_OK,
            )
        except PatientDoctorMapping.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "error": {
                        "message": f"Mapping with ID {lookup_id} not found.",
                        "details": "No patient-doctor mapping exists with this ID.",
                    },
                },
                status=status.HTTP_404_NOT_FOUND,
            )
