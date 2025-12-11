<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-3xl font-bold text-gray-800">
          <i class="fas fa-users text-blue-500 mr-2"></i>Manage Patients
        </h2>
        <button
          @click="showAddModal = true"
          class="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 shadow-lg transition"
        >
          <i class="fas fa-plus mr-2"></i>Add Patient
        </button>
      </div>

      <!-- Search -->
      <div class="mb-6">
        <div class="relative">
          <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="search"
            type="text"
            placeholder="Search patients by name, email, or phone..."
            class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-blue-50 to-purple-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">ID</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Name</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Email</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Phone</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Age</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="patient in filteredPatients" :key="patient.id" class="hover:bg-gray-50 transition">
              <td class="px-6 py-4 whitespace-nowrap font-semibold text-gray-900">{{ patient.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center mr-3">
                    <span class="text-white font-bold">{{ patient.name.charAt(0) }}</span>
                  </div>
                  <span class="font-semibold text-gray-900">{{ patient.name }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ patient.email }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ patient.phone }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ patient.age }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button @click="viewPatient(patient)" class="text-blue-600 hover:text-blue-800 mr-3" title="View">
                  <i class="fas fa-eye"></i>
                </button>
                <button @click="editPatient(patient)" class="text-green-600 hover:text-green-800 mr-3" title="Edit">
                  <i class="fas fa-edit"></i>
                </button>
                <button @click="handleDelete(patient.id)" class="text-red-600 hover:text-red-800" title="Delete">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="filteredPatients.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                <i class="fas fa-search text-4xl mb-2"></i>
                <p>No patients found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Modal -->
    <div
      v-if="showAddModal || showEditModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeModals"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fadeIn">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">
            {{ showEditModal ? 'Edit Patient' : 'Add New Patient' }}
          </h3>
          <button @click="closeModals" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Name</label>
              <input
                v-model="form.name"
                type="text"
                required
                placeholder="Enter full name"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Email</label>
              <input
                v-model="form.email"
                type="email"
                required
                placeholder="Enter email address"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Phone</label>
              <input
                v-model="form.phone"
                type="tel"
                required
                placeholder="Enter phone number"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Age</label>
              <input
                v-model="form.age"
                type="number"
                required
                min="1"
                max="120"
                placeholder="Enter age"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
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
              class="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition"
            >
              {{ showEditModal ? 'Update' : 'Add Patient' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- View Modal -->
    <div
      v-if="showViewModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showViewModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fadeIn">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">Patient Details</h3>
          <button @click="showViewModal = false" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <div v-if="selectedPatient" class="space-y-4">
          <div class="flex items-center mb-6">
            <div class="w-16 h-16 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center mr-4">
              <span class="text-white font-bold text-2xl">{{ selectedPatient.name.charAt(0) }}</span>
            </div>
            <div>
              <h4 class="text-xl font-bold text-gray-800">{{ selectedPatient.name }}</h4>
              <p class="text-gray-500">Patient ID: {{ selectedPatient.id }}</p>
            </div>
          </div>

          <div class="space-y-3">
            <div class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-envelope text-blue-500 mr-3"></i>
              <span>{{ selectedPatient.email }}</span>
            </div>
            <div class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-phone text-green-500 mr-3"></i>
              <span>{{ selectedPatient.phone }}</span>
            </div>
            <div class="flex items-center p-3 bg-gray-50 rounded-lg">
              <i class="fas fa-birthday-cake text-purple-500 mr-3"></i>
              <span>{{ selectedPatient.age }} years old</span>
            </div>
          </div>
        </div>

        <button
          @click="showViewModal = false"
          class="w-full mt-6 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData.js'

export default {
  name: 'AdminPatients',
  setup() {
    const { patients, addPatient, updatePatient, deletePatient, addActivity } = useHospitalData()

    const search = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const showViewModal = ref(false)
    const selectedPatient = ref(null)
    const editingId = ref(null)

    const form = ref({
      name: '',
      email: '',
      phone: '',
      age: ''
    })

    const filteredPatients = computed(() => {
      if (!search.value) return patients.value
      const searchLower = search.value.toLowerCase()
      return patients.value.filter(p =>
        p.name.toLowerCase().includes(searchLower) ||
        p.email.toLowerCase().includes(searchLower) ||
        p.phone.includes(search.value)
      )
    })

    const resetForm = () => {
      form.value = { name: '', email: '', phone: '', age: '' }
      editingId.value = null
    }

    const closeModals = () => {
      showAddModal.value = false
      showEditModal.value = false
      resetForm()
    }

    const viewPatient = (patient) => {
      selectedPatient.value = patient
      showViewModal.value = true
    }

    const editPatient = (patient) => {
      form.value = { ...patient }
      editingId.value = patient.id
      showEditModal.value = true
    }

    const handleSubmit = () => {
      if (showEditModal.value && editingId.value) {
        updatePatient(editingId.value, {
          name: form.value.name,
          email: form.value.email,
          phone: form.value.phone,
          age: parseInt(form.value.age)
        })
        addActivity(`Patient ${form.value.name} updated`, 'fas fa-edit', 'bg-blue-500')
      } else {
        addPatient({
          name: form.value.name,
          email: form.value.email,
          phone: form.value.phone,
          age: parseInt(form.value.age)
        })
        addActivity(`New patient ${form.value.name} registered`, 'fas fa-user-plus', 'bg-green-500')
      }
      closeModals()
    }

    const handleDelete = (id) => {
      if (confirm('Are you sure you want to delete this patient?')) {
        const patient = patients.value.find(p => p.id === id)
        deletePatient(id)
        addActivity(`Patient ${patient?.name} deleted`, 'fas fa-trash', 'bg-red-500')
      }
    }

    return {
      search,
      showAddModal,
      showEditModal,
      showViewModal,
      selectedPatient,
      form,
      filteredPatients,
      closeModals,
      viewPatient,
      editPatient,
      handleSubmit,
      handleDelete
    }
  }
}
</script>
