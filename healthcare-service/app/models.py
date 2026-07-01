from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import uuid


class Doctor(models.Model):
    """Mô hình Bác sĩ"""
    DEPARTMENT_CHOICES = [
        ('cardiology', 'Tim mạch'),
        ('dermatology', 'Da liễu'),
        ('neurology', 'Thần kinh'),
        ('pediatrics', 'Nhi khoa'),
        ('orthopedics', 'Chỉnh hình'),
        ('psychiatry', 'Tâm thần'),
        ('general', 'Khám tổng quát'),
        ('dentistry', 'Nha khoa'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Invalid phone number')]
    )
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    specialization = models.CharField(max_length=255)
    license_number = models.CharField(max_length=100, unique=True)
    experience_years = models.PositiveIntegerField()
    bio = models.TextField(blank=True)
    rating = models.FloatField(
        default=5.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    is_available = models.BooleanField(default=True)
    photo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-rating', 'name']
        indexes = [
            models.Index(fields=['department']),
            models.Index(fields=['is_available']),
        ]

    def __str__(self):
        return f"{self.name} - {self.get_department_display()}"


class Patient(models.Model):
    """Mô hình Bệnh nhân"""
    BLOOD_TYPE_CHOICES = [
        ('O+', 'O+'),
        ('O-', 'O-'),
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.CharField(max_length=100, unique=True)  # From customer service
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?1?\d{9,15}$', 'Invalid phone number')]
    )
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=10, choices=[('M', 'Nam'), ('F', 'Nữ'), ('O', 'Khác')])
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES, blank=True)
    allergies = models.TextField(blank=True, help_text="Dị ứng")
    medical_history = models.TextField(blank=True)
    emergency_contact = models.CharField(max_length=255, blank=True)
    emergency_phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user_id']),
            models.Index(fields=['email']),
        ]

    def __str__(self):
        return f"{self.name} ({self.user_id})"


class Appointment(models.Model):
    """Mô hình Lịch hẹn"""
    STATUS_CHOICES = [
        ('pending', 'Chờ xác nhận'),
        ('confirmed', 'Đã xác nhận'),
        ('in_progress', 'Đang khám'),
        ('completed', 'Hoàn thành'),
        ('cancelled', 'Đã hủy'),
        ('no_show', 'Không đến'),
    ]
    
    APPOINTMENT_TYPE_CHOICES = [
        ('consultation', 'Tư vấn'),
        ('follow_up', 'Tái khám'),
        ('surgery', 'Phẫu thuật'),
        ('checkup', 'Khám sức khỏe'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='appointments')
    appointment_type = models.CharField(max_length=50, choices=APPOINTMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=30)
    reason = models.TextField()
    notes = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']
        indexes = [
            models.Index(fields=['patient', 'scheduled_date']),
            models.Index(fields=['doctor', 'scheduled_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Cuộc hẹn: {self.patient.name} - BS. {self.doctor.name} ({self.scheduled_date})"


class MedicalRecord(models.Model):
    """Mô hình Hồ sơ bệnh án"""
    RECORD_TYPE_CHOICES = [
        ('diagnosis', 'Chuẩn đoán'),
        ('prescription', 'Đơn thuốc'),
        ('lab_result', 'Kết quả xét nghiệm'),
        ('imaging', 'Chẩn đoán hình ảnh'),
        ('surgery_report', 'Báo cáo phẫu thuật'),
        ('vaccination', 'Tiêm chủng'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='medical_records')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='medical_records')
    record_type = models.CharField(max_length=50, choices=RECORD_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    findings = models.TextField(blank=True)
    treatment_plan = models.TextField(blank=True)
    medications = models.TextField(blank=True, help_text="JSON format: [{'name': '...', 'dosage': '...'}]")
    vital_signs = models.JSONField(blank=True, null=True, help_text="{'temperature': 37.5, 'blood_pressure': '120/80', ...}")
    next_followup = models.DateTimeField(blank=True, null=True)
    document_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['patient', 'created_at']),
            models.Index(fields=['doctor', 'created_at']),
        ]

    def __str__(self):
        return f"{self.get_record_type_display()} - {self.patient.name}"


class HealthcareChat(models.Model):
    """Mô hình Chat hỗ trợ sức khỏe"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='chats')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_chats')
    subject = models.CharField(max_length=255)
    message_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['patient', 'is_active']),
            models.Index(fields=['doctor', 'is_active']),
        ]

    def __str__(self):
        return f"Chat: {self.patient.name} - {self.subject}"


class ChatMessage(models.Model):
    """Mô hình Tin nhắn chat"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    chat = models.ForeignKey(HealthcareChat, on_delete=models.CASCADE, related_name='messages')
    sender_role = models.CharField(max_length=20, choices=[('patient', 'Bệnh nhân'), ('doctor', 'Bác sĩ'), ('system', 'Hệ thống')])
    message = models.TextField()
    attachments = models.JSONField(default=list, blank=True)  # URL danh sách tập tin đính kèm
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['chat', 'created_at']),
            models.Index(fields=['is_read']),
        ]

    def __str__(self):
        return f"{self.get_sender_role_display()}: {self.message[:50]}"
