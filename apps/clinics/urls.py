from django.urls import path
from .views import ClinicListCreateView, ClinicDetailView, VerifyClinicView, ClinicStaffListView

urlpatterns = [
    path('', ClinicListCreateView.as_view(), name='clinic_list'),
    path('<uuid:id>/', ClinicDetailView.as_view(), name='clinic_detail'),
    path('<uuid:id>/verify/', VerifyClinicView.as_view(), name='clinic_verify'),
    path('<uuid:clinic_id>/staff/', ClinicStaffListView.as_view(), name='clinic_staff'),
]
