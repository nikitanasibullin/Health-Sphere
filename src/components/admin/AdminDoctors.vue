<template>
  <div class="animate-fadeIn space-y-6">
    <!-- Specializations Section -->
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">
          <i class="fas fa-tags text-purple-500 mr-2"></i>Specializations
        </h2>
        <button
            @click="showSpecializationModal = true"
            class="bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-5 py-2.5 rounded-lg hover:from-purple-700 hover:to-indigo-700 shadow-lg transition"
        >
          <i class="fas fa-plus mr-2"></i>Add Specialization
        </button>
      </div>

      <!-- Specializations Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-purple-50 to-indigo-50">
          <tr>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">ID</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Name</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Description</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Doctors Count</th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
          </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
          <tr v-for="spec in specializations" :key="spec.id" class="hover:bg-gray-50 transition">
            <td class="px-6 py-4 whitespace-nowrap font-semibold text-gray-900">{{ spec.id }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="w-10 h-10 bg-gradient-to-r from-purple-400 to-indigo-400 rounded-full flex items-center justify-center mr-3">
                  <i class="fas fa-stethoscope text-white"></i>
                </div>
                <span class="font-semibold text-gray-900">{{ spec.name }}</span>
              </div>
            </td>
            <td class="px-6 py-4 text-gray-700">
              <span v-if="spec.description" class="line-clamp-2">{{ spec.description }}</span>
              <span v-else class="text-gray-400 italic">No description</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-semibold">
                  {{ getDoctorCountBySpecialization(spec.name) }} doctors
                </span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex gap-3">
                <button
                    @click="editSpecialization(spec)"
                    class="text-blue-600 hover:text-blue-800"
                    title="Edit"
                >
                  <i class="fas fa-edit"></i>
                </button>
                <button
                    @click="handleDeleteSpecialization(spec.id)"
                    class="text-red-600 hover:text-red-800"
                    title="Delete"
                    :disabled="getDoctorCountBySpecialization(spec.name) > 0"
                    :class="{ 'opacity-50 cursor-not-allowed': getDoctorCountBySpecialization(spec.name) > 0 }"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="specializations.length === 0">
            <td colspan="5" class="px-6 py-8 text-center text-gray-500">
              <i class="fas fa-tags text-4xl mb-2 block"></i>
              <p>No specializations found</p>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Doctors Section -->
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-2xl font-bold text-gray-800">
          <i class="fas fa-user-md text-green-500 mr-2"></i>Doctors
        </h2>
        <button
            @click="showAddModal = true"
            class="bg-gradient-to-r from-green-600 to-teal-600 text-white px-5 py-2.5 rounded-lg hover:from-green-700 hover:to-teal-700 shadow-lg transition"
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

      <!-- Doctors Table -->
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
            <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ doctor.phone_number }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <button @click="handleDeleteDoctor(doctor.id)" class="text-red-600 hover:text-red-800" title="Delete">
                <i class="fas fa-trash"></i>
              </button>
            </td>
          </tr>
          <tr v-if="filteredDoctors.length === 0">
            <td colspan="6" class="px-6 py-8 text-center text-gray-500">
              <i class="fas fa-user-md text-4xl mb-2 block"></i>
              <p>No doctors found</p>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Add/Edit Doctor Modal -->
    <div
        v-if="showAddModal || showEditModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeModals"
    >
      <div
          class="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] flex flex-col animate-fadeIn"
          @click.stop
      >
        <div class="flex justify-between items-center p-8 pb-6 flex-shrink-0">
          <h3 class="text-2xl font-bold text-gray-800">
            {{ showEditModal ? 'Edit Doctor' : 'Add New Doctor' }}
          </h3>
          <button @click="closeModals" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <div class="flex-1 overflow-y-auto px-8">
          <form @submit.prevent="handleDoctorSubmit" id="doctorForm">
            <div class="space-y-4">
              <div>
                <label class="block text-gray-700 text-sm font-bold mb-2">First Name</label>
                <input
                    v-model="doctorForm.firstName"
                    type="text"
                    required
                    placeholder="First Name"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
              </div>
              <div>
                <label class="block text-gray-700 text-sm font-bold mb-2">Last Name</label>
                <input
                    v-model="doctorForm.lastName"
                    type="text"
                    required
                    placeholder="Last Name"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
              </div>
              <div>
                <label class="block text-gray-700 text-sm font-bold mb-2">Patronymic</label>
                <input
                    v-model="doctorForm.patronymic"
                    type="text"
                    required
                    placeholder="Patronymic"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
              </div>
              <div>
                <label class="block text-gray-700 text-sm font-bold mb-2">Email</label>
                <input
                    v-model="doctorForm.email"
                    type="email"
                    required
                    placeholder="doctor@hospital.com"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
              </div>
              <div>
                <label class="block text-gray-700 text-sm font-bold mb-2">Phone</label>
                <input
                    v-model="doctorForm.phone"
                    type="tel"
                    required
                    placeholder="Phone number"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
              </div>

              <div v-if="showAddModal">
                <label class="block text-gray-700 text-sm font-bold mb-2">Password</label>
                <input
                    v-model="doctorForm.password"
                    type="password"
                    required
                    placeholder="Password"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                >
              </div>

              <div>
                <label class="block text-gray-700 text-sm font-bold mb-2">Specialization</label>
                <div class="relative">
                  <select
                      v-model="doctorForm.specialization_id"
                      required
                      class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 appearance-none"
                  >
                    <option value="">Select specialization...</option>
                    <option
                        v-for="spec in specializations"
                        :key="spec.id"
                        :value="spec.id"
                    >
                      {{ spec.name }}
                    </option>
                  </select>
                  <i class="fas fa-chevron-down absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 pointer-events-none"></i>
                </div>
              </div>
            </div>
          </form>
        </div>

        <div class="flex gap-4 p-8 pt-6 flex-shrink-0">
          <button
              type="button"
              @click="closeModals"
              class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
              type="submit"
              form="doctorForm"
              class="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-teal-600 text-white rounded-lg hover:from-green-700 hover:to-teal-700 transition"
          >
            {{ showEditModal ? 'Update' : 'Add Doctor' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Add/Edit Specialization Modal -->
    <div
        v-if="showSpecializationModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeSpecializationModal"
    >
      <div
          class="bg-white rounded-2xl shadow-2xl w-full max-w-md animate-fadeIn"
          @click.stop
      >
        <div class="flex justify-between items-center p-8 pb-6">
          <h3 class="text-2xl font-bold text-gray-800">
            <i class="fas fa-tags text-purple-500 mr-2"></i>
            {{ editingSpecializationId ? 'Edit Specialization' : 'Add Specialization' }}
          </h3>
          <button @click="closeSpecializationModal" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <div class="px-8">
          <form @submit.prevent="handleSpecializationSubmit" id="specializationForm">
            <div class="space-y-4">
              <div>
                <label class="block text-gray-700 text-sm font-bold mb-2">
                  Name <span class="text-red-500">*</span>
                </label>
                <input
                    v-model="specializationForm.name"
                    type="text"
                    required
                    placeholder="e.g., Cardiology, Neurology..."
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
              </div>
              <div>
                <label class="block text-gray-700 text-sm font-bold mb-2">
                  Description <span class="text-gray-400 font-normal">(optional)</span>
                </label>
                <textarea
                    v-model="specializationForm.description"
                    rows="3"
                    placeholder="Brief description of the specialization..."
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500 resize-none"
                ></textarea>
              </div>
            </div>
          </form>
        </div>

        <div class="flex gap-4 p-8 pt-6">
          <button
              type="button"
              @click="closeSpecializationModal"
              class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
          >
            Cancel
          </button>
          <button
              type="submit"
              form="specializationForm"
              :disabled="isSubmitting"
              class="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-lg hover:from-purple-700 hover:to-indigo-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span v-if="isSubmitting">
              <i class="fas fa-spinner fa-spin mr-2"></i>Saving...
            </span>
            <span v-else>{{ editingSpecializationId ? 'Update' : 'Add Specialization' }}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAdminData } from '../../composables/useAdminData'

export default {
  name: 'AdminDoctors',
  setup() {
    const {
      initializeData,
      specializations,
      doctors,
      addDoctor,
      updateDoctor,
      deleteDoctor,
      addSpecialization,
      updateSpecialization,
      deleteSpecialization
    } = useAdminData()

    const search = ref('')
    const showAddModal = ref(false)
    const showEditModal = ref(false)
    const showSpecializationModal = ref(false)
    const editingDoctorId = ref(null)
    const editingSpecializationId = ref(null)
    const isSubmitting = ref(false)

    // Doctor form
    const doctorForm = ref({
      firstName: '',
      lastName: '',
      patronymic: '',
      email: '',
      phone: '',
      password: '',
      specialization_id: ''
    })

    // Specialization form
    const specializationForm = ref({
      name: '',
      description: ''
    })

    // Computed
    const filteredDoctors = computed(() => {
      if (!search.value) return doctors.value
      const searchLower = search.value.toLowerCase()
      return doctors.value.filter(d =>
          d.name.toLowerCase().includes(searchLower) ||
          d.specialization.toLowerCase().includes(searchLower)
      )
    })

    const getDoctorCountBySpecialization = (specName) => {
      return doctors.value.filter(d => d.specialization === specName).length
    }

    // Reset functions
    const resetDoctorForm = () => {
      doctorForm.value = {
        firstName: '',
        lastName: '',
        patronymic: '',
        email: '',
        phone: '',
        password: '',
        specialization_id: ''
      }
      editingDoctorId.value = null
    }

    const resetSpecializationForm = () => {
      specializationForm.value = {
        name: '',
        description: ''
      }
      editingSpecializationId.value = null
    }

    // Close modals
    const closeModals = () => {
      showAddModal.value = false
      showEditModal.value = false
      resetDoctorForm()
    }

    const closeSpecializationModal = () => {
      showSpecializationModal.value = false
      resetSpecializationForm()
    }

    // Edit functions
    const editDoctor = (doctor) => {
      doctorForm.value = {
        firstName: doctor.first_name,
        lastName: doctor.last_name,
        patronymic: doctor.patronymic,
        email: doctor.email,
        phone: doctor.phone_number,
        password: '',
        specialization_id: doctor.specialization_id || ''
      }
      editingDoctorId.value = doctor.id
      showEditModal.value = true
    }

    const editSpecialization = (spec) => {
      specializationForm.value = {
        name: spec.name,
        description: spec.description || ''
      }
      editingSpecializationId.value = spec.id
      showSpecializationModal.value = true
    }

    // Submit functions
    const handleDoctorSubmit = async () => {
      if (showEditModal.value && editingDoctorId.value) {
        await updateDoctor(editingDoctorId.value, { ...doctorForm.value })
      } else {
        await addDoctor({
          first_name: doctorForm.value.firstName,
          last_name: doctorForm.value.lastName,
          patronymic: doctorForm.value.patronymic,
          phone_number: doctorForm.value.phone,
          email: doctorForm.value.email,
          password: doctorForm.value.password,
          specialization_id: doctorForm.value.specialization_id
        })
      }
      closeModals()
    }

    const handleSpecializationSubmit = async () => {
      if (!specializationForm.value.name.trim()) return

      isSubmitting.value = true
      try {
        const data = {
          name: specializationForm.value.name.trim(),
          description: specializationForm.value.description.trim() || null
        }

        if (editingSpecializationId.value) {
          await updateSpecialization(editingSpecializationId.value, data)
        } else {
          await addSpecialization(data)
        }
        closeSpecializationModal()
      } catch (error) {
        console.error('Failed to save specialization:', error)
      } finally {
        isSubmitting.value = false
      }
    }

    // Delete functions
    const handleDeleteDoctor = (id) => {
      if (confirm('Are you sure you want to delete this doctor?')) {
        deleteDoctor(id)
      }
    }

    const handleDeleteSpecialization = (id) => {
      const spec = specializations.value.find(s => s.id === id)
      const doctorCount = getDoctorCountBySpecialization(spec?.name)

      if (doctorCount > 0) {
        alert(`Cannot delete this specialization. There are ${doctorCount} doctor(s) assigned to it.`)
        return
      }

      if (confirm('Are you sure you want to delete this specialization?')) {
        deleteSpecialization(id)
      }
    }

    onMounted(async () => {
      await initializeData()
    })

    return {
      search,
      showAddModal,
      showEditModal,
      showSpecializationModal,
      doctorForm,
      specializationForm,
      filteredDoctors,
      specializations,
      isSubmitting,
      editingSpecializationId,
      getDoctorCountBySpecialization,
      closeModals,
      closeSpecializationModal,
      editDoctor,
      editSpecialization,
      handleDoctorSubmit,
      handleSpecializationSubmit,
      handleDeleteDoctor,
      handleDeleteSpecialization
    }
  }
}
</script>
