from datetime import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
import requests

from app.models import (
    Appointment,
    ChatMessage,
    Doctor,
    HealthcareChat,
    MedicalRecord,
    Patient,
)


DOCTORS = [
    {
        'name': 'Nguyen Minh An',
        'email': 'an.nguyen@healthcare.local',
        'phone': '+84901110001',
        'department': 'general',
        'specialization': 'Kham tong quat va suc khoe dinh ky',
        'license_number': 'HCP-GEN-0001',
        'experience_years': 12,
        'bio': 'Kinh nghiem cham soc suc khoe tong the cho nguoi lon va tre em.',
        'rating': 4.9,
        'is_available': True,
        'photo_url': 'https://placehold.co/600x600/f97316/ffffff?text=Dr+An',
    },
    {
        'name': 'Tran Thu Hien',
        'email': 'hien.tran@healthcare.local',
        'phone': '+84901110002',
        'department': 'cardiology',
        'specialization': 'Chuyen khoa tim mach, tang huyet ap',
        'license_number': 'HCP-CAR-0001',
        'experience_years': 15,
        'bio': 'Tap trung dieu tri benh tim mach, theo doi huyet ap va ro lieu.',
        'rating': 4.8,
        'is_available': True,
        'photo_url': 'https://placehold.co/600x600/ec4899/ffffff?text=Dr+Hien',
    },
    {
        'name': 'Le Quang Phuc',
        'email': 'phuc.le@healthcare.local',
        'phone': '+84901110003',
        'department': 'dermatology',
        'specialization': 'Da lieu, di ung da, my pham',
        'license_number': 'HCP-DER-0001',
        'experience_years': 9,
        'bio': 'Kham va dieu tri cac van de ve da, mun, viem da va di ung.',
        'rating': 4.7,
        'is_available': True,
        'photo_url': 'https://placehold.co/600x600/8b5cf6/ffffff?text=Dr+Phuc',
    },
    {
        'name': 'Pham Ngoc Mai',
        'email': 'mai.pham@healthcare.local',
        'phone': '+84901110004',
        'department': 'pediatrics',
        'specialization': 'Nhi khoa, tiem chung, dinh duong tre em',
        'license_number': 'HCP-PED-0001',
        'experience_years': 11,
        'bio': 'Theo doi phat trien, tiem chung va cham soc suc khoe nhi.',
        'rating': 4.95,
        'is_available': True,
        'photo_url': 'https://placehold.co/600x600/14b8a6/ffffff?text=Dr+Mai',
    },
    {
        'name': 'Vo Tuan Kiet',
        'email': 'kiet.vo@healthcare.local',
        'phone': '+84901110005',
        'department': 'neurology',
        'specialization': 'Than kinh, dau dau man tinh, roi loan giac ngu',
        'license_number': 'HCP-NEU-0001',
        'experience_years': 14,
        'bio': 'Chuyen dieu tri roi loan than kinh va theo doi dieu tri dai han.',
        'rating': 4.85,
        'is_available': False,
        'photo_url': 'https://placehold.co/600x600/0ea5e9/ffffff?text=Dr+Kiet',
    },
    {
        'name': 'Bui Thanh Lam',
        'email': 'lam.bui@healthcare.local',
        'phone': '+84901110006',
        'department': 'dentistry',
        'specialization': 'Nha khoa tong quat va phuc hinh rang',
        'license_number': 'HCP-DEN-0001',
        'experience_years': 8,
        'bio': 'Kham rang, nha chu, tram rang va phuc hinh tham my.',
        'rating': 4.6,
        'is_available': True,
        'photo_url': 'https://placehold.co/600x600/f43f5e/ffffff?text=Dr+Lam',
    },
]

PATIENT_PROFILES = [
    {
        'date_of_birth': '1995-04-12',
        'gender': 'M',
        'blood_type': 'O+',
        'allergies': 'Penicillin',
        'medical_history': 'Tung co viem xoang va tang can nhe.',
        'emergency_contact': 'Nguyen Thi Lan',
        'emergency_phone': '+84903110001',
    },
    {
        'date_of_birth': '1988-09-23',
        'gender': 'F',
        'blood_type': 'A+',
        'allergies': 'Hai voi hai san',
        'medical_history': 'Co tien su tang huyet ap nhe.',
        'emergency_contact': 'Tran Van Binh',
        'emergency_phone': '+84903110002',
    },
    {
        'date_of_birth': '2001-01-08',
        'gender': 'M',
        'blood_type': 'B+',
        'allergies': '',
        'medical_history': 'Thuong tap gym, can theo doi chan thuong co xuong.',
        'emergency_contact': 'Le Thi Hoa',
        'emergency_phone': '+84903110003',
    },
    {
        'date_of_birth': '2019-07-15',
        'gender': 'F',
        'blood_type': 'AB+',
        'allergies': 'Phan hoa moc',
        'medical_history': 'Tre nho, da tiem chung co ban.',
        'emergency_contact': 'Pham Van Hai',
        'emergency_phone': '+84903110004',
    },
    {
        'date_of_birth': '1992-11-30',
        'gender': 'M',
        'blood_type': 'A-',
        'allergies': '',
        'medical_history': 'Lam viec nhieu, hay met moi va can kiem tra suc khoe dinh ky.',
        'emergency_contact': 'Le Thi Mai',
        'emergency_phone': '+84903110005',
    },
]

