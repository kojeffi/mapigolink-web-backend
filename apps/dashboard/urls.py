from django.urls import path
from .views import (
    DashboardStatsView, PatientGrowthView,
    RecordActivityView, TopClinicsView, RecentActivityView
)

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard_stats'),
    path('patient-growth/', PatientGrowthView.as_view(), name='patient_growth'),
    path('record-activity/', RecordActivityView.as_view(), name='record_activity'),
    path('top-clinics/', TopClinicsView.as_view(), name='top_clinics'),
    path('recent-activity/', RecentActivityView.as_view(), name='recent_activity'),
]
