import { computed } from 'vue'
import http from '../components/http'
import { state, handleApiError, useHospitalCore } from './useHospitalCore'

export function useDoctorData() {
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

  // ==================== APPOINTMENTS ====================

  const getDoctorAppointments = async (statusFilter = null) => {
    try {
      state.loading.appointments = true
      const url = statusFilter
        ? `/api/doctor/appointments?status_filter=${statusFilter}`
        : '/api/doctor/appointments'
      const response = await http.get(url)
      return response.data
    } catch (error) {
      console.error('Failed to fetch doctor appointments:', error)
      return []
    } finally {
      state.loading.appointments = false
    }
  }

  const getDoctorTodayAppointments = async () => {
    const appointments = await getDoctorAppointments()
    const today = new Date().toISOString().split('T')[0]
    return appointments.filter(a => a.schedule?.date === today)
  }

  const updateAppointmentStatus = async (appointmentId, updateData) => {
    try {
      const response = await http.put(`/api/doctor/appointments/${appointmentId}`, updateData)
      return response.data
    } catch (error) {
      handleApiError(error, 'Update appointment')
    }
  }

  // ==================== PATIENTS ====================

  const getDoctorPatients = (doctorId) => {
    return computed(() => {
      const patientIds = [...new Set(
        state.appointments
          .filter(a => a.doctor_id === doctorId)
          .map(a => a.patient_id)
      )]
      return state.patients.filter(p => patientIds.includes(p.id))
    })
  }

  const getPatientMedicationReport = async (patientId) => {
    try {
      const response = await http.get(`/api/doctor/patients/${patientId}/medication`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch patient medication report:', error)
      return null
    }
  }

  const getPatientMedicaments = async (patientId) => {
    try {
      const response = await http.get(`/api/doctor/patients/${patientId}/medicaments`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch patient medicaments:', error)
      return []
    }
  }

  const getPatientActiveMedicaments = async (patientId) => {
    try {
      const response = await http.get(`/api/doctor/patients/${patientId}/medicaments/active`)
      return response.data
    } catch (error) {
      console.error('Failed to fetch active medicaments:', error)
      return []
    }
  }

  // ==================== PRESCRIPTIONS ====================

  const getDoctorPrescriptions = (doctorId) => {
    return computed(() => state.prescriptions.filter(p => p.doctor_id === doctorId))
  }

  const addPrescription = async (prescription) => {
    try {
      const response = await http.post('/api/doctor/prescriptions', prescription)
      return response.data
    } catch (error) {
      handleApiError(error, 'Add prescription')
    }
  }

  const updatePrescription = async (id, data) => {
    try {
      const response = await http.put(`/api/doctor/prescriptions/${id}`, data)
      return response.data
    } catch (error) {
      handleApiError(error, 'Update prescription')
    }
  }

  const deletePrescription = async (id) => {
    try {
      await http.delete(`/api/doctor/prescriptions/${id}`)
    } catch (error) {
      handleApiError(error, 'Delete prescription')
    }
  }

  // ==================== MEDICAMENTS & CONTRAINDICATIONS ====================

  const addMedicamentsForAppointment = async (appointmentId, medicaments) => {
    try {
      const response = await http.post(
        `/api/doctor/appointments/${appointmentId}/medicaments`,
        { medicaments }
      )
      return response.data
    } catch (error) {
      handleApiError(error, 'Add medicaments')
    }
  }

  const addMedicamentContraindications = async (medicamentName, contradictions) => {
    try {
      const response = await http.post('/api/doctor/medicaments/contraindications', {
        medicament_name: medicamentName,
        contradictions
      })
      return response.data
    } catch (error) {
      handleApiError(error, 'Add medicament contraindications')
    }
  }

  const getMedicamentContraindications = async (medicamentName = null) => {
    try {
      const url = medicamentName
        ? `/api/doctor/medicaments/contraindications?medicament_name=${encodeURIComponent(medicamentName)}`
        : '/api/doctor/medicaments/contraindications'
      const response = await http.get(url)
      return response.data
    } catch (error) {
      console.error('Failed to get contraindications:', error)
      return []
    }
  }

  const deleteMedicamentContraindication = async (medicamentName, contradiction) => {
    try {
      const response = await http.delete('/api/doctor/medicaments/contraindications', {
        medicament_name: medicamentName,
        contradictions: contradiction
      })
      return response.data
    } catch (error) {
      handleApiError(error, 'Delete contraindication')
    }
  }

  const addPatientContraindications = async (patientId, contradictions) => {
    try {
      const response = await http.post(
        `/api/doctor/patients/${patientId}/contraindications`,
        { contradictions }
      )
      return response.data
    } catch (error) {
      handleApiError(error, 'Add patient contraindications')
    }
  }

  const deletePatientContraindication = async (patientId, contradiction) => {
    try {
      const response = await http.delete(
        `/api/doctor/patients/${patientId}/contraindications`,
        { contradiction }
      )
      return response.data
    } catch (error) {
      handleApiError(error, 'Delete patient contraindication')
    }
  }

  // ==================== INITIALIZATION ====================

  const initializeData = async () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      state.userType = 'doctor'
      try {
        await fetchDoctors()
      } catch (error) {
        console.error('Failed to initialize doctor data:', error)
      }
    }
  }

  return {
    ...core,

    // Fetch
    fetchDoctors,
    initializeData,

    // Appointments
    getDoctorAppointments,
    getDoctorTodayAppointments,
    updateAppointmentStatus,

    // Patients
    getDoctorPatients,
    getPatientMedicationReport,
    getPatientMedicaments,
    getPatientActiveMedicaments,

    // Prescriptions
    getDoctorPrescriptions,
    addPrescription,
    updatePrescription,
    deletePrescription,

    // Medicaments & Contraindications
    addMedicamentsForAppointment,
    addMedicamentContraindications,
    getMedicamentContraindications,
    deleteMedicamentContraindication,
    addPatientContraindications,
    deletePatientContraindication
  }
}
