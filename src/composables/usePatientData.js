import { computed } from 'vue'
import http from '../components/http'
import { state, handleApiError, useHospitalCore } from './useHospitalCore'

export function usePatientData() {
  const core = useHospitalCore()

  // ==================== FETCH FUNCTIONS ====================

  const fetchDoctors = async () => {
    try {
      state.loading.doctors = true
      state.errors.doctors = null
      const response = await http.get('/api/patient/doctors')
      state.doctors = response.data.map((doctor) => ({
        id: doctor.id,
        name: `${doctor.first_name} ${doctor.last_name} ${doctor.patronymic || ''}`.trim(),
        specialization: doctor.specialization.name
      }))
      return response.data
    } catch (error) {
      state.errors.doctors = error.response?.data?.detail || error.message
      console.error('Failed to fetch doctors:', error)
      return []
    } finally {
      state.loading.doctors = false
    }
  }

  const fetchDoctorSchedule = async (doctorId) => {
    try {
      state.loading.schedules = true
      const response = await http.get(`/api/patient/schedule/${doctorId}`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch doctor schedule:', error)
      return []
    } finally {
      state.loading.schedules = false
    }
  }

  // ==================== REGISTRATION ====================

  const registerPatient = async (patientData) => {
    try {
      state.loading.general = true
      const response = await http.post('/api/patient/register', patientData)
      const { access_token, user_type } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('user_type', user_type)
      state.userType = user_type
      return response.data
    } catch (error) {
      handleApiError(error, 'Patient registration')
    } finally {
      state.loading.general = false
    }
  }

  // ==================== APPOINTMENTS ====================

  const getPatientAppointments = async (statusFilter = null) => {
    try {
      state.loading.appointments = true
      const url = statusFilter
        ? `/api/patient/appointments?status_filter=${statusFilter}`
        : '/api/patient/appointments'
      const response = await http.get(url)
      return response.data
    } catch (error) {
      console.error('Failed to fetch patient appointments:', error)
      return []
    } finally {
      state.loading.appointments = false
    }
  }

  const getPatientUpcomingAppointments = async () => {
    return await getPatientAppointments('scheduled')
  }

  const getPatientCompletedAppointments = async () => {
    return await getPatientAppointments('completed')
  }

  const addAppointment = async (scheduleId) => {
    try {
      state.loading.appointments = true
      const response = await http.post(`/api/patient/appointments/${scheduleId}`, {})
      return response.data
    } catch (error) {
      handleApiError(error, 'Create appointment')
    } finally {
      state.loading.appointments = false
    }
  }

  const cancelAppointment = async (appointmentId) => {
    try {
      const response = await http.delete(`/api/patient/appointments/${appointmentId}`)
      return response.data
    } catch (error) {
      handleApiError(error, 'Cancel appointment')
    }
  }

  // ==================== SCHEDULE HELPERS ====================

  const getAvailableSlots = async (doctorId, date) => {
    try {
      const schedules = await fetchDoctorSchedule(doctorId)
      const dateSchedules = schedules.filter(s => s.date === date && s.is_available)
      return dateSchedules
    } catch (error) {
      console.error('Failed to get available slots:', error)
      return []
    }
  }

  const getDoctorScheduledDates = async (doctorId) => {
    try {
      const schedules = await fetchDoctorSchedule(doctorId)
      return [...new Set(schedules.map(s => s.date))]
    } catch (error) {
      console.error('Failed to get scheduled dates:', error)
      return []
    }
  }

  const doctorHasScheduleOnDate = async (doctorId, date) => {
    const schedules = await fetchDoctorSchedule(doctorId)
    return schedules.some(s => s.date === date && s.is_available)
  }

  // ==================== MEDICATION ====================

  const getPatientMedication = async () => {
    try {
      const response = await http.get('/api/patient/medication')
      return response.data
    } catch (error) {
      console.error('Failed to fetch patient medication:', error)
      return null
    }
  }

  // ==================== COMPUTED FROM STATE ====================

  const getPatientMedicalRecords = (patientId) => {
    return computed(() => state.medicalRecords.filter(r => r.patient_id === patientId))
  }

  const getPatientPrescriptions = (patientId) => {
    return computed(() => state.prescriptions.filter(p => p.patient_id === patientId))
  }

  const getPatientBillings = (patientId) => {
    return computed(() => state.billings.filter(b => b.patient_id === patientId))
  }

  // ==================== INITIALIZATION ====================

  const initializeData = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      state.userType = 'patient'
      try {
        await fetchDoctors()
      } catch (error) {
        console.error('Failed to initialize patient data:', error)
      }
    }
  }

  return {
    ...core,

    // Fetch
    fetchDoctors,
    fetchDoctorSchedule,
    initializeData,

    // Registration
    registerPatient,

    // Appointments
    getPatientAppointments,
    getPatientUpcomingAppointments,
    getPatientCompletedAppointments,
    addAppointment,
    cancelAppointment,

    // Schedule
    getAvailableSlots,
    getDoctorScheduledDates,
    doctorHasScheduleOnDate,

    // Medication
    getPatientMedication,

    // Computed
    getPatientMedicalRecords,
    getPatientPrescriptions,
    getPatientBillings
  }
}
