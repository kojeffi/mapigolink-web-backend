"""
Management command to seed MapigoLink with demo data for presentations.
Usage: python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed demo data for MapigoLink presentation'

    def handle(self, *args, **options):
        from apps.accounts.models import User
        from apps.clinics.models import Clinic, ClinicStaff
        from apps.patients.models import Patient
        from apps.records.models import MedicalRecord, Prescription

        self.stdout.write(self.style.NOTICE('🌱 Seeding MapigoLink demo data...'))

        # Create admin
        admin, _ = User.objects.get_or_create(
            email='admin@mapigolink.org',
            defaults={
                'first_name': 'System', 'last_name': 'Admin',
                'role': 'admin', 'is_staff': True, 'is_superuser': True,
                'country': 'Kenya',
            }
        )
        admin.set_password('Admin@2025')
        admin.save()
        self.stdout.write(f'  ✅ Admin: admin@mapigolink.org / Admin@2025')

        # Create demo doctors
        doctors = []
        for i, (first, last, country) in enumerate([
            ('Dr. James', 'Mwangi', 'Kenya'),
            ('Dr. Amina', 'Hassan', 'Uganda'),
            ('Dr. Sarah', 'Ochieng', 'Tanzania'),
        ]):
            doc, _ = User.objects.get_or_create(
                email=f'doctor{i+1}@mapigolink.org',
                defaults={
                    'first_name': first, 'last_name': last,
                    'role': 'doctor', 'country': country,
                }
            )
            doc.set_password('Doctor@2025')
            doc.save()
            doctors.append(doc)
        self.stdout.write(f'  ✅ Created {len(doctors)} doctors')

        # Create clinics
        clinic_data = [
            ('Nairobi General Hospital', 'hospital', 'Kenya', 'Nairobi County', 'MOH/KE/2024/001'),
            ('Kampala Medical Centre', 'clinic', 'Uganda', 'Central Region', 'MOH/UG/2024/002'),
            ('Dar es Salaam Health Center', 'health_center', 'Tanzania', 'Dar es Salaam', 'MOH/TZ/2024/003'),
            ('Kigali Specialist Clinic', 'specialist', 'Rwanda', 'Kigali City', 'MOH/RW/2024/004'),
        ]
        clinics = []
        for name, ctype, country, district, reg_no in clinic_data:
            clinic, created = Clinic.objects.get_or_create(
                registration_number=reg_no,
                defaults={
                    'name': name, 'clinic_type': ctype, 'country': country,
                    'county_district': district, 'address': f'123 Healthcare St, {district}',
                    'phone': f'+254 700 {random.randint(100000, 999999)}',
                    'email': f'info@{name.lower().replace(" ", "")}.org',
                    'status': 'active', 'is_verified': True,
                    'admin': admin, 'verified_at': timezone.now(),
                }
            )
            clinics.append(clinic)
        self.stdout.write(f'  ✅ Created {len(clinics)} clinics')

        # Assign doctors to clinics
        for i, doc in enumerate(doctors):
            ClinicStaff.objects.get_or_create(
                clinic=clinics[i % len(clinics)],
                user=doc,
                defaults={'role': 'doctor'}
            )

        # Create patients
        patient_data = [
            ('John', 'Kamau', '1985-03-15', 'M', 'Kenya', 'Kenyan', 'O+', '+254711001001'),
            ('Mary', 'Achieng', '1992-07-22', 'F', 'Uganda', 'Ugandan', 'A+', '+256712002002'),
            ('Robert', 'Mushi', '1978-11-08', 'M', 'Tanzania', 'Tanzanian', 'B+', '+255713003003'),
            ('Fatima', 'Omar', '1990-05-30', 'F', 'Kenya', 'Kenyan', 'AB+', '+254714004004'),
            ('Peter', 'Kinyua', '1965-01-17', 'M', 'Kenya', 'Kenyan', 'O-', '+254715005005'),
            ('Grace', 'Nakamura', '1998-09-12', 'F', 'Uganda', 'Ugandan', 'A-', '+256716006006'),
            ('Emmanuel', 'Habimana', '1982-04-25', 'M', 'Rwanda', 'Rwandan', 'B-', '+250717007007'),
            ('Alice', 'Wanjiku', '1975-12-03', 'F', 'Kenya', 'Kenyan', 'O+', '+254718008008'),
        ]

        patients = []
        for first, last, dob, gender, country, nationality, blood, phone in patient_data:
            p, created = Patient.objects.get_or_create(
                phone=phone,
                defaults={
                    'first_name': first, 'last_name': last,
                    'date_of_birth': date.fromisoformat(dob),
                    'gender': gender, 'country': country, 'nationality': nationality,
                    'blood_group': blood, 'status': 'active',
                    'registered_by': admin, 'registered_clinic': clinics[0],
                    'allergies': random.choice(['', 'Penicillin', 'Aspirin', 'Sulfa drugs', '']),
                    'chronic_conditions': random.choice(['', 'Hypertension', 'Diabetes Type 2', 'Asthma', '']),
                    'emergency_contact_name': 'Jane Doe',
                    'emergency_contact_phone': '+254700000000',
                    'emergency_contact_relation': 'Spouse',
                }
            )
            patients.append(p)
        self.stdout.write(f'  ✅ Created {len(patients)} patients')

        # Create medical records
        record_types = ['consultation', 'lab_result', 'prescription', 'vaccination', 'imaging']
        record_titles = {
            'consultation': ['Initial Consultation', 'Follow-up Visit', 'Annual Check-up'],
            'lab_result': ['Full Blood Count', 'Malaria Test', 'Blood Sugar Test', 'HIV Test'],
            'prescription': ['Antibiotic Course', 'Antihypertensive', 'Antimalarial Treatment'],
            'vaccination': ['Tetanus Booster', 'Yellow Fever', 'COVID-19 Vaccine'],
            'imaging': ['Chest X-Ray', 'Abdominal Ultrasound', 'Brain CT Scan'],
        }

        records_created = 0
        for patient in patients:
            for _ in range(random.randint(2, 5)):
                rtype = random.choice(record_types)
                title = random.choice(record_titles[rtype])
                visit_date = timezone.now() - timedelta(days=random.randint(1, 365))
                record = MedicalRecord.objects.create(
                    patient=patient,
                    clinic=random.choice(clinics),
                    created_by=random.choice(doctors),
                    record_type=rtype,
                    title=title,
                    description=f'Patient presented with complaints. {title} performed.',
                    diagnosis='Patient assessed and treatment plan established.',
                    treatment='Standard treatment protocol applied as per guidelines.',
                    priority=random.choice(['low', 'medium', 'medium', 'high']),
                    visit_date=visit_date,
                    weight_kg=random.randint(50, 95),
                    height_cm=random.randint(155, 185),
                    temperature_c=random.choice([36.5, 36.8, 37.0, 37.2, 38.0]),
                    blood_pressure=random.choice(['120/80', '130/85', '140/90', '115/75']),
                    pulse_rate=random.randint(60, 90),
                )
                if rtype == 'prescription':
                    Prescription.objects.create(
                        record=record,
                        medication_name='Amoxicillin 500mg',
                        dosage='500mg',
                        frequency='3 times daily',
                        duration='7 days',
                        instructions='Take after meals',
                    )
                records_created += 1

        self.stdout.write(f'  ✅ Created {records_created} medical records')

        self.stdout.write(self.style.SUCCESS('\n✨ Demo data seeded successfully!'))
        self.stdout.write(self.style.SUCCESS('─' * 40))
        self.stdout.write(f'  Admin login:    admin@mapigolink.org / Admin@2025')
        self.stdout.write(f'  Doctor login:   doctor1@mapigolink.org / Doctor@2025')
        self.stdout.write(f'  Web app:        http://localhost:3000')
        self.stdout.write(f'  Admin panel:    http://localhost:8000/admin')
        self.stdout.write(f'  API docs:       http://localhost:8000/api/docs/')
        self.stdout.write(self.style.SUCCESS('─' * 40))
