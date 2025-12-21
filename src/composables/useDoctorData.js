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

    const getAllMedicaments = async () => {
        try {
            const response = await http.get('/api/doctor/medicaments')
            return response.data
        } catch (error) {
            console.error('Failed to fetch medicaments:', error)
            return []
        }
    }

    // ==================== MEDICAMENT MANAGEMENT ====================

    const addMedicamentWithContraindications = async (medicamentName, medContraindicationIds = [], otherContraindications = []) => {
        try {
            const response = await http.post('/api/doctor/medicaments', {
                medicament_name: medicamentName,
                med_contraindications_ids: medContraindicationIds
            })
            const medicament = response.data

            if (otherContraindications.length > 0) {
                let allContras = await getAllContraindications()

                for (const contraName of otherContraindications) {
                    let contra = allContras.find(c => c.name.toLowerCase() === contraName.toLowerCase())

                    if (!contra) {
                        try {
                            const contraResponse = await http.post('/api/doctor/contraindications', {
                                name: contraName
                            })
                            contra = contraResponse.data
                            allContras = await getAllContraindications()
                        } catch (e) {
                            console.warn('Failed to create contraindication:', e.response?.data?.detail || e.message)
                            continue
                        }
                    }

                    try {
                        await http.post('/api/doctor/medication-contraindication', {
                            medicament_id: medicament.id,
                            contraindication_id: contra.id
                        })
                    } catch (e) {
                        console.warn('Link may already exist:', e.response?.data?.detail || e.message)
                    }
                }
            }

            return { success: true, medicament_id: medicament.id, medicament_name: medicament.name }
        } catch (error) {
            handleApiError(error, 'Add medicament with contraindications')
            throw error
        }
    }

    const deleteMedicamentById = async (medicamentId) => {
        try {
            const response = await http.delete(`/api/doctor/medicaments/${medicamentId}`)
            return response.data
        } catch (error) {
            handleApiError(error, 'Delete medicament')
            throw error
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

    const getAppointmentDetails = async (appointmentId) => {
        try {
            const appointments = await getDoctorAppointments()
            const appointment = appointments.find(apt => apt.id === appointmentId)

            if (!appointment) {
                console.error(`Appointment ${appointmentId} not found`)
                return null
            }

            let medicaments = []
            if (appointment.patient?.id) {
                medicaments = await getPatientMedicaments(appointment.patient.id)
            }

            return {
                ...appointment,
                medicaments: medicaments.reverse() || []
            }
        } catch (error) {
            console.error('Failed to fetch appointment details:', error)
            return null
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
            throw error
        }
    }

    // Получить лекарства для конкретного приёма
    const getAppointmentMedicaments = async (appointmentId) => {
        try {
            const response = await http.get(`/api/doctor/appointments/${appointmentId}/medicaments`)
            return response.data
        } catch (error) {
            console.error('Failed to fetch appointment medicaments:', error)
            return []
        }
    }

    const addMedicamentsForAppointment = async (appointmentId, medicaments) => {
        try {
            const payload = {
                medicaments: Array.isArray(medicaments) ? medicaments : [medicaments]
            }

            const response = await http.post(
                `/api/doctor/appointments/${appointmentId}/medicaments`,
                payload
            )
            return response.data
        } catch (error) {
            handleApiError(error, 'Add medicaments')
            throw error
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
            const response = await http.get(`/api/doctor/patient/${patientId}/medication`)
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

    // Получить противопоказания пациента к медикаментам
    const getPatientMedicamentContraindications = async (patientId) => {
        try {
            const response = await http.get(`/api/doctor/patient/medication-contraindication/${patientId}`)
            return response.data
        } catch (error) {
            console.error('Failed to fetch patient medicament contraindications:', error)
            return []
        }
    }

    // Получить другие противопоказания пациента
    const getPatientOtherContraindications = async (patientId) => {
        try {
            const response = await http.get(`/api/doctor/patient/other-contraindication/${patientId}`)
            return response.data
        } catch (error) {
            console.error('Failed to fetch patient other contraindications:', error)
            return []
        }
    }

    // Получить ВСЕ противопоказания пациента (объединённые)
    const getPatientContraindications = async (patientId) => {
        try {
            const [medContras, otherContras] = await Promise.all([
                getPatientMedicamentContraindications(patientId),
                getPatientOtherContraindications(patientId)
            ])

            const result = []

            if (medContras && medContras.length > 0) {
                medContras.forEach(c => {
                    result.push(`Cannot take: ${c.medicament_name}`)
                })
            }

            if (otherContras && otherContras.length > 0) {
                otherContras.forEach(c => {
                    result.push(c.contraindication_name)
                })
            }

            return result
        } catch (error) {
            console.error('Failed to fetch patient contraindications:', error)
            return []
        }
    }

    // ==================== PATIENT CONTRAINDICATIONS ====================

    const addPatientMedicamentContraindication = async (patientId, medicamentId) => {
        try {
            const response = await http.post('/api/doctor/patient/medication-contraindication', {
                patient_id: patientId,
                contraindication_medicament_id: medicamentId
            })
            return response.data
        } catch (error) {
            handleApiError(error, 'Add patient medicament contraindication')
            throw error
        }
    }

    const addPatientOtherContraindication = async (patientId, contraindicationId) => {
        try {
            const response = await http.post('/api/doctor/patient/other-contraindication', {
                patient_id: patientId,
                contraindication_id: contraindicationId
            })
            return response.data
        } catch (error) {
            handleApiError(error, 'Add patient other contraindication')
            throw error
        }
    }

    const addPatientContraindications = async (patientId, contradictionNames) => {
        try {
            let allContras = await getAllContraindications()

            for (const name of contradictionNames) {
                let contra = allContras.find(c => c.name.toLowerCase() === name.toLowerCase())

                if (!contra) {
                    try {
                        const response = await http.post('/api/doctor/contraindications', { name })
                        contra = response.data
                        allContras = await getAllContraindications()
                    } catch (e) {
                        console.warn('Failed to create contraindication:', e.response?.data?.detail || e.message)
                        continue
                    }
                }

                try {
                    await addPatientOtherContraindication(patientId, contra.id)
                } catch (e) {
                    console.warn('Link may already exist:', e.response?.data?.detail || e.message)
                }
            }

            return { success: true }
        } catch (error) {
            handleApiError(error, 'Add patient contraindications')
            throw error
        }
    }

    const deletePatientMedicamentContraindication = async (patientId, medicamentId) => {
        try {
            const response = await http.delete('/api/doctor/patient/medication-contraindication', {
                data: {
                    patient_id: patientId,
                    contraindication_medicament_id: medicamentId
                }
            })
            return response.data
        } catch (error) {
            handleApiError(error, 'Delete patient medicament contraindication')
            throw error
        }
    }

    const deletePatientOtherContraindication = async (patientId, contraindicationId) => {
        try {
            const response = await http.delete('/api/doctor/patient/other-contraindication', {
                data: {
                    patient_id: patientId,
                    contraindication_id: contraindicationId
                }
            })
            return response.data
        } catch (error) {
            handleApiError(error, 'Delete patient other contraindication')
            throw error
        }
    }

    // ==================== PRESCRIPTIONS ====================

    const getDoctorPrescriptions = (doctorId) => {
        return computed(() => state.prescriptions.filter(p => p.doctor_id === doctorId))
    }

    const getMyPrescriptions = async () => {
        try {
            const response = await http.get('/api/doctor/my-prescriptions')
            return response.data
        } catch (error) {
            console.error('Failed to fetch my prescriptions:', error)
            return []
        }
    }

    const addPrescription = async (prescription) => {
        try {
            const response = await http.post('/api/doctor/prescriptions', prescription)
            return response.data
        } catch (error) {
            handleApiError(error, 'Add prescription')
            throw error
        }
    }

    const updatePrescription = async (id, data) => {
        try {
            const response = await http.put(`/api/doctor/prescriptions/${id}`, data)
            return response.data
        } catch (error) {
            handleApiError(error, 'Update prescription')
            throw error
        }
    }

    const deletePrescription = async (id) => {
        try {
            await http.delete(`/api/doctor/prescriptions/${id}`)
        } catch (error) {
            handleApiError(error, 'Delete prescription')
            throw error
        }
    }

    const deletePatientMedicament = async (patientMedicamentId) => {
        try {
            const response = await http.delete(`/api/doctor/patient-medicaments/${patientMedicamentId}`)
            return response.data
        } catch (error) {
            handleApiError(error, 'Delete patient medicament')
            throw error
        }
    }

    // ==================== CONTRAINDICATIONS ====================

    const getAllContraindications = async () => {
        try {
            const response = await http.get('/api/doctor/contraindications')
            return response.data
        } catch (error) {
            console.error('Failed to fetch contraindications:', error)
            return []
        }
    }

    const addContraindication = async (name) => {
        try {
            const response = await http.post('/api/doctor/contraindications', { name })
            return response.data
        } catch (error) {
            handleApiError(error, 'Add contraindication')
            throw error
        }
    }

    const deleteContraindication = async (contraindicationId) => {
        try {
            const response = await http.delete(`/api/doctor/contraindications/${contraindicationId}`)
            return response.data
        } catch (error) {
            handleApiError(error, 'Delete contraindication')
            throw error
        }
    }

    // ==================== MEDICAMENT INTERACTIONS ====================

    const getMedicamentInteractions = async () => {
        try {
            const response = await http.get('/api/doctor/interactions')
            return response.data
        } catch (error) {
            console.error('Failed to fetch interactions:', error)
            return []
        }
    }

    const addMedicamentInteraction = async (firstMedicamentId, secondMedicamentId) => {
        try {
            const response = await http.post('/api/doctor/interactions', {
                first_medicament_id: firstMedicamentId,
                second_medicament_id: secondMedicamentId
            })
            return response.data
        } catch (error) {
            handleApiError(error, 'Add medicament interaction')
            throw error
        }
    }

    const deleteMedicamentInteraction = async (medicament1Id, medicament2Id) => {
        try {
            const response = await http.delete('/api/doctor/interactions', {
                data: {
                    first_medicament_id: medicament1Id,
                    second_medicament_id: medicament2Id
                }
            })
            return response.data
        } catch (error) {
            handleApiError(error, 'Delete medicament interaction')
            throw error
        }
    }

    // ==================== MEDICATION-CONTRAINDICATION LINKS ====================

    const getMedicationContraindicationLinks = async () => {
        try {
            const response = await http.get('/api/doctor/medication-contraindication')
            return response.data
        } catch (error) {
            console.error('Failed to fetch medication contraindication links:', error)
            return []
        }
    }

    const addMedicationContraindicationLink = async (medicamentId, contraindicationId) => {
        try {
            const response = await http.post('/api/doctor/medication-contraindication', {
                medicament_id: medicamentId,
                contraindication_id: contraindicationId
            })
            return response.data
        } catch (error) {
            handleApiError(error, 'Add medication contraindication link')
            throw error
        }
    }

    const deleteMedicationContraindicationLink = async (medicamentId, contraindicationId) => {
        try {
            const response = await http.delete('/api/doctor/medication-contraindication', {
                data: {
                    medicament_id: medicamentId,
                    contraindication_id: contraindicationId
                }
            })
            return response.data
        } catch (error) {
            handleApiError(error, 'Delete medication contraindication link')
            throw error
        }
    }

    const getMedicamentAllContraindications = async (medicamentId) => {
        try {
            const response = await http.get(`/api/doctor/medicaments/${medicamentId}/all-contraindications`)
            return response.data
        } catch (error) {
            console.error('Failed to fetch medicament contraindications:', error)
            return null
        }
    }

    const getMedicamentContraindications = async () => {
        try {
            const [medicaments, interactions, medContraLinks] = await Promise.all([
                getAllMedicaments(),
                getMedicamentInteractions(),
                getMedicationContraindicationLinks()
            ])

            const result = []

            medicaments.forEach(med => {
                result.push({
                    medicament_id: med.id,
                    medicament_name: med.name,
                    contradiction: null
                })
            })

            interactions.forEach(i => {
                result.push({
                    medicament_id: i.first_medicament_id,
                    medicament_name: i.first_medicament_name,
                    contradiction: i.second_medicament_name
                })
                result.push({
                    medicament_id: i.second_medicament_id,
                    medicament_name: i.second_medicament_name,
                    contradiction: i.first_medicament_name
                })
            })

            medContraLinks.forEach(link => {
                result.push({
                    medicament_id: link.medicament_id,
                    medicament_name: link.medicament_name,
                    contradiction: link.contraindication_name
                })
            })

            return result
        } catch (error) {
            console.error('Failed to get medicament contraindications:', error)
            return []
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
        getAllMedicaments,

        // Medicament Management
        addMedicamentWithContraindications,
        deleteMedicamentById,

        // Appointments
        getDoctorAppointments,
        getDoctorTodayAppointments,
        updateAppointmentStatus,
        getAppointmentDetails,
        getAppointmentMedicaments,
        addMedicamentsForAppointment,

        // Patients
        getDoctorPatients,
        getPatientMedicationReport,
        getPatientMedicaments,
        getPatientActiveMedicaments,
        getPatientContraindications,
        getPatientMedicamentContraindications,
        getPatientOtherContraindications,

        // Patient Contraindications
        addPatientContraindications,
        addPatientMedicamentContraindication,
        addPatientOtherContraindication,
        deletePatientMedicamentContraindication,
        deletePatientOtherContraindication,

        // Prescriptions
        getDoctorPrescriptions,
        getMyPrescriptions,
        addPrescription,
        updatePrescription,
        deletePrescription,
        deletePatientMedicament,

        // Contraindications
        getAllContraindications,
        addContraindication,
        deleteContraindication,

        // Medicament Interactions
        getMedicamentInteractions,
        addMedicamentInteraction,
        deleteMedicamentInteraction,

        // Medication-Contraindication Links
        getMedicationContraindicationLinks,
        addMedicationContraindicationLink,
        deleteMedicationContraindicationLink,
        getMedicamentAllContraindications,
        getMedicamentContraindications,
    }
}