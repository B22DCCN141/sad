# Healthcare Service - Microservice Design

## Tổng Quan

Healthcare Service là một microservice độc lập quản lý toàn bộ hệ thống y tế:
- **Bác sĩ** (Doctors)
- **Bệnh nhân** (Patients)
- **Lịch hẹn** (Appointments)
- **Hồ sơ bệnh án** (Medical Records)
- **Chat hỗ trợ** (Chat Support)

## Cấu Trúc

```
healthcare-service/
├── app/
│   ├── models.py          # Các mô hình: Doctor, Patient, Appointment...
│   ├── views.py           # ViewSets REST API
│   ├── serializers.py     # Serializers cho API
│   ├── urls.py            # URL routing
│   ├── admin.py           # Django Admin
│   └── apps.py            # App configuration
├── config/
│   ├── settings/
│   │   ├── base.py        # Base settings
│   │   ├── dev.py         # Development
│   │   └── prod.py        # Production
│   └── urls.py            # Project URLs
├── manage.py
├── requirements.txt
└── Dockerfile
```

## API Endpoints

### Doctors
- `GET /api/doctors/` - Danh sách bác sĩ
- `GET /api/doctors/available/` - Bác sĩ khả dụng
- `GET /api/doctors/by_department/?dept=cardiology` - Bác sĩ theo chuyên khoa
- `GET /api/doctors/{id}/schedule/` - Lịch khám của bác sĩ

### Patients
- `GET /api/patients/` - Danh sách bệnh nhân
- `GET /api/patients/{id}/appointments/` - Lịch hẹn của bệnh nhân
- `GET /api/patients/{id}/medical_records/` - Hồ sơ bệnh án

### Appointments
- `GET /api/appointments/` - Danh sách lịch hẹn
- `GET /api/appointments/upcoming/` - Lịch hẹn sắp tới
- `POST /api/appointments/{id}/confirm/` - Xác nhận lịch hẹn
- `POST /api/appointments/{id}/cancel/` - Hủy lịch hẹn

### Medical Records
- `GET /api/medical-records/` - Danh sách hồ sơ
- `GET /api/medical-records/by_patient/?patient_id=xxx` - Hồ sơ theo bệnh nhân

### Chat
- `GET /api/chats/` - Danh sách chat
- `GET /api/chats/by_patient/?patient_id=xxx` - Chat của bệnh nhân
- `POST /api/chats/{id}/send_message/` - Gửi tin nhắn
- `POST /api/chats/{id}/close/` - Đóng chat

## Models

### Doctor
```python
- name: CharField
- email: EmailField (unique)
- phone: CharField
- department: Choice field (cardiology, dermatology, ...)
- specialization: CharField
- license_number: CharField (unique)
- experience_years: PositiveIntegerField
- bio: TextField
- rating: FloatField (0-5)
- is_available: BooleanField
- photo_url: URLField
```

### Patient
```python
- user_id: CharField (unique, from customer service)
- name: CharField
- email: EmailField
- phone: CharField
- date_of_birth: DateField
- gender: Choice field (M, F, O)
- blood_type: Choice field (O+, A+, ...)
- allergies: TextField
- medical_history: TextField
- emergency_contact: CharField
- emergency_phone: CharField
```

### Appointment
```python
- patient: ForeignKey(Patient)
- doctor: ForeignKey(Doctor)
- appointment_type: Choice (consultation, follow_up, surgery, checkup)
- status: Choice (pending, confirmed, in_progress, completed, cancelled, no_show)
- scheduled_date: DateTimeField
- duration_minutes: PositiveIntegerField
- reason: TextField
- notes: TextField
- location: CharField
```

### MedicalRecord
```python
- appointment: ForeignKey(Appointment)
- patient: ForeignKey(Patient)
- doctor: ForeignKey(Doctor)
- record_type: Choice (diagnosis, prescription, lab_result, imaging, surgery_report, vaccination)
- title: CharField
- description: TextField
- findings: TextField
- treatment_plan: TextField
- medications: TextField (JSON)
- vital_signs: JSONField
- next_followup: DateTimeField
- document_url: URLField
```

### HealthcareChat
```python
- patient: ForeignKey(Patient)
- doctor: ForeignKey(Doctor, nullable)
- subject: CharField
- message_count: PositiveIntegerField
- is_active: BooleanField
```

### ChatMessage
```python
- chat: ForeignKey(HealthcareChat)
- sender_role: Choice (patient, doctor, system)
- message: TextField
- attachments: JSONField (list of URLs)
- is_read: BooleanField
```

## Frontend

File: `store-front/healthcare.html`
Script: `store-front/healthcare-chat.js`

### Chức Năng:
1. **Tìm Bác Sĩ** - Lọc theo chuyên khoa, tìm kiếm theo tên
2. **Đặt Lịch Hẹn** - Chọn bác sĩ, thời gian, lý do
3. **Chat Trực Tiếp** - Nhắn tin với bác sĩ
4. **Xem Hồ Sơ Y Tế** - Kết quả xét nghiệm, đơn thuốc, chẩn đoán

## Cách Chạy

```bash
# Development
cd healthcare-service
python manage.py migrate
python manage.py runserver 0.0.0.0:8015

# Docker
docker-compose up healthcare-service
```

## Integration

Healthcare Service tích hợp với:
- **API Gateway** (8000) - Routing các request
- **Customer Service** (8001) - Lấy thông tin bệnh nhân
- **Database** - SQLite (development), PostgreSQL (production)

## Các Lệnh Admin

```bash
# Tạo bác sĩ mẫu
python manage.py shell
>>> from app.models import Doctor
>>> Doctor.objects.create(name="...", ...)

# Truy cập admin
python manage.py createsuperuser
http://localhost:8015/admin
```

## Phân Rã Khung Chat

### Kiến Trúc Chat

```text
Frontend (healthcare-chat.js)
    ↓
REST API (/api/chats/)
    ↓
Django ViewSet (HealthcareChatViewSet)
    ↓
Database (HealthcareChat, ChatMessage models)
```

### Chat Flow

1. **Tạo Cuộc Chat**
   - Bệnh nhân chọn bác sĩ hoặc tạo chat mới
   - Gọi POST `/api/chats/`
   - Tạo HealthcareChat record

2. **Gửi Tin Nhắn**
   - Gọi POST `/api/chats/{id}/send_message/`
   - Tạo ChatMessage record
   - Update message_count

3. **Nhận Tin Nhắn**
   - GET `/api/chats/{id}/` với nested messages
   - Render UI với role (patient/doctor/system)

4. **Đóng Chat**
   - Gọi POST `/api/chats/{id}/close/`
   - Set is_active = False

### Frontend Components

- **ChatList** - Danh sách cuộc hội thoại
- **ChatWindow** - Hiển thị tin nhắn
- **MessageInput** - Input gửi tin nhắn
- **MessageBubble** - UI tin nhắn (patient/doctor/system)

## Mở Rộng

- Thêm WebSocket cho real-time chat
- Integratie video call (Twilio/Agora)
- Notification system (Firebase Cloud Messaging)
- AI-powered health recommendations