APPOINTMENTS = [
    {
    'patient_index': 0,
        'doctor_license': 'HCP-GEN-0001',
        'appointment_type': 'checkup',
        'status': 'confirmed',
        'scheduled_date': datetime(2026, 5, 12, 9, 0),
        'duration_minutes': 30,
        'reason': 'Kham tong quat va kiem tra suc khoe dinh ky',
        'notes': 'Uong nuoc day du truoc khi den kham.',
        'location': 'Phong kham tong quat - Tang 2',
    },
    {
    'patient_index': 1,
        'doctor_license': 'HCP-CAR-0001',
        'appointment_type': 'follow_up',
        'status': 'pending',
        'scheduled_date': datetime(2026, 5, 12, 10, 30),
        'duration_minutes': 20,
        'reason': 'Theo doi huyet ap sau don thuoc truoc do',
        'notes': 'Mang theo so do huyet ap 7 ngay gan nhat.',
        'location': 'Phong tim mach - Tang 3',
    },
    {
    'patient_index': 2,
        'doctor_license': 'HCP-NEU-0001',
        'appointment_type': 'consultation',
        'status': 'confirmed',
        'scheduled_date': datetime(2026, 5, 13, 13, 30),
        'duration_minutes': 30,
        'reason': 'Dau dau keo dai va roi loan giac ngu',
        'notes': 'Kiem tra ca trieu chung va lich ngu.',
        'location': 'Phong than kinh - Tang 4',
    },
    {
    'patient_index': 3,
        'doctor_license': 'HCP-PED-0001',
        'appointment_type': 'consultation',
        'status': 'confirmed',
        'scheduled_date': datetime(2026, 5, 13, 15, 0),
        'duration_minutes': 25,
        'reason': 'Kham nhi va tu van dinh duong',
        'notes': 'Co nguoi than di cung.',
        'location': 'Khoa nhi - Tang 1',
    },
    {
    'patient_index': 0,
        'doctor_license': 'HCP-DER-0001',
        'appointment_type': 'consultation',
        'status': 'completed',
        'scheduled_date': datetime(2026, 5, 9, 14, 0),
        'duration_minutes': 20,
        'reason': 'Noi mun va kich ung da',
        'notes': 'Da hoan thanh kham va co don kem boi.',
        'location': 'Phong da lieu - Tang 2',
    },
    {
    'patient_index': 1,
        'doctor_license': 'HCP-DEN-0001',
        'appointment_type': 'checkup',
        'status': 'confirmed',
        'scheduled_date': datetime(2026, 5, 14, 11, 0),
        'duration_minutes': 30,
        'reason': 'Kiem tra rang dinh ky va ve sinh rang mieng',
        'notes': 'Tra tranh uong nuoc ngoai truoc khi den.',
        'location': 'Nha khoa - Tang 1',
    },
]

RECORDS = [
    {
        'patient_index': 0,
        'record_type': 'diagnosis',
        'title': 'Kham tong quat dinh ky',
        'description': 'Ket luan suc khoe tong the tot, can tang them van dong.',
        'findings': 'Huyet ap on dinh, chi so co the binh thuong.',
        'treatment_plan': 'Duy tri the thao 30 phut/ngay va theo doi can nang.',
        'medications': '[{"name": "Vitamin D", "dosage": "1 vien/ngay"}]',
        'next_followup': timezone.make_aware(datetime(2026, 8, 12, 9, 0)),
    },
    {
        'patient_index': 1,
        'record_type': 'prescription',
        'title': 'Don thuoc tang huyet ap',
        'description': 'Don thuoc sau lan tai kham tim mach.',
        'findings': 'Huyet ap giao dong nhe, can theo doi lien tuc.',
        'treatment_plan': 'Uong thuoc dung gio va do huyet ap moi sang.',
        'medications': '[{"name": "Amlodipine", "dosage": "5mg/ngay"}]',
        'next_followup': timezone.make_aware(datetime(2026, 5, 26, 10, 30)),
    },
    {
        'patient_index': 2,
        'record_type': 'lab_result',
        'title': 'Ket qua xet nghiem co ban',
        'description': 'Mau va sinhhoc co ban trong gioi han cho phep.',
        'findings': 'Khong thay bat thuong lon.',
        'treatment_plan': 'Theo doi them neu trieu chung keo dai.',
        'medications': '[]',
        'next_followup': None,
    },
    {
        'patient_index': 3,
        'record_type': 'vaccination',
        'title': 'Tiem chung nhi khoa',
        'description': 'Ghi nhan mui tiem dinh ky cho tre em.',
        'findings': 'Tre phan ung tot sau tiem.',
        'treatment_plan': 'Hen quay lai dung lich tiem tiep theo.',
        'medications': '[]',
        'next_followup': timezone.make_aware(datetime(2026, 6, 15, 15, 0)),
    },
]

