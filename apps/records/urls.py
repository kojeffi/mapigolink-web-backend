from django.urls import path
from .views import (
    MedicalRecordListCreateView, MedicalRecordDetailView,
    PatientRecordsView, AttachmentUploadView,
    PrescriptionListCreateView, AccessLogListView
)

urlpatterns = [
    path('', MedicalRecordListCreateView.as_view(), name='record_list'),
    path('<uuid:id>/', MedicalRecordDetailView.as_view(), name='record_detail'),
    path('patient/<uuid:patient_id>/', PatientRecordsView.as_view(), name='patient_records'),
    path('<uuid:record_id>/prescriptions/', PrescriptionListCreateView.as_view(), name='prescriptions'),
    path('attachments/upload/', AttachmentUploadView.as_view(), name='attachment_upload'),
    path('access-logs/', AccessLogListView.as_view(), name='access_logs'),
]
