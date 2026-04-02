from rest_framework import serializers
from .models import Patient, PatientConsent


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['id', 'mapigo_id', 'qr_code', 'created_at', 'updated_at']

    def get_qr_code_url(self, obj):
        request = self.context.get('request')
        if obj.qr_code and request:
            return request.build_absolute_uri(obj.qr_code.url)
        return None


class PatientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        exclude = ['qr_code', 'mapigo_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['registered_by'] = self.context['request'].user
        return super().create(validated_data)


class PatientListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for lists"""
    full_name = serializers.ReadOnlyField()
    age = serializers.ReadOnlyField()

    class Meta:
        model = Patient
        fields = ['id', 'mapigo_id', 'full_name', 'date_of_birth', 'age',
                  'gender', 'blood_group', 'country', 'phone', 'status',
                  'photo', 'created_at']


class PatientConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientConsent
        fields = '__all__'
        read_only_fields = ['granted_at', 'granted_by']
