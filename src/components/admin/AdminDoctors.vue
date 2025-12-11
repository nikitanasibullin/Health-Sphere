<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-3xl font-bold text-gray-800">
          <i class="fas fa-user-md text-green-500 mr-2"></i>Manage Doctors
        </h2>
        <button
          @click="showAddModal = true"
          class="bg-gradient-to-r from-green-600 to-teal-600 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-teal-700 shadow-lg transition"
        >
          <i class="fas fa-plus mr-2"></i>Add Doctor
        </button>
      </div>

      <!-- Search -->
      <div class="mb-6">
        <div class="relative">
          <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input
            v-model="search"
            type="text"
            placeholder="Search doctors by name or specialization..."
            class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
          >
        </div>
      </div>

      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-green-50 to-teal-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">ID</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Name</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Email</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Specialization</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Phone</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="doctor in filteredDoctors" :key="doctor.id" class="hover:bg-gray-50 transition">
              <td class="px-6 py-4 whitespace-nowrap font-semibold text-gray-900">{{ doctor.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gradient-to-r from-green-400 to-teal-400 rounded-full flex items-center justify-center mr-3">
                    <span class="text-white font-bold">{{ doctor.name.charAt(0) }}</span>
                  </div>
                  <span class="font-semibold text-gray-900">{{ doctor.name }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ doctor.email }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold">
                  {{ doctor.specialization }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ doctor.phone }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button @click="editDoctor(doctor)" class="text-green-600 hover:text-green-800 mr-3" title="Edit">
                  <i class="fas fa-edit"></i>
                </button>
                <button @click="handleDelete(doctor.id)" class="text-red-600 hover:text-red-800" title="Delete">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
            <tr v-if="filteredDoctors.length === 0">
              <td colspan="6" class="px-6 py-8 text-center text-gray-500">
                <i class="fas fa-user-md text-4xl mb-2"></i>
                <p>No doctors found</p>
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
            {{ showEditModal ? 'Edit Doctor' : 'Add New Doctor' }}
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
                placeholder="Dr. Full Name"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Email</label>
              <input
                v-model="form.email"
                type="email"
                required
                placeholder="doctor@hospital.com"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Phone</label>
              <input
                v-model="form.phone"
                type="tel"
                required
                placeholder="Phone number"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
            </div>

            <div v-if="showAddModal">
              <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
              <input
                v-model="form.password"
                type="password"
                required
                placeholder="Password"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
            </div>

            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Specialization</label>
              <select
                v-model="form.specialization"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select specialization...</option>
                <option value="Cardiology">Cardiology</option>
                <option value="Neurology">Neurology</option>
                <option value="Pediatrics">Pediatrics</option>
                <option value="Orthopedics">Orthopedics</option>
                <option value="Dermatology">Dermatology</option>
                <option value="General Practice">General Practice</option>
              </select>
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
              {{ showEditModal ? 'Update' : 'Add Doctor' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData.js'

export default {
  name: 'AdminDoctors',
  setup() {
    const { doctors, addDoctor, updateDoctor, deleteDoctor, addActivity } = useHospitalData()

    const search = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const editingId = ref(null)

    const form = ref({
      name: '',
      email: '',
      phone: '',
      password: '',
      specialization: ''
    })

    const filteredDoctors = computed(() => {
      if (!search.value) return doctors.value
      const searchLower = search.value.toLowerCase()
      return doctors.value.filter(d =>
        d.name.toLowerCase().includes(searchLower) ||
        d.specialization.toLowerCase().includes(searchLower)
      )
    })

    const resetForm = () => {
      form.value = { name: '', email: '', phone: '', specialization: '' }
      editingId.value = null
    }

    const closeModals = () => {
      showAddModal.value = false
      showEditModal.value = false
      resetForm()
    }

    const editDoctor = (doctor) => {
      form.value = { ...doctor }
      editingId.value = doctor.id
      showEditModal.value = true
    }

    const handleSubmit = () => {
      if (showEditModal.value && editingId.value) {
        updateDoctor(editingId.value, { ...form.value })
        addActivity(`Doctor ${form.value.name} updated`, 'fas fa-edit', 'bg-green-500')
      } else {
        addDoctor({ ...form.value })
        addActivity(`New doctor ${form.value.name} added`, 'fas fa-user-md', 'bg-green-500')
      }
      closeModals()
    }

    const handleDelete = (id) => {
      if (confirm('Are you sure you want to delete this doctor?')) {
        const doctor = doctors.value.find(d => d.id === id)
        deleteDoctor(id)
        addActivity(`Doctor ${doctor?.name} removed`, 'fas fa-trash', 'bg-red-500')
      }
    }

    return {
      search,
      showAddModal,
      showEditModal,
      form,
      filteredDoctors,
      closeModals,
      editDoctor,
      handleSubmit,
      handleDelete
    }
  }
}
</script>
