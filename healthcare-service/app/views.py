from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.utils import timezone

from .models import Doctor, Patient, Appointment, MedicalRecord, HealthcareChat, ChatMessage
from .serializers import (
    DoctorSerializer, PatientSerializer, AppointmentSerializer,
    MedicalRecordSerializer, HealthcareChatSerializer, ChatMessageSerializer
)


class DoctorViewSet(viewsets.ModelViewSet):
    """
    API ViewSet cho Bác sĩ
    - Liệt kê bác sĩ
    - Lọc theo chuyên khoa
    - Tìm kiếm theo tên
    """
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [AllowAny]
    search_fields = ['name', 'department', 'specialization']
    ordering_fields = ['rating', 'experience_years', 'name']
    ordering = ['-rating']

    @action(detail=False, methods=['get'])
    def available(self, request):
        """Lấy danh sách bác sĩ khả dụng"""
        doctors = self.get_queryset().filter(is_available=True)
        serializer = self.get_serializer(doctors, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Lấy bác sĩ theo chuyên khoa"""
        department = request.query_params.get('dept')
        if department:
            doctors = self.get_queryset().filter(department=department)
            serializer = self.get_serializer(doctors, many=True)
            return Response(serializer.data)
        return Response({'error': 'Department parameter required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def schedule(self, request, pk=None):
        """Lấy lịch khám của bác sĩ"""
        doctor = self.get_object()
        appointments = doctor.appointments.filter(
            scheduled_date__gte=timezone.now()
        ).order_by('scheduled_date')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)


class PatientViewSet(viewsets.ModelViewSet):
    """
    API ViewSet cho Bệnh nhân
    """
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [AllowAny]
    search_fields = ['name', 'user_id', 'email']

    @action(detail=True, methods=['get'])
    def appointments(self, request, pk=None):
        """Lấy danh sách lịch hẹn của bệnh nhân"""
        patient = self.get_object()
        appointments = patient.appointments.all().order_by('-scheduled_date')
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def medical_records(self, request, pk=None):
        """Lấy hồ sơ bệnh án của bệnh nhân"""
        patient = self.get_object()
        records = patient.medical_records.all().order_by('-created_at')
        serializer = MedicalRecordSerializer(records, many=True)
        return Response(serializer.data)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    API ViewSet cho Lịch hẹn
    """
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [AllowAny]
    ordering_fields = ['scheduled_date', 'created_at', 'status']
    ordering = ['-scheduled_date']

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Lấy các lịch hẹn sắp tới"""
        appointments = self.get_queryset().filter(
            scheduled_date__gte=timezone.now(),
            status__in=['confirmed', 'pending']
        ).order_by('scheduled_date')
        serializer = self.get_serializer(appointments, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Xác nhận lịch hẹn"""
        appointment = self.get_object()
        appointment.status = 'confirmed'
        appointment.save()
        return Response(
            {'status': 'Lịch hẹn đã được xác nhận'},
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Hủy lịch hẹn"""
        appointment = self.get_object()
        appointment.status = 'cancelled'
        appointment.save()
        return Response(
            {'status': 'Lịch hẹn đã bị hủy'},
            status=status.HTTP_200_OK
        )


class MedicalRecordViewSet(viewsets.ModelViewSet):
    """
    API ViewSet cho Hồ sơ bệnh án
    """
    queryset = MedicalRecord.objects.all()
    serializer_class = MedicalRecordSerializer
    permission_classes = [AllowAny]
    ordering_fields = ['created_at', 'record_type']
    ordering = ['-created_at']

    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Lấy hồ sơ theo bệnh nhân"""
        patient_id = request.query_params.get('patient_id')
        if patient_id:
            records = self.get_queryset().filter(patient_id=patient_id)
            serializer = self.get_serializer(records, many=True)
            return Response(serializer.data)
        return Response({'error': 'Patient ID required'}, status=status.HTTP_400_BAD_REQUEST)


class HealthcareChatViewSet(viewsets.ModelViewSet):
    """
    API ViewSet cho Chat hỗ trợ sức khỏe
    """
    queryset = HealthcareChat.objects.all()
    serializer_class = HealthcareChatSerializer
    permission_classes = [AllowAny]
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']

    @action(detail=False, methods=['get'])
    def by_patient(self, request):
        """Lấy chat theo bệnh nhân"""
        patient_id = request.query_params.get('patient_id')
        if patient_id:
            chats = self.get_queryset().filter(patient_id=patient_id, is_active=True)
            serializer = self.get_serializer(chats, many=True)
            return Response(serializer.data)
        return Response({'error': 'Patient ID required'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Gửi tin nhắn trong chat"""
        chat = self.get_object()
        message_data = request.data.get('message')
        sender_role = request.data.get('sender_role', 'patient')

        message = ChatMessage.objects.create(
            chat=chat,
            sender_role=sender_role,
            message=message_data
        )
        
        chat.message_count += 1
        chat.save()
        
        return Response(
            ChatMessageSerializer(message).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        """Đóng chat"""
        chat = self.get_object()
        chat.is_active = False
        chat.save()
        return Response({'status': 'Chat đã được đóng'}, status=status.HTTP_200_OK)
