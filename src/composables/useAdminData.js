import { computed } from 'vue'
import http from '../components/http'
import {
  state,
  handleApiError,
  useHospitalCore,
  DAYS_OF_WEEK,
  generateTimeSlots,
  calculateSlots
} from './useHospitalCore'

export function useAdminData() {
  const core = useHospitalCore()

  // ==================== FETCH FUNCTIONS ====================

  const fetchPatients = async () => {
    try {
      state.loading.patients = true
      state.errors.patients = null
      const response = await http.get('/api/admin/patients')
      state.patients = response.data
      return response.data
    } catch (error) {
      state.errors.patients = error.response?.data?.detail || error.message
      console.error('Failed to fetch patients:', error)
      return []
    } finally {
      state.loading.patients = false
    }
  }
  const fetchAdminDoctorSchedule = async (doctorId) => {
        try {
            const response = await http.get(`/api/admin/schedule/${doctorId}`)
            return response.data.map(schedule => ({
                id: schedule.id,
                doctor_id: schedule.doctor_id,
                date: schedule.date,
                startTime: schedule.start_time,
                endTime: schedule.end_time,
                appointmentCount: schedule.slots_count,
                bookedCount: schedule.booked_count || 0,
                officeNumber: schedule.office_number,
                isActive: schedule.is_available ?? true
            }))
        } catch (error) {
            console.error(`Failed to fetch schedule for doctor ${doctorId}:`, error)
            return []
        }
    }
  const fetchDoctors = async () => {
    try {
      state.loading.doctors = true
      state.errors.doctors = null
      const response = await http.get('/api/admin/doctors')

      state.doctors = response.data.map((doctor) => ({
        id: doctor.id,
        first_name: doctor.first_name,
        last_name: doctor.last_name,
        patronymic: doctor.patronymic || '',
        name: `${doctor.first_name} ${doctor.last_name} ${doctor.patronymic || ''}`.trim(),
        specialization: doctor.specialization.name,
      }))

      return response.data
    } catch (error) {
      state.errors.doctors = error.response?.data?.detail || error.message
      console.error('Failed to fetch doctors (admin):', error)
      return []
    } finally {
      state.loading.doctors = false
    }
  }

  const fetchSpecializations = async () => {
    try {
      state.loading.specializations = true
      const response = await http.get('/api/admin/specializations')
      state.specializations = response.data
      return response.data
    } catch (error) {
      console.error('Failed to fetch specializations:', error)
      return []
    } finally {
      state.loading.specializations = false
    }
  }

  const fetchAppointments = async () => {
    try {
      state.loading.appointments = true
      state.errors.appointments = null
      const response = await http.get('/api/admin/appointments')
      state.appointments = response.data
      return response.data
    } catch (error) {
      state.errors.appointments = error.response?.data?.detail || error.message
      console.error('Failed to fetch appointments:', error)
      return []
    } finally {
      state.loading.appointments = false
    }
  }

  const fetchDoctorSchedule = async (doctorId) => {
    try {
      const response = await http.get(`/api/admin/schedule/${doctorId}`)
      return response.data.map(schedule => ({
        id: schedule.id,
        doctor_id: schedule.doctor_id,
        date: schedule.date,
        startTime: schedule.start_time,
        endTime: schedule.end_time,
        appointmentCount: schedule.slots_count,
        bookedCount: schedule.booked_count || 0,
        officeNumber: schedule.office_number,
        isActive: schedule.is_available ?? true
      }))
    } catch (error) {
      console.error(`Failed to fetch schedule for doctor ${doctorId}:`, error)
      return []
    }
  }

  // ==================== COMPUTED ====================

  const todayAppointments = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return state.appointments.filter(a => a.date === today).length
  })

  const scheduledToday = computed(() => {
    const today = new Date().toISOString().split('T')[0]
    return state.appointments.filter(a => a.date === today && a.status === 'scheduled').length
  })

  const totalRevenue = computed(() => {
    return state.billings
      .filter(b => b.status === 'Paid')
      .reduce((sum, b) => sum + b.amount, 0)
  })

  const monthlyRevenue = computed(() => {
    const currentMonth = new Date().getMonth()
    return state.billings
      .filter(b => {
        const billMonth = new Date(b.date).getMonth()
        return b.status === 'Paid' && billMonth === currentMonth
      })
      .reduce((sum, b) => sum + b.amount, 0)
  })

  // ==================== SPECIALIZATIONS ====================

  const addSpecialization = async (specialization) => {
    try {
      const response = await http.post('/api/admin/specializations', specialization)
      await fetchSpecializations()
      return response.data
    } catch (error) {
      handleApiError(error, 'Add specialization')
    }
  }

  // ==================== SCHEDULE FUNCTIONS ====================

  const getDoctorSchedules = (doctorId) => {
    return computed(() => state.schedules.filter(s => s.doctor_id === doctorId))
  }

  const getAllSchedules = () => {
    return computed(() => state.schedules)
  }

  const addSchedule = async (schedule) => {
    try {
      const response = await http.post('/api/admin/schedule', schedule)
      return response.data
    } catch (error) {
      handleApiError(error, 'Add schedule')
    }
  }

  const addScheduleBatch = async (batchSchedule) => {
    try {
      const response = await http.post('/api/admin/schedule/batch', batchSchedule)
      return response.data
    } catch (error) {
      handleApiError(error, 'Add batch schedule')
    }
  }

  const updateSchedule = async (id, data) => {
    try {
      const response = await http.put(`/api/admin/schedule/${id}`, data)
      return response.data
    } catch (error) {
      handleApiError(error, 'Update schedule')
    }
  }

  const deleteSchedule = async (id) => {
    try {
      await http.delete(`/api/admin/schedule/${id}`)
    } catch (error) {
      handleApiError(error, 'Delete schedule')
    }
  }

  const toggleScheduleStatus = async (id) => {
    try {
      const response = await http.patch(`/api/admin/schedules/${id}/`)
      return response.data
    } catch (error) {
      handleApiError(error, 'Toggle schedule status')
    }
  }

  const getAppointmentCount = (scheduleId) => {
    return state.appointments.filter(a =>
      a.schedule_id === scheduleId &&
      a.status !== 'cancelled'
    ).length
  }

  // ==================== CRUD - PATIENTS ====================

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

  const addPatient = async (patient) => {
    return await registerPatient(patient)
  }

  const updatePatient = async (id, data) => {
    try {
      const response = await http.put(`/api/admin/patient/${id}`, data)
      await fetchPatients()
      return response.data
    } catch (error) {
      handleApiError(error, 'Update patient')
    }
  }

  const deletePatient = async (id) => {
    try {
      await http.delete(`/api/admin/patient/${id}`)
      await fetchPatients()
    } catch (error) {
      handleApiError(error, 'Delete patient')
    }
  }

  // ==================== CRUD - DOCTORS ====================

  const addDoctor = async (doctor) => {
    try {
      state.loading.general = true
      const response = await http.post('/api/admin/doctor', doctor)
      await fetchDoctors()
      return response.data
    } catch (error) {
      handleApiError(error, 'Add doctor')
    } finally {
      state.loading.general = false
    }
  }

  const updateDoctor = async (id, data) => {
    try {
      const response = await http.put(`/api/admin/doctor/${id}`, data)
      await fetchDoctors()
      return response.data
    } catch (error) {
      handleApiError(error, 'Update doctor')
    }
  }

  const deleteDoctor = async (id) => {
    try {
      await http.delete(`/api/admin/doctor/${id}`)
      await fetchDoctors()
    } catch (error) {
      handleApiError(error, 'Delete doctor')
    }
  }

  const searchDoctors = async (searchTerm) => {
    try {
      const response = await http.get(`/api/admin/doctors/search/${searchTerm}`)
      return response.data
    } catch (error) {
      console.error('Failed to search doctors:', error)
      return []
    }
  }

  // ==================== CRUD - APPOINTMENTS ====================

  const deleteAppointment = async (id) => {
    try {
      await http.delete(`/api/admin/appointments/${id}`)
      await fetchAppointments()
    } catch (error) {
      handleApiError(error, 'Delete appointment')
    }
  }

  // ==================== CRUD - BILLING ====================

  const addBilling = async (billing) => {
    try {
      const response = await http.post('/api/admin/billings', billing)
      return response.data
    } catch (error) {
      handleApiError(error, 'Add billing')
    }
  }

  const markBillingPaid = async (id) => {
    try {
      const response = await http.patch(`/api/admin/billings/${id}/pay`)
      return response.data
    } catch (error) {
      handleApiError(error, 'Mark billing paid')
    }
  }

  // ==================== INITIALIZATION ====================

  const initializeData = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      state.userType = 'admin'
      try {
        await Promise.all([
          fetchPatients(),
          fetchDoctors(),
          fetchAppointments(),
          fetchSpecializations()
        ])
      } catch (error) {
        console.error('Failed to initialize admin data:', error)
      }
    }
  }

  return {
    ...core,

    // Computed
    todayAppointments,
    scheduledToday,
    totalRevenue,
    monthlyRevenue,

    // Fetch
    fetchPatients,
    fetchDoctors,
    fetchAppointments,
    fetchSpecializations,
    fetchDoctorSchedule,
    initializeData,

    // Specializations
    addSpecialization,

    // Schedule
    getDoctorSchedules,
    getAllSchedules,
    addSchedule,
    addScheduleBatch,
    updateSchedule,
    deleteSchedule,
    toggleScheduleStatus,
    getAppointmentCount,

    // Patients CRUD
    addPatient,
    updatePatient,
    deletePatient,

    // Doctors CRUD
    addDoctor,
    updateDoctor,
    deleteDoctor,
    searchDoctors,

    // Appointments
    deleteAppointment,

    // Billing
    addBilling,
    markBillingPaid,
    fetchAdminDoctorSchedule
  }
}
