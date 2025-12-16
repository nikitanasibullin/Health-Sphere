<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-calendar-alt text-purple-500 mr-2"></i>My Appointments
      </h2>

      <!-- Filter -->
      <div class="mb-6 flex flex-wrap gap-4">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="activeFilter = filter.value"
          :class="[
            'px-4 py-2 rounded-lg font-semibold transition',
            activeFilter === filter.value
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
          ]"
        >
          {{ filter.label }}
        </button>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-purple-50 to-pink-50">
            <tr>
              <th
                class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"
              >
                Patient
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"
              >
                Date
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"
              >
                Time
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider"
              >
                Actions
              </th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr
              v-for="apt in filteredAppointments"
              :key="apt.id"
              class="hover:bg-gray-50 transition"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div
                    class="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center mr-3"
                  >
                    <span class="text-white font-bold">{{
                      getPatientName(apt.patientId).charAt(0)
                    }}</span>
                  </div>
                  <span class="font-semibold text-gray-900">{{
                    `${apt.patient.first_name} ${apt.patient.last_name} ${apt.patient.patronymic}`
                  }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ apt.schedule.date }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">
                {{ apt.schedule.start_time }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(apt.status)">{{ capitalizeStatus(apt.status) }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button
                  @click="openEditModal(apt)"
                  class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-semibold transition flex items-center gap-2"
                >
                  <i class="fas fa-edit"></i>
                  Edit
                </button>
              </td>
            </tr>
            <tr v-if="filteredAppointments.length === 0">
              <td colspan="5" class="px-6 py-12 text-center text-gray-500">
                <i class="fas fa-calendar-times text-4xl mb-4"></i>
                <p>No appointments found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal -->
    <div
      v-if="showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click.self="closeEditModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div
          class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center z-10"
        >
          <h3 class="text-2xl font-bold text-gray-800">
            <i class="fas fa-edit text-purple-500 mr-2"></i>Edit Appointment
          </h3>
          <button @click="closeEditModal" class="text-gray-400 hover:text-gray-600 transition">
            <i class="fas fa-times text-2xl"></i>
          </button>
        </div>

        <form @submit.prevent="saveAppointment" class="p-6 space-y-6">
          <!-- Appointment Status -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Appointment Status
            </label>
            <select
              v-model="editForm.status"
              class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
              required
            >
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <!-- Appointment Information -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Appointment Information
            </label>
            <textarea
              v-model="editForm.information"
              rows="6"
              class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
              placeholder="Enter detailed appointment information, notes, diagnosis, etc."
            ></textarea>
          </div>

          <!-- Prescriptions Section -->
          <div class="border-t pt-6">
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-lg font-bold text-gray-800">
                <i class="fas fa-pills text-purple-500 mr-2"></i>Prescriptions
              </h4>
              <button
                type="button"
                @click="addPrescription"
                class="px-4 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition flex items-center gap-2"
              >
                <i class="fas fa-plus"></i>
                Add Prescription
              </button>
            </div>

            <!-- Prescription Items -->
            <div
              v-for="(prescription, index) in editForm.prescriptions"
              :key="index"
              class="mb-6 p-4 border-2 border-purple-200 rounded-lg bg-purple-50"
            >
              <div class="flex justify-between items-center mb-4">
                <h5 class="font-bold text-gray-800">Prescription #{{ index + 1 }}</h5>
                <button
                  v-if="editForm.prescriptions.length > 1"
                  type="button"
                  @click="removePrescription(index)"
                  class="text-red-600 hover:text-red-800 transition"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>

              <div class="space-y-4">
                <!-- Medicament Name -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2">
                    Medicament Name
                  </label>
                  <input
                    v-model="prescription.medicament_name"
                    type="text"
                    class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
                    placeholder="Enter medicament name"
                  />
                </div>

                <!-- Dosage -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2"> Dosage </label>
                  <input
                    v-model="prescription.dosage"
                    type="text"
                    class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
                    placeholder="e.g., 500mg"
                  />
                </div>

                <!-- Frequency -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2"> Frequency </label>
                  <input
                    v-model="prescription.frequency"
                    type="text"
                    class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
                    placeholder="e.g., Twice daily, Every 6 hours"
                  />
                </div>

                <div class="grid grid-cols-2 gap-4">
                  <!-- Start Date -->
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">
                      Start Date
                    </label>
                    <input
                      v-model="prescription.start_date"
                      type="date"
                      class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
                    />
                  </div>

                  <!-- End Date -->
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2"> End Date </label>
                    <input
                      v-model="prescription.end_date"
                      type="date"
                      class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
                    />
                  </div>
                </div>

                <!-- Notes -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2"> Notes </label>
                  <textarea
                    v-model="prescription.notes"
                    rows="3"
                    class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500 bg-white"
                    placeholder="Additional notes for this prescription..."
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- No Prescriptions Message -->
            <div v-if="editForm.prescriptions.length === 0" class="text-center py-8 text-gray-500">
              <i class="fas fa-prescription-bottle text-4xl mb-2"></i>
              <p>No prescriptions added yet</p>
            </div>
          </div>

          <!-- Contraindications Section -->
          <div class="border-t pt-6">
            <h4 class="text-lg font-bold text-gray-800 mb-4">
              <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>Contraindications
            </h4>
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Contraindication Information
              </label>
              <textarea
                v-model="editForm.contraindications"
                rows="4"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter any contraindications, allergies, or warnings related to the prescriptions..."
              ></textarea>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end gap-4 pt-4 border-t sticky bottom-0 bg-white">
            <button
              type="button"
              @click="closeEditModal"
              class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition flex items-center gap-2"
            >
              <i class="fas fa-save"></i>
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useDoctorData } from '../../composables/useDoctorData'

