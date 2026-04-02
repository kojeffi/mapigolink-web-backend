from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth, TruncDate
from django.utils import timezone
from datetime import timedelta
from apps.patients.models import Patient
from apps.records.models import MedicalRecord, AccessLog
from apps.clinics.models import Clinic
from apps.accounts.models import User


class DashboardStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        last_30 = now - timedelta(days=30)
        last_7 = now - timedelta(days=7)

        stats = {
            'patients': {
                'total': Patient.objects.count(),
                'active': Patient.objects.filter(status='active').count(),
                'new_this_month': Patient.objects.filter(created_at__gte=last_30).count(),
                'new_this_week': Patient.objects.filter(created_at__gte=last_7).count(),
            },
            'records': {
                'total': MedicalRecord.objects.count(),
                'this_month': MedicalRecord.objects.filter(created_at__gte=last_30).count(),
                'by_type': list(
                    MedicalRecord.objects.values('record_type')
                    .annotate(count=Count('id'))
                    .order_by('-count')
                ),
            },
            'clinics': {
                'total': Clinic.objects.count(),
                'active': Clinic.objects.filter(status='active').count(),
                'verified': Clinic.objects.filter(is_verified=True).count(),
                'pending': Clinic.objects.filter(status='pending').count(),
                'by_country': list(
                    Clinic.objects.filter(is_verified=True)
                    .values('country')
                    .annotate(count=Count('id'))
                    .order_by('-count')[:10]
                ),
            },
            'users': {
                'total': User.objects.count(),
                'active': User.objects.filter(is_active=True).count(),
                'by_role': list(
                    User.objects.values('role')
                    .annotate(count=Count('id'))
                ),
            },
            'access_logs': {
                'total_today': AccessLog.objects.filter(
                    accessed_at__date=now.date()
                ).count(),
                'qr_scans_today': AccessLog.objects.filter(
                    accessed_at__date=now.date(), access_type='qr_scan'
                ).count(),
            }
        }
        return Response(stats)


class PatientGrowthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        data = (
            Patient.objects
            .annotate(month=TruncMonth('created_at'))
            .values('month')
            .annotate(count=Count('id'))
            .order_by('month')
        )
        return Response(list(data))


class RecordActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        last_30 = timezone.now() - timedelta(days=30)
        data = (
            MedicalRecord.objects
            .filter(created_at__gte=last_30)
            .annotate(day=TruncDate('created_at'))
            .values('day')
            .annotate(count=Count('id'))
            .order_by('day')
        )
        return Response(list(data))


class TopClinicsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clinics = (
            Clinic.objects
            .annotate(
                record_count=Count('records'),
                patient_count=Count('patients')
            )
            .order_by('-record_count')[:10]
            .values('id', 'name', 'country', 'clinic_type', 'record_count', 'patient_count')
        )
        return Response(list(clinics))


class RecentActivityView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        recent_patients = Patient.objects.order_by('-created_at')[:5].values(
            'id', 'mapigo_id', 'first_name', 'last_name', 'country', 'created_at'
        )
        recent_records = MedicalRecord.objects.order_by('-created_at')[:5].values(
            'id', 'title', 'record_type', 'priority', 'created_at'
        )
        recent_access = AccessLog.objects.order_by('-accessed_at')[:10].select_related(
            'patient', 'accessed_by', 'clinic'
        )
        access_data = [
            {
                'patient': a.patient.full_name,
                'accessed_by': a.accessed_by.full_name if a.accessed_by else 'Unknown',
                'access_type': a.access_type,
                'accessed_at': a.accessed_at,
            }
            for a in recent_access
        ]
        return Response({
            'recent_patients': list(recent_patients),
            'recent_records': list(recent_records),
            'recent_access': access_data,
        })
