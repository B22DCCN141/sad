from rest_framework import serializers
from .models import Doctor, Patient, Appointment, MedicalRecord, HealthcareChat, ChatMessage


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = [
            'id', 'name', 'email', 'phone', 'department', 'specialization',
            'license_number', 'experience_years', 'bio', 'rating', 'is_available',
            'photo_url', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PatientSerializer(serializers.ModelSerializer):
    age = serializers.SerializerMethodField()
    
    class Meta:
        model = Patient
        fields = [
            'id', 'user_id', 'name', 'email', 'phone', 'date_of_birth', 'age',
            'gender', 'blood_type', 'allergies', 'medical_history',
            'emergency_contact', 'emergency_phone', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_age(self, obj):
        from datetime import date
        return (date.today() - obj.date_of_birth).days // 365


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'appointment_type', 'status', 'scheduled_date', 'duration_minutes',
            'reason', 'notes', 'location', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class MedicalRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    
    class Meta:
        model = MedicalRecord
        fields = [
            'id', 'appointment', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'record_type', 'title', 'description', 'findings', 'treatment_plan',
            'medications', 'vital_signs', 'next_followup', 'document_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ChatMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatMessage
        fields = ['id', 'chat', 'sender_role', 'message', 'attachments', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class HealthcareChatSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True, allow_null=True)
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = HealthcareChat
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'subject', 'message_count', 'is_active', 'messages',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
