from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from .models import Clinic, ClinicStaff
from .serializers import ClinicSerializer, ClinicListSerializer, ClinicStaffSerializer


class ClinicListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['clinic_type', 'country', 'status', 'is_verified']
    search_fields = ['name', 'registration_number', 'country', 'county_district']
    ordering_fields = ['joined_at', 'name']
    ordering = ['-joined_at']

    def get_queryset(self):
        return Clinic.objects.select_related('admin').all()

    def get_serializer_class(self):
        return ClinicSerializer if self.request.method == 'POST' else ClinicListSerializer


class ClinicDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Clinic.objects.prefetch_related('staff')
    serializer_class = ClinicSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'


class VerifyClinicView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        if request.user.role != 'admin':
            return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)
        try:
            clinic = Clinic.objects.get(id=id)
            clinic.is_verified = True
            clinic.status = 'active'
            clinic.verified_at = timezone.now()
            clinic.save()
            return Response({'message': f'{clinic.name} has been verified'})
        except Clinic.DoesNotExist:
            return Response({'error': 'Clinic not found'}, status=status.HTTP_404_NOT_FOUND)


class ClinicStaffListView(generics.ListCreateAPIView):
    serializer_class = ClinicStaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ClinicStaff.objects.filter(clinic__id=self.kwargs['clinic_id']).select_related('user')

    def perform_create(self, serializer):
        clinic = Clinic.objects.get(id=self.kwargs['clinic_id'])
        serializer.save(clinic=clinic)
