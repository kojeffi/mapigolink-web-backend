import uuid
import qrcode
import os
from io import BytesIO
from django.db import models
from django.core.files import File
from django.conf import settings


def generate_mapigo_id():
    """Generate unique MapigoLink patient ID"""
    import random
    import string
    prefix = "ML"
    year = __import__('datetime').datetime.now().year
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{year}-{suffix}"


class Patient(models.Model):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-'),
    ]
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    STATUS_CHOICES = [('active', 'Active'), ('inactive', 'Inactive'), ('deceased', 'Deceased')]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    mapigo_id = models.CharField(max_length=20, unique=True, default=generate_mapigo_id)
    
    # Personal Info
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    national_id = models.CharField(max_length=50, blank=True)
    passport_number = models.CharField(max_length=50, blank=True)
    
    # Contact
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    country = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    
    # Medical
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, blank=True)
    allergies = models.TextField(blank=True)
    chronic_conditions = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    
    # System
    photo = models.ImageField(upload_to='patients/photos/', null=True, blank=True)
    qr_code = models.ImageField(upload_to='qrcodes/', blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    registered_by = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True, related_name='registered_patients'
    )
    registered_clinic = models.ForeignKey(
        'clinics.Clinic', on_delete=models.SET_NULL, null=True, blank=True, related_name='patients'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.mapigo_id})"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age(self):
        from datetime import date
        today = date.today()
        dob = self.date_of_birth
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

    def generate_qr_code(self):
        """Generate QR code for patient"""
        qr_data = {
            'mapigo_id': self.mapigo_id,
            'name': self.full_name,
            'blood_group': self.blood_group,
            'allergies': self.allergies,
        }
        import json
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(json.dumps(qr_data))
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0f4c81", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        filename = f'qr_{self.mapigo_id}.png'
        self.qr_code.save(filename, File(buffer), save=False)

    def save(self, *args, **kwargs):
        if not self.qr_code:
            self.generate_qr_code()
        super().save(*args, **kwargs)


class PatientConsent(models.Model):
    """Track which clinics have access to patient records"""
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='consents')
    clinic = models.ForeignKey('clinics.Clinic', on_delete=models.CASCADE)
    granted_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    granted_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'patient_consents'
        unique_together = ['patient', 'clinic']
