import { reactive, computed } from 'vue'
import http from '../components/http'

// Days of the week constant
export const DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

// Shared state across all components
export const state = reactive({
  patients: [],
  doctors: [],
  schedules: [],
  appointments: [],
  medicalRecords: [],
  prescriptions: [],
  billings: [],
  departments: [],
  recentActivities: [],
  specializations: [],
  offices: [],
  loading: {
    patients: false,
    doctors: false,
    schedules: false,
    appointments: false,
    specializations: false,
    general: false
  },

  errors: {
    patients: null,
    doctors: null,
    schedules: null,
    appointments: null,
    general: null
  },

  currentUser: null,
  userType: null
})

// ==================== UTILITY FUNCTIONS ====================

export function generateTimeSlots(startTime, endTime, appointmentCount) {
  const slots = []
  if (!startTime || !endTime || !appointmentCount) return slots

  const slotDuration = calculateSlots(startTime, endTime, appointmentCount)
  if (slotDuration <= 0) return slots

  const [startHour, startMin] = startTime.split(':').map(Number)
  let currentMinutes = startHour * 60 + startMin
  const endMinutes = endTime.split(':').map(Number).reduce((a, b) => a * 60 + b, 0)

  for (let i = 0; i < appointmentCount; i++) {
    if (currentMinutes >= endMinutes) break
    const hours = Math.floor(currentMinutes / 60)
    const mins = currentMinutes % 60
    slots.push(`${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`)
    currentMinutes += slotDuration
  }

  return slots
}

export function calculateSlots(startTime, endTime, appointmentCount) {
  if (!startTime || !endTime || !appointmentCount) return 0

  const [startHour, startMin] = startTime.split(':').map(Number)
  const [endHour, endMin] = endTime.split(':').map(Number)

  const startMinutes = startHour * 60 + startMin
  const endMinutes = endHour * 60 + endMin

  if (endMinutes <= startMinutes || appointmentCount <= 0) return 0

  return Math.floor((endMinutes - startMinutes) / appointmentCount)
}

export function handleApiError(error, context = 'Operation') {
  console.error(`${context} failed:`, error)
  const message = error.response?.data?.detail || error.message || 'Unknown error occurred'
  state.errors.general = message
  throw new Error(message)
}

// ==================== AUTH FUNCTIONS ====================

export const login = async (email, password) => {
  try {
    state.loading.general = true
    state.errors.general = null

    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)

    const response = await http.post('/api/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    })

    const { access_token, user_type } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('user_type', user_type)
    state.userType = user_type

    return response
  } catch (error) {
    const message = error.response?.data?.detail || error.message || 'Ошибка авторизации'
    state.errors.general = message
    console.error('Login failed:', message)
    return null
  } finally {
    state.loading.general = false
  }
}

export const logout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('user_type')
  localStorage.removeItem('currentUser')
  state.currentUser = null
  state.userType = null
  state.patients = []
  state.doctors = []
  state.schedules = []
  state.appointments = []
}

// ==================== HELPER FUNCTIONS ====================

export const getPatientName = (id) => {
  const patient = state.patients.find(p => p.id === id)
  if (patient) {
    return `${patient.last_name} ${patient.first_name} ${patient.patronymic || ''}`.trim()
  }
  return 'Unknown'
}

export const getPatientById = (id) => {
  return state.patients.find(p => p.id === id)
}

export const getPatientByEmail = (email) => {
  return state.patients.find(p => p.email === email)
}

export const getDoctorName = (id) => {
  const doctor = state.doctors.find(d => d.id === id)
  console.log(doctor)
  if (doctor) {
    return `${doctor.name}`.trim()
  }
  return 'Unknown'
}

export const buildDoctorName = (doctor) => {
  return `${doctor.first_name} ${doctor.last_name} ${doctor.patronymic}`
}

export const getDoctorById = (id) => {
  return state.doctors.find(d => d.id === id)
}

export const getDoctorByEmail = (email) => {
  return state.doctors.find(d => d.email === email)
}

export const getDoctorSpecialization = (id) => {
  const doctor = state.doctors.find(d => d.id === id)
  if (doctor && doctor.specialization) {
    return doctor.specialization.name || doctor.specialization
  }
  return 'Unknown'
}

// ==================== BASE COMPOSABLE ====================

export function useHospitalCore() {
  return {
    DAYS_OF_WEEK,

    // Computed states
    patients: computed(() => state.patients),
    doctors: computed(() => state.doctors),
    schedules: computed(() => state.schedules),
    appointments: computed(() => state.appointments),
    medicalRecords: computed(() => state.medicalRecords),
    prescriptions: computed(() => state.prescriptions),
    billings: computed(() => state.billings),
    departments: computed(() => state.departments),
    recentActivities: computed(() => state.recentActivities),
    specializations: computed(() => state.specializations),
    loading: computed(() => state.loading),
    errors: computed(() => state.errors),
    userType: computed(() => state.userType),

    // Auth
    login,
    logout,

    // Getters
    buildDoctorName,
    getPatientName,
    getPatientById,
    getPatientByEmail,
    getDoctorName,
    getDoctorById,
    getDoctorByEmail,
    getDoctorSpecialization,

    // Utilities
    generateTimeSlots,
    calculateSlots,
  }
}
