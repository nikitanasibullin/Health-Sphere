<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-3xl font-bold text-gray-800">
          <i class="fas fa-prescription text-green-500 mr-2"></i>Prescriptions
        </h2>
        <button
          @click="showAddModal = true"
          class="bg-gradient-to-r from-green-600 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-teal-700 shadow-lg transition"
        >
          <i class="fas fa-plus mr-2"></i>New Prescription
        </button>
      </div>

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

      <!-- Prescriptions Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div
          v-for="prescription in filteredPrescriptions"
          :key="prescription.id"
          class="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition card-hover"
        >
          <div class="flex justify-between items-start mb-4">
            <div>
              <h3 class="font-bold text-lg text-gray-800">{{ getPatientName(prescription.patientId) }}</h3>
              <p class="text-sm text-gray-600">{{ prescription.date }}</p>
            </div>
            <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-xs font-semibold">
              Active
            </span>
          </div>

          <div class="bg-gradient-to-r from-green-50 to-teal-50 rounded-lg p-4 mb-4">
            <p class="text-sm font-semibold text-gray-700 mb-1">Medication:</p>
            <p class="text-gray-800 font-medium">{{ prescription.medication }}</p>
          </div>

          <div class="space-y-2 text-sm">
            <p class="text-gray-600">
              <strong class="text-gray-700">Dosage:</strong> {{ prescription.dosage }}
            </p>
            <p class="text-gray-600">
              <strong class="text-gray-700">Duration:</strong> {{ prescription.duration }}
            </p>
            <p v-if="prescription.notes" class="text-gray-600">
              <strong class="text-gray-700">Notes:</strong> {{ prescription.notes }}
            </p>
          </div>

          <div class="flex gap-2 mt-4">
            <button
              @click="editPrescription(prescription)"
              class="flex-1 bg-blue-100 text-blue-700 py-2 rounded-lg hover:bg-blue-200 transition"
            >
              <i class="fas fa-edit mr-1"></i>Edit
            </button>
            <button
              @click="printPrescription(prescription)"
              class="flex-1 bg-gray-100 text-gray-700 py-2 rounded-lg hover:bg-gray-200 transition"
            >
              <i class="fas fa-print mr-1"></i>Print
            </button>
          </div>
        </div>

        <div v-if="filteredPrescriptions.length === 0" class="col-span-full text-center py-12 text-gray-500">
          <i class="fas fa-prescription text-4xl mb-4"></i>
          <p>No prescriptions found</p>
        </div>
      </div>
    </div>

    <!-- Add/Edit Prescription Modal -->
    <div
      v-if="showAddModal || showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeModals"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fadeIn">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">
            {{ showEditModal ? 'Edit Prescription' : 'New Prescription' }}
          </h3>
          <button @click="closeModals" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Patient</label>
              <select
                v-model="form.patientId"
                required
                :disabled="showEditModal"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 disabled:bg-gray-100"
              >
                <option value="">Select patient...</option>
                <option v-for="patient in myPatients" :key="patient.id" :value="patient.id">
                  {{ patient.name }}
                </option>
              </select>
            </div>

            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Medication</label>
              <input
                v-model="form.medication"
                type="text"
                required
                placeholder="e.g., Lisinopril 10mg"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
            </div>

            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Dosage</label>
              <input
                v-model="form.dosage"
                type="text"
                required
                placeholder="e.g., 1 tablet twice daily"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
            </div>

            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Duration</label>
              <input
                v-model="form.duration"
                type="text"
                required
                placeholder="e.g., 30 days"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
            </div>

            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Notes (Optional)</label>
              <textarea
                v-model="form.notes"
                rows="3"
                placeholder="Additional instructions..."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              ></textarea>
            </div>
          </div>

          <div class="flex gap-4 mt-6">
            <button
              type="button"
              @click="closeModals"
              class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 transition"
            >
              {{ showEditModal ? 'Update' : 'Create Prescription' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useDoctorData } from '../../composables/useDoctorData'

export default {
  name: 'DoctorPrescriptions',
  props: {
    doctorId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const {
      getPatientName,
      getDoctorPatients,
      getDoctorPrescriptions,
      addPrescription,
      updatePrescription,
      addActivity
    } = useDoctorData()

    const myPatients = getDoctorPatients(props.doctorId)
    const myPrescriptions = getDoctorPrescriptions(props.doctorId)

    const search = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const editingId = ref(null)

    const form = ref({
      patientId: '',
      medication: '',
      dosage: '',
      duration: '',
      notes: ''
    })

    const filteredPrescriptions = computed(() => {
      if (!search.value) return myPrescriptions.value
      const searchLower = search.value.toLowerCase()
      return myPrescriptions.value.filter(p =>
        getPatientName(p.patientId).toLowerCase().includes(searchLower) ||
        p.medication.toLowerCase().includes(searchLower)
      )
    })

    const resetForm = () => {
      form.value = {
        patientId: '',
        medication: '',
        dosage: '',
        duration: '',
        notes: ''
      }
      editingId.value = null
    }

    const closeModals = () => {
      showAddModal.value = false
      showEditModal.value = false
      resetForm()
    }

    const editPrescription = (prescription) => {
      form.value = { ...prescription }
      editingId.value = prescription.id
      showEditModal.value = true
    }

    const handleSubmit = () => {
      if (showEditModal.value && editingId.value) {
        updatePrescription(editingId.value, {
          medication: form.value.medication,
          dosage: form.value.dosage,
          duration: form.value.duration,
          notes: form.value.notes
        })
        addActivity('Prescription updated', 'fas fa-edit', 'bg-blue-500')
      } else {
        addPrescription({
          patientId: parseInt(form.value.patientId),
          doctorId: props.doctorId,
          medication: form.value.medication,
          dosage: form.value.dosage,
          duration: form.value.duration,
          notes: form.value.notes
        })
        addActivity(`New prescription created for ${getPatientName(parseInt(form.value.patientId))}`, 'fas fa-prescription', 'bg-green-500')
      }
      closeModals()
    }

    const printPrescription = (prescription) => {
      alert(`Printing prescription for ${getPatientName(prescription.patientId)}\n\nMedication: ${prescription.medication}\nDosage: ${prescription.dosage}\nDuration: ${prescription.duration}`)
    }

    return {
      search,
      showAddModal,
      showEditModal,
      form,
      myPatients,
      filteredPrescriptions,
      getPatientName,
      closeModals,
      editPrescription,
      handleSubmit,
      printPrescription
    }
  }
}
</script>
