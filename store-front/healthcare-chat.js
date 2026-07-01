// Healthcare Chat System
const HEALTHCARE_API = 'http://localhost:8015/api';
let currentPatient = null;
let currentChat = null;

function getStoredUserId() {
    return localStorage.getItem('userId') || localStorage.getItem('user_id');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadPatientInfo();
    showTab('doctors');
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('search-doctor').addEventListener('input', filterDoctors);
    document.getElementById('department-filter').addEventListener('change', filterDoctors);
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
}

// Tab Management
function showTab(tab) {
    document.querySelectorAll('section').forEach(s => s.classList.add('hidden'));
    
    if (tab === 'doctors') {
        document.getElementById('doctors-section').classList.remove('hidden');
        loadDoctors();
    } else if (tab === 'appointments') {
        document.getElementById('appointments-section').classList.remove('hidden');
        loadAppointments();
    } else if (tab === 'chat') {
        document.getElementById('chat-section').classList.remove('hidden');
        loadChats();
    } else if (tab === 'records') {
        document.getElementById('records-section').classList.remove('hidden');
        loadMedicalRecords();
    }
}

// Patient Management
function buildDefaultPatientProfile(userId, customer = {}) {
    const fallbackProfiles = [
        {
            date_of_birth: '1995-04-12',
            gender: 'M',
            blood_type: 'O+',
            allergies: 'Penicillin',
            medical_history: 'Tung co viem xoang va tang can nhe.',
            emergency_contact: 'Nguyen Thi Lan',
            emergency_phone: '+84903110001',
        },
        {
            date_of_birth: '1988-09-23',
            gender: 'F',
            blood_type: 'A+',
            allergies: 'Hai voi hai san',
            medical_history: 'Co tien su tang huyet ap nhe.',
            emergency_contact: 'Tran Van Binh',
            emergency_phone: '+84903110002',
        },
        {
            date_of_birth: '2001-01-08',
            gender: 'M',
            blood_type: 'B+',
            allergies: '',
            medical_history: 'Thuong tap gym, can theo doi chan thuong co xuong.',
            emergency_contact: 'Le Thi Hoa',
            emergency_phone: '+84903110003',
        },
        {
            date_of_birth: '2019-07-15',
            gender: 'F',
            blood_type: 'AB+',
            allergies: 'Phan hoa moc',
            medical_history: 'Tre nho, da tiem chung co ban.',
            emergency_contact: 'Pham Van Hai',
            emergency_phone: '+84903110004',
        },
        {
            date_of_birth: '1992-11-30',
            gender: 'M',
            blood_type: 'A-',
            allergies: '',
            medical_history: 'Lam viec nhieu, hay met moi va can kiem tra suc khoe dinh ky.',
            emergency_contact: 'Le Thi Mai',
            emergency_phone: '+84903110005',
        },
    ];

    const numericId = Number.parseInt(userId, 10);
    const profile = Number.isFinite(numericId)
        ? fallbackProfiles[(numericId - 1) % fallbackProfiles.length]
        : fallbackProfiles[0];

    return {
        user_id: String(userId),
        name: customer.name || localStorage.getItem('userName') || `Patient ${userId}`,
        email: customer.email || `${String(userId)}@healthcare.local`,
        phone: customer.phone || '',
        ...profile,
    };
}

async function findPatientRecord(userId) {
    const response = await fetch(`${HEALTHCARE_API}/patients/?search=${encodeURIComponent(userId)}`);
    const data = await response.json();
    if (data.results && data.results.length > 0) {
        return data.results.find((patient) => String(patient.user_id) === String(userId)) || data.results[0];
    }
    return null;
}

