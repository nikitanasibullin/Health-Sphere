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
              <h3 class="font-bold text-lg text-gray-800">{{ prescription.medication }}</h3>
              <p class="text-sm text-gray-600">
                Prescribed by {{ getDoctorName(prescription.doctorId) }}
              </p>
              <p class="text-sm text-gray-500">{{ formatDate(prescription.date) }}</p>
            </div>
            <span :class="getStatusClass(prescription)">
              {{ isActive(prescription) ? 'Active' : 'Expired' }}
            </span>
          </div>

          <div class="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-4 mb-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-xs font-semibold text-gray-500 uppercase">Dosage</p>
                <p class="text-gray-800 font-medium">{{ prescription.dosage }}</p>
              </div>
              <div>
                <p class="text-xs font-semibold text-gray-500 uppercase">Duration</p>
                <p class="text-gray-800 font-medium">{{ prescription.duration }}</p>
              </div>
            </div>
          </div>

          <div v-if="prescription.notes" class="mb-4">
            <p class="text-sm text-gray-600">
              <i class="fas fa-info-circle text-blue-500 mr-1"></i>
              <strong>Notes:</strong> {{ prescription.notes }}
            </p>
          </div>

          <div class="flex gap-2">
            <button
              @click="viewDetails(prescription)"
              class="flex-1 bg-blue-100 text-blue-700 py-2 rounded-lg hover:bg-blue-200 transition text-sm font-semibold"
            >
              <i class="fas fa-eye mr-1"></i>View Details
            </button>
            <button
              @click="requestRefill(prescription)"
              class="flex-1 bg-green-100 text-green-700 py-2 rounded-lg hover:bg-green-200 transition text-sm font-semibold"
            >
              <i class="fas fa-redo mr-1"></i>Request Refill
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Prescription Details Modal -->
    <div
      v-if="showDetailsModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showDetailsModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fadeIn">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">Prescription Details</h3>
          <button @click="showDetailsModal = false" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <div v-if="selectedPrescription" class="space-y-4">
          <div class="p-4 bg-gradient-to-r from-green-50 to-teal-50 rounded-xl">
            <h4 class="font-bold text-xl text-gray-800">{{ selectedPrescription.medication }}</h4>
          </div>

          <div class="space-y-3">
            <div class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-user-md text-green-500 mr-3 w-5"></i>
              <div>
                <p class="text-xs text-gray-500">Prescribed By</p>
                <p class="font-semibold">{{ getDoctorName(selectedPrescription.doctorId) }}</p>
              </div>
            </div>

            <div class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-calendar text-blue-500 mr-3 w-5"></i>
              <div>
                <p class="text-xs text-gray-500">Date</p>
                <p class="font-semibold">{{ formatDate(selectedPrescription.date) }}</p>
              </div>
            </div>

            <div class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-pills text-purple-500 mr-3 w-5"></i>
              <div>
                <p class="text-xs text-gray-500">Dosage</p>
                <p class="font-semibold">{{ selectedPrescription.dosage }}</p>
              </div>
            </div>

            <div class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-clock text-orange-500 mr-3 w-5"></i>
              <div>
                <p class="text-xs text-gray-500">Duration</p>
                <p class="font-semibold">{{ selectedPrescription.duration }}</p>
              </div>
            </div>

            <div v-if="selectedPrescription.notes" class="p-3 bg-yellow-50 rounded-lg">
              <p class="text-xs text-gray-500 mb-1">Special Instructions</p>
              <p class="text-gray-800">{{ selectedPrescription.notes }}</p>
            </div>
          </div>
        </div>

        <button
          @click="showDetailsModal = false"
          class="w-full mt-6 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
        >
          Close
        </button>
      </div>
    </div>

    <!-- Refill Request Modal -->
    <div
      v-if="showRefillModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showRefillModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fadeIn">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">Request Refill</h3>
          <button @click="showRefillModal = false" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <div v-if="selectedPrescription" class="mb-6">
          <p class="text-gray-600 mb-4">
            Request a refill for <strong>{{ selectedPrescription.medication }}</strong>?
          </p>

          <div class="p-4 bg-blue-50 rounded-lg">
            <p class="text-sm text-blue-800">
              <i class="fas fa-info-circle mr-2"></i>
              Your request will be sent to {{ getDoctorName(selectedPrescription.doctorId) }} for approval.
            </p>
          </div>
        </div>

        <div class="flex gap-4">
          <button
            @click="showRefillModal = false"
            class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
            @click="submitRefillRequest"
            class="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 transition"
          >
            <i class="fas fa-paper-plane mr-2"></i>Submit Request
          </button>
        </div>

        <div v-if="refillSuccess" class="mt-4 p-3 bg-green-100 text-green-700 rounded-lg animate-fadeIn">
          <i class="fas fa-check-circle mr-2"></i>Refill request submitted successfully!
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { usePatientData } from '../../composables/usePatientData'

export default {
  name: 'PatientPrescriptions',
  props: {
    patientId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const { getDoctorName, getPatientPrescriptions, addActivity } = usePatientData()

    const prescriptions = getPatientPrescriptions(props.patientId)

    const search = ref('')
    const showDetailsModal = ref(false)
    const showRefillModal = ref(false)
    const selectedPrescription = ref(null)
    const refillSuccess = ref(false)

    const filteredPrescriptions = computed(() => {
      if (!search.value) {
        return [...prescriptions.value].sort((a, b) => new Date(b.date) - new Date(a.date))
      }
      const searchLower = search.value.toLowerCase()
      return prescriptions.value
        .filter(p =>
          p.medication.toLowerCase().includes(searchLower) ||
          getDoctorName(p.doctorId).toLowerCase().includes(searchLower)
        )
        .sort((a, b) => new Date(b.date) - new Date(a.date))
    })

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const isActive = (prescription) => {
      // if prescribed within last 90 days, consider active
      const prescriptionDate = new Date(prescription.date)
      const today = new Date()
      const diffDays = Math.floor((today - prescriptionDate) / (1000 * 60 * 60 * 24))
      return diffDays <= 90
    }

    const getStatusClass = (prescription) => {
      return isActive(prescription)
        ? 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold'
        : 'px-3 py-1 bg-gray-100 text-gray-600 rounded-full text-xs font-semibold'
    }

    const viewDetails = (prescription) => {
      selectedPrescription.value = prescription
      showDetailsModal.value = true
    }

    const requestRefill = (prescription) => {
      selectedPrescription.value = prescription
      refillSuccess.value = false
      showRefillModal.value = true
    }

    const submitRefillRequest = () => {
      refillSuccess.value = true
      addActivity(
        `Refill requested for ${selectedPrescription.value.medication}`,
        'fas fa-redo',
        'bg-green-500'
      )

      setTimeout(() => {
        showRefillModal.value = false
        refillSuccess.value = false
      }, 2000)
    }

    return {
      search,
      showDetailsModal,
      showRefillModal,
      selectedPrescription,
      refillSuccess,
      filteredPrescriptions,
      getDoctorName,
      formatDate,
      isActive,
      getStatusClass,
      viewDetails,
      requestRefill,
      submitRefillRequest
    }
  }
}
</script>
