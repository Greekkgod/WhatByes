from django.urls import path
from .views import MappingListCreateView, MappingDetailOrPatientView

urlpatterns = [
    path("", MappingListCreateView.as_view(), name="mapping-list-create"),
    path("<int:lookup_id>/", MappingDetailOrPatientView.as_view(), name="mapping-detail-or-patient"),
    path("patient/<int:lookup_id>/", MappingDetailOrPatientView.as_view(), name="mapping-patient-explicit"),
]
