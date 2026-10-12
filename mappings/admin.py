from django.contrib import admin
from .models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "assigned_date", "created_at")
    list_filter = ("assigned_date", "created_at")
    search_fields = ("patient__name", "doctor__name")
    ordering = ("-created_at",)