async function syncPatientFromCustomerService(userId) {
    try {
        const response = await fetch(`http://localhost:8000/api/customers/`);
        const customers = await response.json();
        const customer = Array.isArray(customers)
            ? customers.find((item) => String(item.id) === String(userId))
            : null;

        if (!customer) {
            return null;
        }

        const existingPatient = await findPatientRecord(userId);
        if (existingPatient) {
            return existingPatient;
        }

        const payload = buildDefaultPatientProfile(userId, customer);
        const createResponse = await fetch(`${HEALTHCARE_API}/patients/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!createResponse.ok) {
            return null;
        }

        return await createResponse.json();
    } catch (error) {
        console.error('Failed to sync patient from customer service:', error);
        return null;
    }
}

async function loadPatientInfo() {
    try {
        const userId = getStoredUserId();
        if (!userId) {
            currentPatient = null;
            return;
        }

        currentPatient = await findPatientRecord(userId);
        if (currentPatient) {
            return;
        }

        currentPatient = await syncPatientFromCustomerService(userId);
    } catch (error) {
        console.error('Failed to load patient:', error);
    }
}

async function ensurePatientLoaded() {
    if (currentPatient) {
        return currentPatient;
    }

    const userId = getStoredUserId();
    if (!userId) {
        return null;
    }

    currentPatient = await findPatientRecord(userId);
    if (currentPatient) {
        return currentPatient;
    }

    currentPatient = await syncPatientFromCustomerService(userId);
    return currentPatient;
}

// Doctor Functions
async function loadDoctors() {
    try {
        const response = await fetch(`${HEALTHCARE_API}/doctors/?ordering=-rating`);
        const data = await response.json();
        renderDoctors(data.results || data);
    } catch (error) {
        console.error('Failed to load doctors:', error);
        document.getElementById('doctors-grid').innerHTML = 
            '<div class="text-center text-white py-12">Lỗi tải danh sách bác sĩ</div>';
    }
}

function renderDoctors(doctors) {
    const grid = document.getElementById('doctors-grid');
    
    if (!doctors || doctors.length === 0) {
        grid.innerHTML = '<div class="text-center text-white py-12">Không tìm thấy bác sĩ</div>';
        return;
    }

    grid.innerHTML = doctors.map(doctor => `
        <div class="glass rounded-lg p-6 doctor-card border border-transparent">
            <div class="flex items-start justify-between mb-4">
                <div class="w-16 h-16 bg-gradient-to-br from-red-400 to-pink-500 rounded-lg flex items-center justify-center text-white text-2xl">
                    <i class="fas fa-user-md"></i>
                </div>
                <div class="flex gap-1">
                    ${Array(5).fill().map((_, i) => `
                        <i class="fas fa-star text-${i < Math.floor(doctor.rating) ? 'yellow' : 'gray'}-400"></i>
                    `).join('')}
                </div>
            </div>
            
            <h3 class="text-lg font-bold mb-1">BS. ${doctor.name}</h3>
            <p class="text-sm text-red-500 font-medium mb-2">${getDepartmentName(doctor.department)}</p>
            <p class="text-sm text-gray-600 mb-3">${doctor.specialization}</p>
            
            <div class="text-sm text-gray-500 mb-4">
                <i class="fas fa-briefcase mr-1"></i> ${doctor.experience_years} năm kinh nghiệm
            </div>
            
            <p class="text-sm text-gray-700 mb-4 line-clamp-2">${doctor.bio || 'Bác sĩ tài năng'}</p>
            
            <div class="flex gap-2">
                <button onclick="selectDoctor('${doctor.id}')" 
                        class="flex-1 bg-red-500 text-white py-2 rounded-lg hover:bg-red-600 font-medium">
                    <i class="fas fa-calendar-plus mr-1"></i>Đặt lịch
                </button>
                <button onclick="startChatWithDoctor('${doctor.id}')" 
                        class="flex-1 bg-gray-200 text-gray-700 py-2 rounded-lg hover:bg-gray-300 font-medium">
                    <i class="fas fa-comment mr-1"></i>Chat
                </button>
            </div>
        </div>
    `).join('');
}

function getDepartmentName(dept) {
    const depts = {
        'cardiology': 'Tim mạch',
        'dermatology': 'Da liễu',
        'neurology': 'Thần kinh',
        'pediatrics': 'Nhi khoa',
        'orthopedics': 'Chỉnh hình',
        'psychiatry': 'Tâm thần',
        'general': 'Khám tổng quát',
        'dentistry': 'Nha khoa'
    };
    return depts[dept] || dept;
}

function filterDoctors() {
    loadDoctors();
}

async function selectDoctor(doctorId) {
    const patient = await ensurePatientLoaded();
    if (!patient) {
        alert('Vui lòng đăng nhập');
        return;
    }
    
    localStorage.setItem('selected_doctor_id', doctorId);
    document.getElementById('appointment-modal').classList.remove('hidden');
}

async function bookAppointment(event) {
    event.preventDefault();

    const patient = await ensurePatientLoaded();
    if (!patient) {
        alert('Vui lòng đăng nhập');
        return;
    }

    const doctorId = localStorage.getItem('selected_doctor_id');
    const scheduledDate = document.getElementById('appointment-date').value;
    const reason = document.getElementById('appointment-reason').value;

    try {
        const response = await fetch(`${HEALTHCARE_API}/appointments/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient: patient.id,
                doctor: doctorId,
                scheduled_date: new Date(scheduledDate).toISOString(),
                reason: reason,
                appointment_type: 'consultation',
                location: 'Phòng khám'
            })
        });

        if (response.ok) {
            alert('Đặt lịch hẹn thành công!');
            closeModal('appointment-modal');
            loadAppointments();
        }
    } catch (error) {
        console.error('Error booking appointment:', error);
        alert('Không thể đặt lịch hẹn');
    }
}

