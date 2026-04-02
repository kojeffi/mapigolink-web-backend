from django.contrib import admin
from .models import MedicalRecord, RecordAttachment, Prescription, AccessLog


class PrescriptionInline(admin.TabularInline):
    model = Prescription
    extra = 0


class AttachmentInline(admin.TabularInline):
    model = RecordAttachment
    extra = 0


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'record_type', 'title', 'priority', 'visit_date', 'clinic']
    list_filter = ['record_type', 'priority', 'visit_date']
    search_fields = ['patient__first_name', 'patient__last_name', 'title', 'diagnosis']
    inlines = [PrescriptionInline, AttachmentInline]
    ordering = ['-visit_date']


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['patient', 'accessed_by', 'access_type', 'clinic', 'accessed_at']
    list_filter = ['access_type', 'accessed_at']
    ordering = ['-accessed_at']
