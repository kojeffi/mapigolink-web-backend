from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Patient, PatientConsent
from .serializers import PatientSerializer, PatientCreateSerializer, PatientListSerializer, PatientConsentSerializer


class PatientListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['gender', 'blood_group', 'country', 'status']
    search_fields = ['first_name', 'last_name', 'mapigo_id', 'national_id', 'phone']
    ordering_fields = ['created_at', 'first_name', 'last_name']
    ordering = ['-created_at']

    def get_queryset(self):
        return Patient.objects.select_related('registered_clinic', 'registered_by').all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return PatientCreateSerializer
        return PatientListSerializer


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class PatientByMapigoIDView(generics.RetrieveAPIView):
    """Fetch patient by MapigoLink ID (used by QR scan)"""
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'mapigo_id'


class QRScanView(APIView):
    """Clinic scans patient QR code to get records"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        mapigo_id = request.data.get('mapigo_id')
        if not mapigo_id:
            return Response({'error': 'mapigo_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            patient = Patient.objects.get(mapigo_id=mapigo_id)
            # Log the access
            from apps.records.models import AccessLog
            AccessLog.objects.create(
                patient=patient,
                accessed_by=request.user,
                access_type='qr_scan',
                clinic=getattr(request.user, 'clinic', None)
            )
            serializer = PatientSerializer(patient, context={'request': request})
            return Response({
                'patient': serializer.data,
                'message': 'Patient found successfully'
            })
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)


class RegenerateQRView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            patient = Patient.objects.get(id=id)
            patient.qr_code.delete(save=False)
            patient.generate_qr_code()
            patient.save()
            return Response({'message': 'QR code regenerated', 'qr_code': request.build_absolute_uri(patient.qr_code.url)})
        except Patient.DoesNotExist:
            return Response({'error': 'Patient not found'}, status=status.HTTP_404_NOT_FOUND)
