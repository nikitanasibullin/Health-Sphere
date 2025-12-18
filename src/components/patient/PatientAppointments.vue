<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-calendar-alt text-purple-500 mr-2"></i>My Appointments
      </h2>

      <!-- Filter Tabs -->
      <div class="mb-6 flex flex-wrap gap-2">
        <button
            v-for="filter in filters"
            :key="filter.value"
            @click="activeFilter = filter.value"
            :class="[
            'px-4 py-2 rounded-lg font-semibold transition',
            activeFilter === filter.value
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ filter.label }}
        </button>
      </div>

      <!-- Appointments List -->
      <div v-if="filteredAppointments.length === 0" class="text-center py-12 text-gray-500">
        <i class="fas fa-calendar-times text-4xl mb-4"></i>
        <p>No {{ activeFilter === 'all' ? '' : activeFilter.toLowerCase() }} appointments found</p>
      </div>

      <div v-else class="space-y-4">
        <div
            v-for="apt in filteredAppointments"
            :key="apt.id"
            class="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition card-hover"
        >
          <div class="flex flex-col md:flex-row justify-between items-start">
            <div class="flex items-center flex-1 mb-4 md:mb-0">
              <div class="w-16 h-16 bg-gradient-to-r from-green-400 to-teal-400 rounded-full flex items-center justify-center mr-4">
                <i class="fas fa-user-md text-white text-2xl"></i>
              </div>
              <div>
                <h3 class="font-bold text-xl text-gray-800">{{ buildDoctorName(apt.schedule.doctor) }}</h3>
                <p class="text-gray-600">{{ apt.schedule.doctor.specialization.name }}</p>
                <p class="text-gray-700 mt-2">
                  <i class="fas fa-calendar text-blue-500 mr-2"></i>
                  {{ formatDate(apt.schedule.date) }} at {{ apt.schedule.start_time }} - {{ apt.schedule.end_time }}
                </p>
              </div>
            </div>

            <div class="flex flex-col items-end gap-2">
              <span :class="getStatusClass(apt.status)">{{ capitalizeStatus(apt.status) }}</span>

              <!-- Action Buttons -->
              <div class="flex gap-2 mt-2">
                <button
                    @click="openDetailsModal(apt)"
                    class="bg-blue-100 text-blue-700 px-4 py-2 rounded-lg hover:bg-blue-200 transition text-sm font-semibold"
                >
                  <i class="fas fa-eye mr-1"></i>View Details
                </button>
                <button
                    v-if="apt.status === 'scheduled'"
                    @click="handleCancelAppointment(apt.id)"
                    class="bg-red-100 text-red-600 px-4 py-2 rounded-lg hover:bg-red-200 transition text-sm font-semibold"
                >
                  <i class="fas fa-times-circle mr-1"></i>Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointment Details Modal -->
    <div
        v-if="showDetailsModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeDetailsModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto animate-fadeIn">
        <!-- Modal Header -->
        <div class="sticky top-0 bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-6 py-4 flex justify-between items-center rounded-t-2xl z-10">
          <h3 class="text-2xl font-bold">
            <i class="fas fa-calendar-check mr-2"></i>Appointment Details
          </h3>
          <button @click="closeDetailsModal" class="text-white hover:text-gray-200 transition">
            <i class="fas fa-times text-2xl"></i>
          </button>
        </div>

        <!-- Loading State -->
        <div v-if="isLoadingDetails" class="p-12 text-center">
          <i class="fas fa-spinner fa-spin text-4xl text-purple-500 mb-4"></i>
          <p class="text-gray-600">Loading appointment details...</p>
        </div>

        <!-- Modal Content -->
        <div v-else class="p-6 space-y-6">
          <!-- Appointment Info Card -->
          <div class="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-5">
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center">
                <div class="w-14 h-14 bg-gradient-to-r from-purple-400 to-indigo-400 rounded-full flex items-center justify-center mr-4">
                  <i class="fas fa-user-md text-white text-xl"></i>
                </div>
                <div>
                  <h4 class="font-bold text-xl text-gray-800">
                    {{ selectedAppointment ? buildDoctorName(selectedAppointment.schedule.doctor) : '' }}
                  </h4>
                  <p class="text-gray-600">
                    {{ selectedAppointment?.schedule.doctor.specialization.name }}
                  </p>
                </div>
              </div>
              <span :class="getStatusClass(selectedAppointment?.status)">
                {{ capitalizeStatus(selectedAppointment?.status) }}
              </span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
              <div class="flex items-center p-3 bg-white rounded-lg">
                <i class="fas fa-calendar text-purple-500 mr-3 text-lg"></i>
                <div>
                  <p class="text-xs text-gray-500 uppercase font-semibold">Date</p>
                  <p class="font-medium text-gray-800">
                    {{ formatDate(selectedAppointment?.schedule.date) }}
                  </p>
                </div>
              </div>
              <div class="flex items-center p-3 bg-white rounded-lg">
                <i class="fas fa-clock text-indigo-500 mr-3 text-lg"></i>
                <div>
                  <p class="text-xs text-gray-500 uppercase font-semibold">Time</p>
                  <p class="font-medium text-gray-800">
                    {{ selectedAppointment?.schedule.start_time }} - {{ selectedAppointment?.schedule.end_time }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Appointment Information/Notes -->
          <div v-if="appointmentDetails.information" class="border border-gray-200 rounded-xl p-5">
            <h5 class="font-bold text-gray-800 mb-3 flex items-center">
              <i class="fas fa-notes-medical text-blue-500 mr-2"></i>
              Doctor's Notes
            </h5>
            <p class="text-gray-700 whitespace-pre-line bg-blue-50 p-4 rounded-lg">
              {{ appointmentDetails.information }}
            </p>
          </div>

          <!-- Prescriptions Section -->
          <div class="border border-gray-200 rounded-xl p-5">
            <h5 class="font-bold text-gray-800 mb-4 flex items-center">
              <i class="fas fa-prescription-bottle text-green-500 mr-2"></i>
              Prescriptions
              <span class="ml-2 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs">
                {{ appointmentDetails.prescriptions?.length || 0 }}
              </span>
            </h5>

            <div v-if="!appointmentDetails.prescriptions?.length" class="text-center py-6 text-gray-500">
              <i class="fas fa-pills text-3xl mb-2 text-gray-300"></i>
              <p>No prescriptions for this appointment</p>
            </div>

            <div v-else class="space-y-4">
              <div
                  v-for="(prescription, index) in appointmentDetails.prescriptions"
                  :key="index"
                  class="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-4 border border-green-200"
              >
                <div class="flex justify-between items-start mb-3">
                  <div class="flex items-center">
                    <div class="w-10 h-10 bg-gradient-to-r from-green-400 to-teal-400 rounded-full flex items-center justify-center mr-3">
                      <i class="fas fa-capsules text-white"></i>
                    </div>
                    <div>
                      <h6 class="font-bold text-gray-800">{{ prescription.medicament_name || prescription.name }}</h6>
                      <span :class="getPrescriptionStatusClass(prescription)">
                        {{ getPrescriptionStatus(prescription) }}
                      </span>
                    </div>
                  </div>
                </div>

                <div class="grid grid-cols-2 gap-3 text-sm">
                  <div v-if="prescription.dosage" class="p-2 bg-white rounded-lg">
                    <p class="text-xs text-gray-500 font-semibold">Dosage</p>
                    <p class="text-gray-800">{{ prescription.dosage }}</p>
                  </div>
                  <div v-if="prescription.frequency" class="p-2 bg-white rounded-lg">
                    <p class="text-xs text-gray-500 font-semibold">Frequency</p>
                    <p class="text-gray-800">{{ prescription.frequency }}</p>
                  </div>
                  <div v-if="prescription.start_date" class="p-2 bg-white rounded-lg">
                    <p class="text-xs text-gray-500 font-semibold">Start Date</p>
                    <p class="text-gray-800">{{ formatShortDate(prescription.start_date) }}</p>
                  </div>
                  <div v-if="prescription.end_date" class="p-2 bg-white rounded-lg">
                    <p class="text-xs text-gray-500 font-semibold">End Date</p>
                    <p class="text-gray-800">{{ formatShortDate(prescription.end_date) }}</p>
                  </div>
                </div>

                <div v-if="prescription.notes" class="mt-3 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                  <p class="text-sm text-gray-700">
                    <i class="fas fa-sticky-note text-yellow-500 mr-1"></i>
                    <strong>Notes:</strong> {{ prescription.notes }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Contraindications Section -->
          <div v-if="appointmentDetails.contraindications?.length" class="border border-red-200 rounded-xl p-5 bg-red-50">
            <h5 class="font-bold text-gray-800 mb-4 flex items-center">
              <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>
              Contraindications & Warnings
            </h5>
            <div class="flex flex-wrap gap-2">
              <span
                  v-for="(contra, index) in appointmentDetails.contraindications"
                  :key="index"
                  class="px-3 py-2 bg-red-100 text-red-700 rounded-lg text-sm font-semibold flex items-center"
              >
                <i class="fas fa-ban mr-2"></i>
                {{ typeof contra === 'string' ? contra : contra.contradiction || contra.name }}
              </span>
            </div>
          </div>

          <!-- No Additional Details Message -->
          <div
              v-if="!appointmentDetails.information && !appointmentDetails.prescriptions?.length && !appointmentDetails.contraindications?.length"
              class="text-center py-8 text-gray-500"
          >
            <i class="fas fa-info-circle text-4xl mb-3 text-gray-300"></i>
            <p class="text-lg">No additional details available</p>
            <p class="text-sm mt-1">Details will be added after your appointment is completed</p>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="sticky bottom-0 bg-white border-t p-4 flex justify-end gap-3 rounded-b-2xl">
          <button
              @click="closeDetailsModal"
              class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition font-semibold"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { usePatientData } from '../../composables/usePatientData'

export default {
  name: 'PatientAppointments',
  props: {
    patientId: {
      type: Number,
      required: false
    }
  },
  setup(props) {
    const {
      getPatientAppointments,
      getPatientMedication,
      cancelAppointment,
      buildDoctorName,
      initializeData
    } = usePatientData()

    // State
    const myAppointments = ref([])
    const activeFilter = ref('all')
    const showDetailsModal = ref(false)
    const selectedAppointment = ref(null)
    const isLoadingDetails = ref(false)
    const appointmentDetails = ref({
      information: '',
      prescriptions: [],
      contraindications: []
    })

    const filters = [
      { label: 'All', value: 'all' },
      { label: 'Scheduled', value: 'scheduled' },
      { label: 'Completed', value: 'completed' },
      { label: 'Cancelled', value: 'cancelled' }
    ]

    // Computed
    const filteredAppointments = computed(() => {
      if (!myAppointments.value) return []

      let filtered = [...myAppointments.value]

      if (activeFilter.value !== 'all') {
        filtered = filtered.filter(a => a.status === activeFilter.value)
      }

      return filtered.sort((a, b) =>
          new Date(b.schedule?.date) - new Date(a.schedule?.date)
      )
    })

    // Methods
    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const formatShortDate = (dateStr) => {
      if (!dateStr) return ''
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    const capitalizeStatus = (status) => {
      if (!status) return ''
      return status.charAt(0).toUpperCase() + status.slice(1)
    }

    const getStatusClass = (status) => {
      const classes = {
        'scheduled': 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold',
        'completed': 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold',
        'cancelled': 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold'
      }
      return classes[status] || classes['scheduled']
    }

    const getPrescriptionStatus = (prescription) => {
      if (prescription.is_active === false) return 'Expired'

      const today = new Date()
      const startDate = new Date(prescription.start_date)
      const endDate = new Date(prescription.end_date)
      if (startDate > today) return 'Upcoming'
      return today > endDate ? 'Expired' : 'Active'
    }

    const getPrescriptionStatusClass = (prescription) => {
      const status = getPrescriptionStatus(prescription)
      const classes = {
        'Active': 'px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs font-semibold',
        'Upcoming': 'px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold',
        'Expired': 'px-2 py-0.5 bg-white text-gray-500 border border-gray-300 rounded-full text-xs font-semibold'
      }
      return classes[status]
    }

    const openDetailsModal = async (appointment) => {
      selectedAppointment.value = appointment
      showDetailsModal.value = true
      isLoadingDetails.value = true

      try {
        // Get medication data using existing function
        const medicationData = await getPatientMedication()
        console.log('Medication data:', medicationData)

        // Extract prescriptions - handle different API response structures
        let prescriptions = []

        if (medicationData) {
          if (medicationData.medicaments && Array.isArray(medicationData.medicaments)) {
            // If API returns { medicaments: [...] }
            prescriptions = medicationData.medicaments
          } else if (Array.isArray(medicationData)) {
            // If API returns array directly
            prescriptions = medicationData
          }

          // Filter prescriptions for this specific appointment if there's appointment_id
          if (prescriptions.length > 0 && prescriptions[0].appointment_id !== undefined) {
            prescriptions = prescriptions.filter(p => p.appointment_id === appointment.id)
          }
        }

        // Extract contraindications from medication data
        let contraindications = []
        if (medicationData) {
          if (medicationData.direct_contraindications) {
            contraindications = [...contraindications, ...medicationData.direct_contraindications]
          }
          if (medicationData.medicament_based_contraindications) {
            contraindications = [...contraindications, ...medicationData.medicament_based_contraindications]
          }
          if (medicationData.contraindications && Array.isArray(medicationData.contraindications)) {
            contraindications = medicationData.contraindications
          }
        }

        // Set appointment details
        appointmentDetails.value = {
          information: appointment.information || '',
          prescriptions: prescriptions,
          contraindications: contraindications
        }

        console.log('Appointment details:', appointmentDetails.value)

      } catch (error) {
        console.error('Error fetching appointment details:', error)
        appointmentDetails.value = {
          information: appointment.information || '',
          prescriptions: [],
          contraindications: []
        }
      } finally {
        isLoadingDetails.value = false
      }
    }

    const closeDetailsModal = () => {
      showDetailsModal.value = false
      selectedAppointment.value = null
      appointmentDetails.value = {
        information: '',
        prescriptions: [],
        contraindications: []
      }
    }

    const handleCancelAppointment = async (appointmentId) => {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        await cancelAppointment(appointmentId)
        // Refresh appointments list
        myAppointments.value = await getPatientAppointments() || []
      }
    }

    onMounted(async () => {
      await initializeData()
      myAppointments.value = await getPatientAppointments() || []
    })

    return {
      activeFilter,
      filters,
      filteredAppointments,
      buildDoctorName,
      formatDate,
      formatShortDate,
      capitalizeStatus,
      getStatusClass,
      getPrescriptionStatus,
      getPrescriptionStatusClass,
      handleCancelAppointment,
      showDetailsModal,
      selectedAppointment,
      isLoadingDetails,
      appointmentDetails,
      openDetailsModal,
      closeDetailsModal
    }
  }
}
</script>