from rest_framework import serializers
from .models import MedicalRecord, RecordAttachment, Prescription, AccessLog


class PrescriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ['id']


class RecordAttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = RecordAttachment
        fields = '__all__'
        read_only_fields = ['id', 'uploaded_at', 'uploaded_by']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class MedicalRecordSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, read_only=True)
    attachments = RecordAttachmentSerializer(many=True, read_only=True)
    created_by_name = serializers.SerializerMethodField()
    clinic_name = serializers.SerializerMethodField()
    patient_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']

    def get_created_by_name(self, obj):
        return obj.created_by.full_name if obj.created_by else None

    def get_clinic_name(self, obj):
        return obj.clinic.name if obj.clinic else None

    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else None


class MedicalRecordCreateSerializer(serializers.ModelSerializer):
    prescriptions = PrescriptionSerializer(many=True, required=False)

    class Meta:
        model = MedicalRecord
        exclude = ['created_by', 'created_at', 'updated_at']

    def create(self, validated_data):
        prescriptions_data = validated_data.pop('prescriptions', [])
        validated_data['created_by'] = self.context['request'].user
        record = super().create(validated_data)
        for p in prescriptions_data:
            Prescription.objects.create(record=record, **p)
        return record


class MedicalRecordListSerializer(serializers.ModelSerializer):
    clinic_name = serializers.SerializerMethodField()

    class Meta:
        model = MedicalRecord
        fields = ['id', 'record_type', 'title', 'diagnosis', 'priority',
                  'visit_date', 'follow_up_date', 'clinic_name', 'created_at']

    def get_clinic_name(self, obj):
        return obj.clinic.name if obj.clinic else None


class AccessLogSerializer(serializers.ModelSerializer):
    accessed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = AccessLog
        fields = '__all__'

    def get_accessed_by_name(self, obj):
        return obj.accessed_by.full_name if obj.accessed_by else None