// Appointment Functions
async function loadAppointments() {
    const patient = await ensurePatientLoaded();
    if (!patient) return;

    try {
        const response = await fetch(`${HEALTHCARE_API}/appointments/?ordering=-scheduled_date`);
        const data = await response.json();
        const appointments = (data.results || data).filter(a => a.patient === patient.id);
        renderAppointments(appointments);
    } catch (error) {
        console.error('Failed to load appointments:', error);
    }
}

function renderAppointments(appointments) {
    const list = document.getElementById('appointments-list');
    
    if (!appointments || appointments.length === 0) {
        list.innerHTML = `
            <div class="text-center text-white py-12">
                <i class="fas fa-calendar text-3xl mb-2 block"></i>
                <p>Bạn chưa có lịch hẹn nào</p>
            </div>
        `;
        return;
    }

    list.innerHTML = appointments.map(apt => `
        <div class="glass rounded-lg p-6">
            <div class="flex justify-between items-start mb-4">
                <div>
                    <h3 class="text-lg font-bold">BS. ${apt.doctor_name}</h3>
                    <p class="text-sm text-gray-600">${apt.appointment_type === 'consultation' ? 'Tư vấn' : apt.appointment_type}</p>
                </div>
                <span class="px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(apt.status)}">
                    ${getStatusName(apt.status)}
                </span>
            </div>
            
            <div class="space-y-2 text-sm text-gray-600 mb-4">
                <div><i class="fas fa-calendar-alt mr-2 text-red-500"></i>${new Date(apt.scheduled_date).toLocaleString('vi-VN')}</div>
                <div><i class="fas fa-clock mr-2 text-red-500"></i>${apt.duration_minutes} phút</div>
                <div><i class="fas fa-map-marker mr-2 text-red-500"></i>${apt.location}</div>
                <div><i class="fas fa-stethoscope mr-2 text-red-500"></i>${apt.reason}</div>
            </div>

            <div class="flex gap-2">
                ${apt.status === 'pending' ? `
                    <button onclick="confirmAppointment('${apt.id}')" class="flex-1 bg-green-500 text-white py-2 rounded-lg hover:bg-green-600">
                        <i class="fas fa-check mr-1"></i>Xác nhận
                    </button>
                    <button onclick="cancelAppointment('${apt.id}')" class="flex-1 bg-red-500 text-white py-2 rounded-lg hover:bg-red-600">
                        <i class="fas fa-times mr-1"></i>Hủy
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function getStatusColor(status) {
    const colors = {
        'pending': 'bg-yellow-100 text-yellow-800',
        'confirmed': 'bg-blue-100 text-blue-800',
        'completed': 'bg-green-100 text-green-800',
        'cancelled': 'bg-red-100 text-red-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
}

function getStatusName(status) {
    const names = {
        'pending': 'Chờ xác nhận',
        'confirmed': 'Đã xác nhận',
        'in_progress': 'Đang khám',
        'completed': 'Hoàn thành',
        'cancelled': 'Đã hủy'
    };
    return names[status] || status;
}

async function confirmAppointment(appointmentId) {
    try {
        const response = await fetch(`${HEALTHCARE_API}/appointments/${appointmentId}/confirm/`, {
            method: 'POST'
        });
        if (response.ok) {
            alert('Xác nhận lịch hẹn thành công');
            loadAppointments();
        }
    } catch (error) {
        console.error('Error confirming appointment:', error);
    }
}

async function cancelAppointment(appointmentId) {
    if (confirm('Bạn chắc chắn muốn hủy lịch hẹn?')) {
        try {
            const response = await fetch(`${HEALTHCARE_API}/appointments/${appointmentId}/cancel/`, {
                method: 'POST'
            });
            if (response.ok) {
                alert('Hủy lịch hẹn thành công');
                loadAppointments();
            }
        } catch (error) {
            console.error('Error cancelling appointment:', error);
        }
    }
}

// Chat Functions
async function startNewChat() {
    const patient = await ensurePatientLoaded();
    if (!patient) {
        alert('Vui lòng đăng nhập');
        return;
    }

    const subject = prompt('Tiêu đề cuộc hội thoại:');
    if (!subject) return;

    try {
        const response = await fetch(`${HEALTHCARE_API}/chats/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient: patient.id,
                subject: subject
            })
        });

        if (response.ok) {
            currentChat = await response.json();
            loadChats();
        }
    } catch (error) {
        console.error('Error creating chat:', error);
    }
}

async function startChatWithDoctor(doctorId) {
    const patient = await ensurePatientLoaded();
    if (!patient) {
        alert('Vui lòng đăng nhập');
        return;
    }

    try {
        const response = await fetch(`${HEALTHCARE_API}/chats/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                patient: patient.id,
                doctor: doctorId,
                subject: 'Tư vấn trực tiếp'
            })
        });

        if (response.ok) {
            currentChat = await response.json();
            showTab('chat');
            loadChats();
        }
    } catch (error) {
        console.error('Error creating chat:', error);
    }
}

