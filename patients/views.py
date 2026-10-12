from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Patient
from .serializers import PatientSerializer


class PatientListCreateView(APIView):
    """
    Patient List & Creation Endpoint.
    - POST /api/patients/ : Add a new patient (Authenticated users only)
    - GET /api/patients/  : Retrieve all patients created by the authenticated user
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List User Patients",
        description="Retrieve all patients created by the authenticated user.",
        responses={200: PatientSerializer(many=True)},
    )
    def get(self, request):
        patients = Patient.objects.filter(created_by=request.user)
        serializer = PatientSerializer(patients, many=True)
        return Response(
            {
                "success": True,
                "count": patients.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Create Patient",
        description="Add a new patient record assigned to the authenticated user.",
        request=PatientSerializer,
        responses={
            201: PatientSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = PatientSerializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save(created_by=request.user)
            return Response(
                {
                    "success": True,
                    "message": "Patient record created successfully.",
                    "data": PatientSerializer(patient).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Patient creation failed.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class PatientDetailView(APIView):
    """
    Patient Detail, Update, and Deletion Endpoint.
    - GET /api/patients/<id>/    : Get details of a specific patient
    - PUT /api/patients/<id>/    : Update patient details
    - PATCH /api/patients/<id>/  : Partial update of patient details
    - DELETE /api/patients/<id>/ : Delete a patient record
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        # Only allows access to patient records created by the authenticated user (or superuser)
        if user.is_staff or user.is_superuser:
            return get_object_or_404(Patient, pk=pk)
        return get_object_or_404(Patient, pk=pk, created_by=user)

    @extend_schema(
        summary="Get Patient Details",
        description="Retrieve details of a specific patient created by the authenticated user.",
        responses={200: PatientSerializer, 404: OpenApiResponse(description="Patient not found")},
    )
    def get(self, request, pk):
        patient = self.get_object(pk, request.user)
        serializer = PatientSerializer(patient)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update Patient",
        description="Update all or specific fields of an existing patient record.",
        request=PatientSerializer,
        responses={
            200: PatientSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Patient not found"),
        },
    )
    def put(self, request, pk):
        patient = self.get_object(pk, request.user)
        serializer = PatientSerializer(patient, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Patient updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Patient update failed.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Partial Update Patient",
        description="Partially update an existing patient record.",
        request=PatientSerializer,
        responses={200: PatientSerializer},
    )
    def patch(self, request, pk):
        patient = self.get_object(pk, request.user)
        serializer = PatientSerializer(patient, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Patient partially updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Patient update failed.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Delete Patient",
        description="Delete a patient record permanently.",
        responses={
            200: OpenApiResponse(description="Patient deleted successfully"),
            404: OpenApiResponse(description="Patient not found"),
        },
    )
    def delete(self, request, pk):
        patient = self.get_object(pk, request.user)
        patient_id = patient.id
        patient.delete()
        return Response(
            {
                "success": True,
                "message": f"Patient with ID {patient_id} deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