CHAT_SESSIONS = [
    {
        'patient_index': 0,
        'doctor_license': 'HCP-GEN-0001',
        'subject': 'Hoi ve lich kham va ket qua tong quat',
        'messages': [
            ('patient', 'Chao bac si, toi muon hoi ve lich kham ngay mai.'),
            ('doctor', 'Chao anh Nam, anh den luc 9:00 sang mai tai phong tong quat nhe.'),
            ('patient', 'Cam on bac si, toi se co mat dung gio.'),
        ],
    },
    {
        'patient_index': 1,
        'doctor_license': 'HCP-CAR-0001',
        'subject': 'Theo doi huyet ap',
        'messages': [
            ('patient', 'Chao bac si, huyet ap cua toi sang nay la 135/88.'),
            ('doctor', 'Anh tiep tuc ghi nhat ky huyet ap, uong thuoc dung gio va han che muoi.'),
            ('patient', 'Vang, toi se theo doi hang ngay.'),
        ],
    },
    {
        'patient_index': 3,
        'doctor_license': 'HCP-PED-0001',
        'subject': 'Tu van dinh duong cho tre',
        'messages': [
            ('patient', 'Bac si oi, be an kem va hay moi dem.'),
            ('doctor', 'Chi nen chia nho bua an, tang sua va rau cu qua phu hop lứa tuoi.'),
        ],
    },
]