async function loadChats() {
    const patient = await ensurePatientLoaded();
    if (!patient) return;

    try {
        const response = await fetch(`${HEALTHCARE_API}/chats/`);
        const data = await response.json();
        const chats = (data.results || data).filter(c => c.patient === patient.id && c.is_active);
        renderChatList(chats);
    } catch (error) {
        console.error('Failed to load chats:', error);
    }
}

function renderChatList(chats) {
    const chatList = document.getElementById('chat-list');
    
    if (!chats || chats.length === 0) {
        chatList.innerHTML = '<div class="text-center text-gray-400 py-8">Không có cuộc hội thoại</div>';
        return;
    }

    chatList.innerHTML = chats.map(chat => `
        <div onclick="selectChat('${chat.id}')" 
             class="p-3 bg-gray-100 rounded-lg cursor-pointer hover:bg-gray-200 transition">
            <div class="font-medium text-sm">${chat.subject}</div>
            <div class="text-xs text-gray-500 mt-1">
                ${chat.doctor_name ? 'BS. ' + chat.doctor_name : 'Cuộc hội thoại'}
            </div>
        </div>
    `).join('');
}

async function selectChat(chatId) {
    try {
        const response = await fetch(`${HEALTHCARE_API}/chats/${chatId}/`);
        currentChat = await response.json();
        renderChatMessages(currentChat.messages || []);
    } catch (error) {
        console.error('Error loading chat:', error);
    }
}

