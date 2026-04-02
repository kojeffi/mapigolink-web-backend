from rest_framework import serializers
from .models import Clinic, ClinicStaff


class ClinicStaffSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField()
    user_email = serializers.SerializerMethodField()

    class Meta:
        model = ClinicStaff
        fields = '__all__'
        read_only_fields = ['joined_at']

    def get_user_name(self, obj):
        return obj.user.full_name

    def get_user_email(self, obj):
        return obj.user.email


class ClinicSerializer(serializers.ModelSerializer):
    staff_count = serializers.ReadOnlyField()
    patient_count = serializers.ReadOnlyField()
    record_count = serializers.ReadOnlyField()
    admin_name = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        fields = '__all__'
        read_only_fields = ['id', 'joined_at', 'updated_at', 'verified_at']

    def get_admin_name(self, obj):
        return obj.admin.full_name if obj.admin else None


class ClinicListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinic
        fields = ['id', 'name', 'clinic_type', 'country', 'county_district',
                  'phone', 'status', 'is_verified', 'logo', 'joined_at']
