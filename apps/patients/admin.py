from django.contrib import admin
from .models import Patient, PatientConsent


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ['mapigo_id', 'full_name', 'date_of_birth', 'gender', 'blood_group', 'country', 'status', 'created_at']
    list_filter = ['gender', 'blood_group', 'country', 'status']
    search_fields = ['first_name', 'last_name', 'mapigo_id', 'national_id', 'phone']
    readonly_fields = ['mapigo_id', 'qr_code', 'created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(PatientConsent)
class PatientConsentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'clinic', 'is_active', 'granted_at']
    list_filter = ['is_active']