function renderChatMessages(messages) {
    const messagesContainer = document.getElementById('chat-messages');
    
    if (!messages || messages.length === 0) {
        messagesContainer.innerHTML = '<div class="text-center text-gray-400 py-8">Bắt đầu cuộc hội thoại</div>';
        return;
    }

    messagesContainer.innerHTML = messages.map(msg => {
        const isPatient = msg.sender_role === 'patient';
        return `
            <div class="flex ${isPatient ? 'justify-end' : 'justify-start'}">
                <div class="chat-bubble ${isPatient ? 'bg-red-500 text-white' : 'bg-gray-200 text-gray-800'} rounded-lg p-3">
                    <p>${msg.message}</p>
                    <div class="text-xs ${isPatient ? 'text-red-100' : 'text-gray-500'} mt-1">
                        ${new Date(msg.created_at).toLocaleTimeString('vi-VN')}
                    </div>
                </div>
            </div>
        `;
    }).join('');

    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

async function sendMessage() {
    if (!currentChat) {
        alert('Chọn cuộc hội thoại trước');
        return;
    }

    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;

    try {
        const response = await fetch(`${HEALTHCARE_API}/chats/${currentChat.id}/send_message/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                sender_role: 'patient'
            })
        });

        if (response.ok) {
            input.value = '';
            selectChat(currentChat.id);
        }
    } catch (error) {
        console.error('Error sending message:', error);
    }
}

// Medical Records
async function loadMedicalRecords() {
    const patient = await ensurePatientLoaded();
    if (!patient) return;

    try {
        const response = await fetch(`${HEALTHCARE_API}/medical-records/?patient_id=${patient.id}`);
        const data = await response.json();
        renderMedicalRecords(data.results || data);
    } catch (error) {
        console.error('Failed to load medical records:', error);
    }
}

function renderMedicalRecords(records) {
    const grid = document.getElementById('records-grid');
    
    if (!records || records.length === 0) {
        grid.innerHTML = `
            <div class="text-center text-white py-12">
                <i class="fas fa-file-medical text-3xl mb-2 block"></i>
                <p>Bạn chưa có hồ sơ y tế nào</p>
            </div>
        `;
        return;
    }

    grid.innerHTML = records.map(record => `
        <div class="glass rounded-lg p-6">
            <div class="flex justify-between items-start mb-3">
                <h3 class="text-lg font-bold">${record.title}</h3>
                <span class="px-2 py-1 bg-red-100 text-red-700 text-xs rounded font-medium">
                    ${getRecordTypeName(record.record_type)}
                </span>
            </div>
            
            <p class="text-sm text-gray-600 mb-3">${record.description}</p>
            
            <div class="text-sm text-gray-500 space-y-1 mb-4">
                <div><i class="fas fa-user-md mr-2 text-red-500"></i>BS. ${record.doctor_name}</div>
                <div><i class="fas fa-calendar mr-2 text-red-500"></i>${new Date(record.created_at).toLocaleString('vi-VN')}</div>
            </div>

            ${record.findings ? `<p class="text-sm text-gray-700 mb-2"><strong>Kết quả:</strong> ${record.findings}</p>` : ''}
            ${record.treatment_plan ? `<p class="text-sm text-gray-700"><strong>Kế hoạch:</strong> ${record.treatment_plan}</p>` : ''}
        </div>
    `).join('');
}

function getRecordTypeName(type) {
    const names = {
        'diagnosis': 'Chuẩn đoán',
        'prescription': 'Đơn thuốc',
        'lab_result': 'Xét nghiệm',
        'imaging': 'Hình ảnh',
        'surgery_report': 'Phẫu thuật',
        'vaccination': 'Tiêm chủng'
    };
    return names[type] || type;
}

// Modal Management
function closeModal(modalId) {
    document.getElementById(modalId).classList.add('hidden');
}

function logout() {
    localStorage.clear();
    window.location.href = 'index.html';
}
