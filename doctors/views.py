from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .models import Doctor
from .serializers import DoctorSerializer


class DoctorListCreateView(APIView):
    """
    Doctor List & Creation Endpoint.
    - POST /api/doctors/ : Add a new doctor (Authenticated users only)
    - GET /api/doctors/  : Retrieve all doctors
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="List All Doctors",
        description="Retrieve all registered doctors in the system.",
        responses={200: DoctorSerializer(many=True)},
    )
    def get(self, request):
        doctors = Doctor.objects.all()
        # Optional filter by specialization or search query
        specialization = request.query_params.get("specialization")
        if specialization:
            doctors = doctors.filter(specialization__icontains=specialization)
        search = request.query_params.get("search")
        if search:
            doctors = doctors.filter(name__icontains=search)

        serializer = DoctorSerializer(doctors, many=True)
        return Response(
            {
                "success": True,
                "count": doctors.count(),
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Create Doctor Record",
        description="Add a new doctor to the system.",
        request=DoctorSerializer,
        responses={
            201: DoctorSerializer,
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = DoctorSerializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save(created_by=request.user)
            return Response(
                {
                    "success": True,
                    "message": "Doctor record created successfully.",
                    "data": DoctorSerializer(doctor).data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Doctor creation failed.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class DoctorDetailView(APIView):
    """
    Doctor Detail, Update, and Deletion Endpoint.
    - GET /api/doctors/<id>/    : Get details of a specific doctor
    - PUT /api/doctors/<id>/    : Update doctor details
    - PATCH /api/doctors/<id>/  : Partial update of doctor details
    - DELETE /api/doctors/<id>/ : Delete a doctor record
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(Doctor, pk=pk)

    @extend_schema(
        summary="Get Doctor Details",
        description="Retrieve details of a specific doctor by ID.",
        responses={200: DoctorSerializer, 404: OpenApiResponse(description="Doctor not found")},
    )
    def get(self, request, pk):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(doctor)
        return Response(
            {
                "success": True,
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Update Doctor",
        description="Update details of an existing doctor.",
        request=DoctorSerializer,
        responses={
            200: DoctorSerializer,
            400: OpenApiResponse(description="Validation error"),
            404: OpenApiResponse(description="Doctor not found"),
        },
    )
    def put(self, request, pk):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(doctor, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Doctor updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Doctor update failed.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Partial Update Doctor",
        description="Partially update fields of an existing doctor.",
        request=DoctorSerializer,
        responses={200: DoctorSerializer},
    )
    def patch(self, request, pk):
        doctor = self.get_object(pk)
        serializer = DoctorSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Doctor partially updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Doctor update failed.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    @extend_schema(
        summary="Delete Doctor",
        description="Delete a doctor record permanently.",
        responses={
            200: OpenApiResponse(description="Doctor deleted successfully"),
            404: OpenApiResponse(description="Doctor not found"),
        },
    )
    def delete(self, request, pk):
        doctor = self.get_object(pk)
        doctor_id = doctor.id
        doctor.delete()
        return Response(
            {
                "success": True,
                "message": f"Doctor with ID {doctor_id} deleted successfully.",
            },
            status=status.HTTP_200_OK,
        )
