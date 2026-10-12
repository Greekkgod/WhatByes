from django.db import models
from patients.models import Patient
from doctors.models import Doctor


class PatientDoctorMapping(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="doctor_mappings",
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="patient_mappings",
    )
    notes = models.TextField(blank=True, default="")
    assigned_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Patient Doctor Mapping"
        verbose_name_plural = "Patient Doctor Mappings"
        unique_together = ("patient", "doctor")

    def __str__(self):
        return f"Mapping #{self.id}: Patient {self.patient.name} -> Dr. {self.doctor.name}"
