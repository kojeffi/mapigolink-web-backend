from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import MedicalRecord, RecordAttachment, Prescription, AccessLog
from .serializers import (
    MedicalRecordSerializer, MedicalRecordCreateSerializer,
    MedicalRecordListSerializer, RecordAttachmentSerializer,
    PrescriptionSerializer, AccessLogSerializer
)


class MedicalRecordListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['record_type', 'priority', 'patient', 'clinic']
    search_fields = ['title', 'diagnosis', 'description']
    ordering_fields = ['visit_date', 'created_at']
    ordering = ['-visit_date']

    def get_queryset(self):
        qs = MedicalRecord.objects.select_related('patient', 'clinic', 'created_by')
        patient_id = self.request.query_params.get('patient_id')
        if patient_id:
            qs = qs.filter(patient__id=patient_id)
        return qs

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MedicalRecordCreateSerializer
        return MedicalRecordListSerializer


class MedicalRecordDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MedicalRecord.objects.prefetch_related('prescriptions', 'attachments')
    serializer_class = MedicalRecordSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Log the access
        AccessLog.objects.create(
            patient=instance.patient,
            accessed_by=request.user,
            access_type='view',
            ip_address=request.META.get('REMOTE_ADDR')
        )
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class PatientRecordsView(generics.ListAPIView):
    serializer_class = MedicalRecordListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        patient_id = self.kwargs['patient_id']
        return MedicalRecord.objects.filter(patient__id=patient_id).order_by('-visit_date')


class AttachmentUploadView(generics.CreateAPIView):
    serializer_class = RecordAttachmentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)


class PrescriptionListCreateView(generics.ListCreateAPIView):
    serializer_class = PrescriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        record_id = self.kwargs.get('record_id')
        return Prescription.objects.filter(record__id=record_id)

    def perform_create(self, serializer):
        record_id = self.kwargs.get('record_id')
        record = MedicalRecord.objects.get(id=record_id)
        serializer.save(record=record)


class AccessLogListView(generics.ListAPIView):
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ['access_type', 'patient']
    ordering = ['-accessed_at']

    def get_queryset(self):
        patient_id = self.request.query_params.get('patient_id')
        qs = AccessLog.objects.select_related('accessed_by', 'patient', 'clinic')
        if patient_id:
            qs = qs.filter(patient__id=patient_id)
        return qs
