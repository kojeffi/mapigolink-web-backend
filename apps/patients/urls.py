from django.urls import path
from .views import (
    PatientListCreateView, PatientDetailView, PatientByMapigoIDView,
    QRScanView, RegenerateQRView
)

urlpatterns = [
    path('', PatientListCreateView.as_view(), name='patient_list'),
    path('<uuid:id>/', PatientDetailView.as_view(), name='patient_detail'),
    path('qr/<str:mapigo_id>/', PatientByMapigoIDView.as_view(), name='patient_by_mapigo_id'),
    path('scan/', QRScanView.as_view(), name='qr_scan'),
    path('<uuid:id>/regenerate-qr/', RegenerateQRView.as_view(), name='regenerate_qr'),
]
