<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-prescription-bottle text-green-500 mr-2"></i>My Prescriptions
      </h2>

      <!-- Search -->
      <div class="mb-6">
        <div class="relative">
          <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="search"
            type="text"
            placeholder="Search prescriptions..."
            class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          >
        </div>
      </div>

      <!-- Empty State -->
      <div v-if="filteredPrescriptions.length === 0" class="text-center py-12 text-gray-500">
        <i class="fas fa-prescription-bottle text-4xl mb-4"></i>
        <p>No prescriptions found</p>
      </div>

      <!-- Prescriptions Grid -->
      <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="prescription in filteredPrescriptions"
          :key="prescription.id"
          class="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition card-hover"
        >
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="font-bold text-lg text-gray-800">{{ prescription.name }}</h3>
              <p v-if="hasValue(prescription.prescribed_by)" class="text-sm text-gray-600">
                Prescribed by {{ prescription.prescribed_by }}
              </p>
              <p v-if="hasValue(prescription.start_date)" class="text-sm text-gray-500">{{ formatDate(prescription.start_date) }}</p>
            </div>
            <span :class="getStatusClass(prescription)">
              {{ getPrescriptionStatus(prescription) }}
            </span>
          </div>

          <!-- Dosage & Frequency -->
          <div v-if="hasValue(prescription.dosage) || hasValue(prescription.frequency)" class="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-4 mb-4">
            <div class="grid gap-4" :class="hasValue(prescription.dosage) && hasValue(prescription.frequency) ? 'grid-cols-2' : 'grid-cols-1'">
              <div v-if="hasValue(prescription.dosage)">
                <p class="text-xs font-semibold text-gray-500 uppercase">Dosage</p>
                <p class="text-gray-800 font-medium">{{ prescription.dosage }}</p>
              </div>
              <div v-if="hasValue(prescription.frequency)">
                <p class="text-xs font-semibold text-gray-500 uppercase">Frequency</p>
                <p class="text-gray-800 font-medium">{{ prescription.frequency }}</p>
              </div>
            </div>
          </div>

          <!-- Duration -->
          <div v-if="hasValue(prescription.start_date) || hasValue(prescription.end_date)" class="bg-gray-50 rounded-lg p-4 mb-4">
            <div class="grid gap-4" :class="hasValue(prescription.start_date) && hasValue(prescription.end_date) ? 'grid-cols-2' : 'grid-cols-1'">
              <div v-if="hasValue(prescription.start_date)">
                <p class="text-xs font-semibold text-gray-500 uppercase">Start Date</p>
                <p class="text-gray-800 font-medium">{{ formatDate(prescription.start_date) }}</p>
              </div>
              <div v-if="hasValue(prescription.end_date)">
                <p class="text-xs font-semibold text-gray-500 uppercase">End Date</p>
                <p class="text-gray-800 font-medium">{{ formatDate(prescription.end_date) }}</p>
              </div>
            </div>
          </div>

          <!-- Notes - only if exists -->
          <div v-if="hasValue(prescription.notes)" class="mb-4">
            <p class="text-sm text-gray-600">
              <i class="fas fa-info-circle text-blue-500 mr-1"></i>
              <strong>Notes:</strong> {{ prescription.notes }}
            </p>
          </div>

          <div v-if="hasDetails(prescription)" class="flex gap-2">
            <button
              @click="viewDetails(prescription)"
              class="flex-1 bg-blue-100 text-blue-700 py-2 rounded-lg hover:bg-blue-200 transition text-sm font-semibold"
            >
              <i class="fas fa-eye mr-1"></i>View Details
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Prescription Details Modal -->
    <div
      v-if="showDetailsModal && selectedPrescription"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="showDetailsModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto animate-fadeIn">
        <div class="sticky top-0 bg-white border-b px-6 py-4 flex justify-between items-center">
          <h3 class="text-2xl font-bold text-gray-800">Prescription Details</h3>
          <button @click="showDetailsModal = false" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <div class="p-6 space-y-4">
          <div class="p-4 bg-gradient-to-r from-green-50 to-teal-50 rounded-xl">
            <h4 class="font-bold text-xl text-gray-800">{{ selectedPrescription.name }}</h4>
            <span :class="getStatusClass(selectedPrescription)" class="mt-2 inline-block">
              {{ getPrescriptionStatus(selectedPrescription) }}
            </span>
          </div>

          <div class="space-y-3">
            <div v-if="hasValue(selectedPrescription.prescribed_by)" class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-user-md text-green-500 mr-3 w-5"></i>
              <div>
                <p class="text-xs text-gray-500">Prescribed By</p>
                <p class="font-semibold">{{ selectedPrescription.prescribed_by }}</p>
              </div>
            </div>

            <div v-if="hasValue(selectedPrescription.dosage)" class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-pills text-purple-500 mr-3 w-5"></i>
              <div>
                <p class="text-xs text-gray-500">Dosage</p>
                <p class="font-semibold">{{ selectedPrescription.dosage }}</p>
              </div>
            </div>

            <div v-if="hasValue(selectedPrescription.frequency)" class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-clock text-orange-500 mr-3 w-5"></i>
              <div>
                <p class="text-xs text-gray-500">Frequency</p>
                <p class="font-semibold">{{ selectedPrescription.frequency }}</p>
              </div>
            </div>

            <!-- Dates -->
            <div v-if="hasValue(selectedPrescription.start_date) || hasValue(selectedPrescription.end_date)" class="grid gap-3" :class="hasValue(selectedPrescription.start_date) && hasValue(selectedPrescription.end_date) ? 'grid-cols-2' : 'grid-cols-1'">
              <div v-if="hasValue(selectedPrescription.start_date)" class="p-3 bg-gray-50 rounded-lg">
                <p class="text-xs text-gray-500">
                  <i class="fas fa-calendar-plus text-blue-500 mr-1"></i>Start Date
                </p>
                <p class="font-semibold">{{ formatDate(selectedPrescription.start_date) }}</p>
              </div>
              <div v-if="hasValue(selectedPrescription.end_date)" class="p-3 bg-gray-50 rounded-lg">
                <p class="text-xs text-gray-500">
                  <i class="fas fa-calendar-minus text-red-500 mr-1"></i>End Date
                </p>
                <p class="font-semibold">{{ formatDate(selectedPrescription.end_date) }}</p>
              </div>
            </div>

            <div v-if="hasValue(selectedPrescription.notes)" class="p-3 bg-yellow-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">
                <i class="fas fa-sticky-note text-yellow-500 mr-1"></i>Special Instructions
              </p>
              <p class="text-gray-800">{{ selectedPrescription.notes }}</p>
            </div>

            <!-- Days Remaining -->
            <div v-if="isPrescriptionActive(selectedPrescription) && hasValue(selectedPrescription.end_date) && getDaysRemaining(selectedPrescription) > 0" class="p-3 bg-green-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">
                <i class="fas fa-hourglass-half text-green-500 mr-1"></i>Days Remaining
              </p>
              <p class="font-semibold text-green-700">{{ getDaysRemaining(selectedPrescription) }} days</p>
            </div>
          </div>
        </div>

        <div class="sticky bottom-0 bg-white border-t p-4">
          <button
            @click="showDetailsModal = false"
            class="w-full px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition font-semibold"
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
  name: 'PatientPrescriptions',
  setup() {
    const { getPatientMedication } = usePatientData()

    // State
    const prescriptions = ref([])
    const search = ref('')
    const showDetailsModal = ref(false)
    const selectedPrescription = ref(null)

    // Helper to check if value exists and is not empty
    const hasValue = (value) => {
      if (value === null || value === undefined) return false
      if (typeof value === 'string' && value.trim() === '') return false
      if (typeof value === 'number') return true
      if (typeof value === 'boolean') return true
      return true
    }

    // Check if prescription has any details worth showing in modal
    const hasDetails = (prescription) => {
      return hasValue(prescription.prescribed_by) ||
        hasValue(prescription.dosage) ||
        hasValue(prescription.frequency) ||
        hasValue(prescription.start_date) ||
        hasValue(prescription.end_date) ||
        hasValue(prescription.notes)
    }

    // Computed
    const filteredPrescriptions = computed(() => {
      if (!prescriptions.value || prescriptions.value.length === 0) {
        return []
      }

      let filtered = [...prescriptions.value]

      if (search.value) {
        const searchLower = search.value.toLowerCase()
        filtered = filtered.filter(p =>
          (hasValue(p.name) && p.name.toLowerCase().includes(searchLower)) ||
          (hasValue(p.dosage) && p.dosage.toLowerCase().includes(searchLower)) ||
          (hasValue(p.frequency) && p.frequency.toLowerCase().includes(searchLower)) ||
          (hasValue(p.prescribed_by) && p.prescribed_by.toLowerCase().includes(searchLower))
        )
      }

      return filtered.sort((a, b) => {
        const dateA = a.start_date ? new Date(a.start_date) : new Date(0)
        const dateB = b.start_date ? new Date(b.start_date) : new Date(0)
        return dateB - dateA
      })
    })

    // Methods
    const formatDate = (dateStr) => {
      if (!hasValue(dateStr)) return null
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const isPrescriptionActive = (prescription) => {
      // Check is_active flag first if available
      if (typeof prescription.is_active === 'boolean') {
        return prescription.is_active
      }
      if (!hasValue(prescription.end_date)) return true
      const endDate = new Date(prescription.end_date)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      return endDate >= today
    }

    const getPrescriptionStatus = (prescription) => {
      // Check is_active flag first
      if (typeof prescription.is_active === 'boolean' && !prescription.is_active) {
        return 'Expired'
      }

      const today = new Date()
      today.setHours(0, 0, 0, 0)

      if (hasValue(prescription.start_date)) {
        const startDate = new Date(prescription.start_date)
        if (today < startDate) return 'Upcoming'
      }

      if (hasValue(prescription.end_date)) {
        const endDate = new Date(prescription.end_date)
        if (today > endDate) return 'Expired'
      }

      return 'Active'
    }

    const getStatusClass = (prescription) => {
      const status = getPrescriptionStatus(prescription)
      const classes = {
        'Active': 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold',
        'Expired': 'px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-semibold',
        'Upcoming': 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold'
      }
      return classes[status]
    }

    const getDaysRemaining = (prescription) => {
      if (!hasValue(prescription.end_date)) return 0
      const endDate = new Date(prescription.end_date)
      const today = new Date()
      today.setHours(0, 0, 0, 0)
      const diffTime = endDate - today
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
      return Math.max(0, diffDays)
    }

    // Clean string value - returns null if empty
    const cleanString = (value) => {
      if (value === null || value === undefined) return null
      if (typeof value === 'string') {
        const trimmed = value.trim()
        return trimmed === '' ? null : trimmed
      }
      return value
    }

    const transformMedicationData = (data) => {
      if (!data) return []

      // Handle API response structure: { medicaments: [...] }
      let medicaments = []

      if (data.medicaments && Array.isArray(data.medicaments)) {
        medicaments = data.medicaments
      } else if (Array.isArray(data)) {
        medicaments = data
      } else {
        return []
      }

      return medicaments.map((item) => ({
        id: item.id,
        name: cleanString(item.name) || cleanString(item.medicament_name) || cleanString(item.medication) || 'Unknown Medication',
        dosage: cleanString(item.dosage),
        frequency: cleanString(item.frequency),
        start_date: cleanString(item.start_date) || cleanString(item.date),
        end_date: cleanString(item.end_date),
        notes: cleanString(item.notes) || cleanString(item.instructions),
        prescribed_by: cleanString(item.prescribed_by),
        is_active: item.is_active
      }))
    }

    const viewDetails = (prescription) => {
      selectedPrescription.value = prescription
      showDetailsModal.value = true
    }

    onMounted(async () => {
      try {
        const medicationData = await getPatientMedication()
        console.log('Raw medication data:', medicationData)
        prescriptions.value = transformMedicationData(medicationData)
        console.log('Transformed prescriptions:', prescriptions.value)
      } catch (error) {
        console.error('Error loading prescriptions:', error)
        prescriptions.value = []
      }
    })

    return {
      search,
      showDetailsModal,
      selectedPrescription,
      filteredPrescriptions,
      hasValue,
      hasDetails,
      formatDate,
      isPrescriptionActive,
      getPrescriptionStatus,
      getStatusClass,
      getDaysRemaining,
      viewDetails
    }
  }
}
</script>
