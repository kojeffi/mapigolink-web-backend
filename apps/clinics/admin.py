from django.contrib import admin
from .models import Clinic, ClinicStaff


class ClinicStaffInline(admin.TabularInline):
    model = ClinicStaff
    extra = 0


@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ['name', 'clinic_type', 'country', 'status', 'is_verified', 'joined_at']
    list_filter = ['clinic_type', 'country', 'status', 'is_verified']
    search_fields = ['name', 'registration_number']
    inlines = [ClinicStaffInline]
    actions = ['verify_clinics']

    def verify_clinics(self, request, queryset):
        from django.utils import timezone
        queryset.update(is_verified=True, status='active', verified_at=timezone.now())
        self.message_user(request, f"{queryset.count()} clinic(s) verified.")
    verify_clinics.short_description = "Verify selected clinics"
