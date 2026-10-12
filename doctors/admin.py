from django.contrib import admin
from .models import Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "specialization", "contact_number", "years_of_experience", "hospital_name", "created_at")
    list_filter = ("specialization", "created_at")
    search_fields = ("name", "specialization", "contact_number")
    ordering = ("-created_at",)
