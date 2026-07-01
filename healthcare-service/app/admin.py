from django.contrib import admin
from .models import Doctor, Patient, Appointment, MedicalRecord, HealthcareChat, ChatMessage


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'specialization', 'rating', 'is_available')
    list_filter = ('department', 'is_available', 'created_at')
    search_fields = ('name', 'email', 'license_number')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('name', 'user_id', 'email', 'gender', 'blood_type')
    list_filter = ('gender', 'blood_type', 'created_at')
    search_fields = ('name', 'email', 'user_id')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'scheduled_date', 'status', 'appointment_type')
    list_filter = ('status', 'appointment_type', 'scheduled_date')
    search_fields = ('patient__name', 'doctor__name')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'record_type', 'created_at')
    list_filter = ('record_type', 'created_at')
    search_fields = ('patient__name', 'doctor__name', 'title')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(HealthcareChat)
class HealthcareChatAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'subject', 'is_active', 'updated_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('patient__name', 'subject')
    readonly_fields = ('id', 'created_at', 'updated_at')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender_role', 'created_at', 'is_read')
    list_filter = ('sender_role', 'is_read', 'created_at')
    search_fields = ('message', 'chat__subject')
    readonly_fields = ('id', 'created_at')
