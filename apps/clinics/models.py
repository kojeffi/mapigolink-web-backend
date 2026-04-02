import uuid
from django.db import models


class Clinic(models.Model):
    CLINIC_TYPES = [
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('health_center', 'Health Center'),
        ('pharmacy', 'Pharmacy'),
        ('laboratory', 'Laboratory'),
        ('specialist', 'Specialist Center'),
    ]
    STATUS = [
        ('active', 'Active'),
        ('pending', 'Pending Verification'),
        ('suspended', 'Suspended'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    clinic_type = models.CharField(max_length=20, choices=CLINIC_TYPES, default='clinic')
    registration_number = models.CharField(max_length=100, unique=True)
    country = models.CharField(max_length=100)
    county_district = models.CharField(max_length=100, blank=True)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='clinics/logos/', null=True, blank=True)

    admin = models.ForeignKey(
        'accounts.User', on_delete=models.SET_NULL, null=True,
        related_name='managed_clinics'
    )
    status = models.CharField(max_length=10, choices=STATUS, default='pending')
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Geolocation
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        db_table = 'clinics'
        ordering = ['-joined_at']

    def __str__(self):
        return f"{self.name} ({self.country})"

    @property
    def staff_count(self):
        return self.staff.count()

    @property
    def patient_count(self):
        return self.patients.count()

    @property
    def record_count(self):
        return self.records.count()


class ClinicStaff(models.Model):
    ROLES = [
        ('doctor', 'Doctor'), ('nurse', 'Nurse'),
        ('receptionist', 'Receptionist'), ('lab_tech', 'Lab Technician'),
        ('pharmacist', 'Pharmacist'), ('admin', 'Admin'),
    ]
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='staff')
    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='clinic_roles')
    role = models.CharField(max_length=20, choices=ROLES)
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'clinic_staff'
        unique_together = ['clinic', 'user']

    def __str__(self):
        return f"{self.user.full_name} @ {self.clinic.name}"