class Command(BaseCommand):
    help = 'Seed sample healthcare data: doctors, patients, appointments, records, and chat.'

    def _safe_write(self, msg):
        try:
            self.stdout.write(msg)
        except UnicodeEncodeError:
            self.stdout.write(msg.encode('ascii', errors='replace').decode('ascii'))

    def handle(self, *args, **options):
        self._safe_write('=== Seeding Healthcare Data ===\n')
        with transaction.atomic():
            doctors = self._seed_doctors()
            patients = self._seed_patients()
            appointments = self._seed_appointments(doctors, patients)
            self._seed_records(doctors, patients, appointments)
            self._seed_chats(doctors, patients)
        self._safe_write(self.style.SUCCESS('\nDone! Healthcare sample data seeded successfully.'))

    def _seed_doctors(self):
        self._safe_write('[Doctors]')
        doctors = {}
        for doctor_data in DOCTORS:
            doctor, created = Doctor.objects.update_or_create(
                license_number=doctor_data['license_number'],
                defaults=doctor_data,
            )
            doctors[doctor.license_number] = doctor
            label = 'Created' if created else 'Updated'
            self._safe_write(f"  [{label}] {doctor.name} ({doctor.department})")
        return doctors

    def _seed_patients(self):
        self._safe_write('\n[Patients]')
        patients = {}
        customer_rows = self._fetch_customers()
        for index, patient_data in enumerate(self._build_patient_rows(customer_rows)):
            patient, created = Patient.objects.update_or_create(
                user_id=patient_data['user_id'],
                defaults=patient_data,
            )
            patients[patient.user_id] = patient
            label = 'Created' if created else 'Updated'
            self._safe_write(f"  [{label}] {patient.name} ({patient.user_id})")
        return patients

    def _fetch_customers(self):
        try:
            response = requests.get('http://customer-service:8000/customers/', timeout=5)
            if response.ok:
                payload = response.json()
                if isinstance(payload, list):
                    return payload
        except Exception:
            pass
        return []

    def _build_patient_rows(self, customers):
        rows = []
        if customers:
            for index, customer in enumerate(customers[:len(PATIENT_PROFILES)]):
                profile = PATIENT_PROFILES[index]
                rows.append({
                    'user_id': str(customer.get('id')),
                    'name': customer.get('name') or f'Customer {customer.get("id")}',
                    'email': customer.get('email') or f'customer{customer.get("id")}@example.com',
                    'phone': customer.get('phone') or '',
                    'date_of_birth': profile['date_of_birth'],
                    'gender': profile['gender'],
                    'blood_type': profile['blood_type'],
                    'allergies': profile['allergies'],
                    'medical_history': profile['medical_history'],
                    'emergency_contact': profile['emergency_contact'],
                    'emergency_phone': profile['emergency_phone'],
                })
            return rows

        for index, profile in enumerate(PATIENT_PROFILES, start=1):
            rows.append({
                'user_id': str(index),
                'name': f'Patient {index}',
                'email': f'patient{index}@healthcare.local',
                'phone': f'+8490211000{index}',
                **profile,
            })
        return rows

    def _seed_appointments(self, doctors, patients):
        self._safe_write('\n[Appointments]')
        appointments = {}
        for item in APPOINTMENTS:
            scheduled_date = timezone.make_aware(item['scheduled_date'])
            appointment, created = Appointment.objects.update_or_create(
                patient=patients[str(self._get_patient_user_id(item, patients))],
                doctor=doctors[item['doctor_license']],
                scheduled_date=scheduled_date,
                defaults={
                    'appointment_type': item['appointment_type'],
                    'status': item['status'],
                    'duration_minutes': item['duration_minutes'],
                    'reason': item['reason'],
                    'notes': item['notes'],
                    'location': item['location'],
                },
            )
            appointments[(str(appointment.patient.user_id), item['doctor_license'], scheduled_date)] = appointment
            label = 'Created' if created else 'Updated'
            self._safe_write(f"  [{label}] {appointment.patient.name} -> {appointment.doctor.name} @ {scheduled_date:%Y-%m-%d %H:%M}")
        return appointments

    def _get_patient_user_id(self, item, patients):
        if 'patient_user_id' in item:
            return item['patient_user_id']
        patient_index = item['patient_index']
        return list(patients.keys())[patient_index]

    def _seed_records(self, doctors, patients, appointments):
        self._safe_write('\n[Medical Records]')
        for item in RECORDS:
            patient = patients[str(self._get_patient_user_id(item, patients))]
            doctor = next((doc for doc in doctors.values() if doc.department in ['general', 'cardiology', 'dermatology', 'pediatrics']), None)
            if item.get('patient_index') == 1:
                doctor = doctors['HCP-CAR-0001']
            elif item.get('patient_index') == 3:
                doctor = doctors['HCP-PED-0001']
            elif item.get('patient_index') == 0 and item['record_type'] == 'diagnosis':
                doctor = doctors['HCP-GEN-0001']
            else:
                doctor = doctor or doctors['HCP-GEN-0001']

            appointment = None
            for key, value in appointments.items():
                if key[0] == patient.user_id:
                    appointment = value
                    break
            if appointment is None:
                continue

            record, created = MedicalRecord.objects.update_or_create(
                appointment=appointment,
                defaults={
                    'patient': patient,
                    'doctor': doctor,
                    'record_type': item['record_type'],
                    'title': item['title'],
                    'description': item['description'],
                    'findings': item['findings'],
                    'treatment_plan': item['treatment_plan'],
                    'medications': item['medications'],
                    'vital_signs': {
                        'temperature': 36.7,
                        'blood_pressure': '120/80',
                        'heart_rate': 72,
                    },
                    'next_followup': item['next_followup'],
                    'document_url': f"https://placehold.co/1200x1600/f8fafc/0f172a?text={item['title'].replace(' ', '+')}",
                },
            )
            label = 'Created' if created else 'Updated'
            self._safe_write(f"  [{label}] {record.title} ({patient.name})")

    def _seed_chats(self, doctors, patients):
        self._safe_write('\n[Chats]')
        for session in CHAT_SESSIONS:
            patient = patients[str(self._get_patient_user_id(session, patients))]
            doctor = doctors[session['doctor_license']]
            chat, created = HealthcareChat.objects.update_or_create(
                patient=patient,
                subject=session['subject'],
                defaults={
                    'doctor': doctor,
                    'message_count': 0,
                    'is_active': True,
                },
            )
            chat.messages.all().delete()
            for sender_role, message in session['messages']:
                ChatMessage.objects.create(
                    chat=chat,
                    sender_role=sender_role,
                    message=message,
                    attachments=[],
                    is_read=sender_role != 'patient',
                )
            chat.message_count = chat.messages.count()
            chat.save(update_fields=['message_count', 'updated_at'])
            label = 'Created' if created else 'Updated'
            self._safe_write(f"  [{label}] {chat.subject} ({patient.name} - {doctor.name})")
