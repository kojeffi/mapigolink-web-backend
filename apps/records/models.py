import uuid
from django.db import models


class MedicalRecord(models.Model):
    RECORD_TYPES = [
        ('consultation', 'Consultation'),
        ('lab_result', 'Lab Result'),
        ('prescription', 'Prescription'),
        ('imaging', 'Imaging / Radiology'),
        ('surgery', 'Surgery'),
        ('vaccination', 'Vaccination'),
        ('allergy', 'Allergy'),
        ('discharge', 'Discharge Summary'),
        ('referral', 'Referral'),
        ('other', 'Other'),
    ]
    PRIORITY = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='records')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.SET_NULL, null=True, related_name='records')
    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, related_name='created_records')

    record_type = models.CharField(max_length=20, choices=RECORD_TYPES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=PRIORITY, default='medium')

    # Vitals
    weight_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature_c = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    blood_pressure = models.CharField(max_length=20, blank=True)
    pulse_rate = models.IntegerField(null=True, blank=True)
    oxygen_saturation = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)

    visit_date = models.DateTimeField()
    follow_up_date = models.DateField(null=True, blank=True)
    is_confidential = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'medical_records'
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.patient.full_name} - {self.record_type} ({self.visit_date.date()})"


class RecordAttachment(models.Model):
    ATTACHMENT_TYPES = [
        ('image', 'Image'), ('pdf', 'PDF'), ('lab', 'Lab Report'),
        ('xray', 'X-Ray'), ('other', 'Other'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='records/attachments/')
    attachment_type = models.CharField(max_length=10, choices=ATTACHMENT_TYPES, default='other')
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'record_attachments'


class Prescription(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='prescriptions')
    medication_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)
    quantity = models.IntegerField(default=1)
    is_dispensed = models.BooleanField(default=False)

    class Meta:
        db_table = 'prescriptions'

    def __str__(self):
        return f"{self.medication_name} - {self.dosage}"


class AccessLog(models.Model):
    ACCESS_TYPES = [
        ('view', 'View'), ('qr_scan', 'QR Scan'),
        ('edit', 'Edit'), ('download', 'Download'),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='access_logs')
    accessed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.SET_NULL, null=True, blank=True)
    access_type = models.CharField(max_length=10, choices=ACCESS_TYPES, default='view')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    accessed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'access_logs'
        ordering = ['-accessed_at']