export default {
  name: 'DoctorAppointments',
  setup() {
    const {
      addPatientContraindications,
      addMedicamentsForAppointment,
      getPatientName,
      getDoctorAppointments,
      updateAppointmentStatus,
    } = useDoctorData()
    const myAppointments = ref([])
    const activeFilter = ref('all')
    const showEditModal = ref(false)
    const currentAppointment = ref(null)
    const editForm = ref({
      status: '',
      information: '',
      prescriptions: [],
      contraindications: '',
    })

    const filters = [
      { label: 'All', value: 'all' },
      { label: 'Scheduled', value: 'scheduled' },
      { label: 'Completed', value: 'completed' },
      { label: 'Cancelled', value: 'cancelled' },
    ]

    const filteredAppointments = computed(() => {
      if (!myAppointments.value) {
        return []
      }
      if (activeFilter.value === 'all') {
        return myAppointments.value
      }
      return myAppointments.value.filter((a) => a.status === activeFilter.value)
    })

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      })
    }

    const capitalizeStatus = (status) => {
      if (!status) return ''
      return status.charAt(0).toUpperCase() + status.slice(1)
    }

    const getStatusClass = (status) => {
      const classes = {
        scheduled: 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold',
        completed: 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold',
        cancelled: 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold',
      }
      return classes[status] || classes['scheduled']
    }

    const createEmptyPrescription = () => ({
      medicament_name: '',
      dosage: '',
      frequency: '',
      start_date: '',
      end_date: '',
      notes: '',
    })

    const addPrescription = () => {
      editForm.value.prescriptions.push(createEmptyPrescription())
    }

    const removePrescription = (index) => {
      editForm.value.prescriptions.splice(index, 1)
    }

    const openEditModal = (appointment) => {
      currentAppointment.value = appointment

      // Initialize prescriptions array
      let prescriptions = []
      if (appointment.prescriptions && appointment.prescriptions.length > 0) {
        prescriptions = appointment.prescriptions.map((p) => ({ ...p }))
      } else if (appointment.medicament_name) {
        // Legacy: convert old single prescription format to array
        prescriptions = [
          {
            medicament_name: appointment.medicament_name || '',
            dosage: appointment.dosage || '',
            frequency: appointment.frequency || '',
            start_date: appointment.start_date || '',
            end_date: appointment.end_date || '',
            notes: appointment.prescription_notes || '',
          },
        ]
      } else {
        // No prescriptions, start with one empty
        prescriptions = [createEmptyPrescription()]
      }

      editForm.value = {
        status: appointment.status || 'scheduled',
        information: appointment.information || '',
        prescriptions: prescriptions,
        contraindications: appointment.contraindications || '',
      }
      showEditModal.value = true
    }

    const closeEditModal = () => {
      showEditModal.value = false
      currentAppointment.value = null
      editForm.value = {
        status: '',
        information: '',
        prescriptions: [],
        contraindications: '',
      }
    }
    console.log(currentAppointment.value)
    const saveAppointment = async () => {
      if (!currentAppointment.value) return

      // Get current doctor ID (adjust based on your auth implementation)

      const updateData = {
        status: editForm.value.status,
        information: editForm.value.information,
      }

      try {
        await updateAppointmentStatus(currentAppointment.value.id, updateData)
        for (const prescription of editForm.value.prescriptions) {
          if (prescription.medicament_name && prescription.medicament_name.trim()) {
            const prescriptionData = {
              medicament_name: prescription.medicament_name,
              dosage: prescription.dosage,
              frequency: prescription.frequency,
              start_date: prescription.start_date,
              end_date: prescription.end_date,
              notes: prescription.notes,
              prescribed_by: '',
            }

            await addMedicamentsForAppointment(currentAppointment.value.id, prescriptionData)
          }
        }
        if (editForm.value.prescriptions !== '') {
          await addPatientContraindications(
            currentAppointment.value.patient.id,
            Array(editForm.value.contraindications),
          )
        }
        closeEditModal()
      } catch (error) {
        console.error('Error updating appointment:', error)
      }
    }

    onMounted(async () => {
      myAppointments.value = (await getDoctorAppointments()) || []
    })

    return {
      activeFilter,
      filters,
      filteredAppointments,
      getPatientName,
      formatDate,
      getStatusClass,
      capitalizeStatus,
      showEditModal,
      editForm,
      openEditModal,
      closeEditModal,
      saveAppointment,
      addPrescription,
      removePrescription,
    }
  },
}
</script>
