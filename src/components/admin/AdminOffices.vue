<template>
  <div class="animate-fadeIn">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-gray-800">
        <i class="fas fa-door-open text-indigo-500 mr-2"></i>Offices
      </h2>
      <button
          @click="openAddModal"
          class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-indigo-700 hover:to-purple-700 shadow-lg transition"
      >
        <i class="fas fa-plus mr-2"></i>Add Office
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="bg-white rounded-2xl shadow-lg p-12 text-center">
      <i class="fas fa-spinner fa-spin text-indigo-500 text-4xl mb-4"></i>
      <p class="text-gray-500">Loading offices...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="officesList.length === 0" class="bg-white rounded-2xl shadow-lg p-12 text-center">
      <i class="fas fa-door-closed text-gray-300 text-6xl mb-4"></i>
      <p class="text-gray-500 text-lg">No offices found</p>
      <p class="text-gray-400 text-sm mt-2">Add your first office to get started</p>
    </div>

    <!-- Offices Grid -->
    <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      <div
          v-for="office in officesList"
          :key="office.id"
          class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
      >
        <div class="bg-gradient-to-r from-indigo-500 to-purple-600 p-4">
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center">
                <i class="fas fa-door-open text-white text-xl"></i>
              </div>
              <div class="ml-3 text-white">
                <h3 class="font-bold text-lg">Office {{ office.number }}</h3>
                <p class="text-indigo-100 text-sm">ID: {{ office.id }}</p>
              </div>
            </div>
          </div>
        </div>

        <div class="p-4">
          <div class="flex justify-between items-center">
            <span class="text-gray-600 text-sm">
              <i class="fas fa-hashtag text-gray-400 mr-1"></i>
              Room {{ office.number }}
            </span>
            <button
                @click="handleDelete(office.id, office.number)"
                class="text-red-500 hover:text-red-700 hover:bg-red-50 p-2 rounded-lg transition"
                title="Delete office"
            >
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Summary Card -->
    <div v-if="officesList.length > 0" class="mt-6 bg-white rounded-xl shadow-lg p-6">
      <div class="flex items-center justify-between">
        <div class="flex items-center">
          <div class="w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
            <i class="fas fa-building text-indigo-600 text-xl"></i>
          </div>
          <div class="ml-4">
            <p class="text-gray-500 text-sm">Total Offices</p>
            <p class="text-2xl font-bold text-gray-800">{{ officesList.length }}</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div
        v-if="showModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
        @click.self="closeModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 mx-4">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">
            <i class="fas fa-plus-circle text-indigo-500 mr-2"></i>Add New Office
          </h3>
          <button @click="closeModal" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- Office Number -->
          <div class="mb-6">
            <label class="block text-gray-700 text-sm font-bold mb-2">
              <i class="fas fa-hashtag text-gray-400 mr-1"></i>
              Office Number
            </label>
            <input
                v-model="form.number"
                type="text"
                required
                placeholder="e.g., 101, A-201, etc."
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            >
            <p class="text-gray-400 text-xs mt-1">Enter a unique office/room number</p>
          </div>

          <!-- Error Message -->
          <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p class="text-red-600 text-sm">
              <i class="fas fa-exclamation-circle mr-1"></i>
              {{ error }}
            </p>
          </div>

          <!-- Buttons -->
          <div class="flex gap-4">
            <button
                type="button"
                @click="closeModal"
                class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button
                type="submit"
                :disabled="submitting"
                class="flex-1 px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 text-white rounded-lg hover:from-indigo-700 hover:to-purple-700 transition disabled:opacity-50"
            >
              <span v-if="submitting">
                <i class="fas fa-spinner fa-spin mr-2"></i>Adding...
              </span>
              <span v-else>
                <i class="fas fa-plus mr-2"></i>Add Office
              </span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useAdminData } from '../../composables/useAdminData'

export default {
  name: 'AdminOffices',
  setup() {
    const {
      offices,
      fetchOffices,
      addOffice,
      deleteOffice,
      initializeData
    } = useAdminData()

    const showModal = ref(false)
    const loading = ref(true)
    const submitting = ref(false)
    const error = ref('')
    const form = ref({
      number: ''
    })

    const officesList = computed(() => offices.value || [])

    const openAddModal = () => {
      form.value = { number: '' }
      error.value = ''
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      error.value = ''
    }

    const handleSubmit = async () => {
      if (!form.value.number.trim()) {
        error.value = 'Office number is required'
        return
      }

      submitting.value = true
      error.value = ''

      try {
        await addOffice({ number: form.value.number.trim() })
        closeModal()
      } catch (err) {
        error.value = err.message || 'Failed to add office'
      } finally {
        submitting.value = false
      }
    }

    const handleDelete = async (id, number) => {
      if (!confirm(`Delete Office ${number}? This action cannot be undone.`)) return

      try {
        await deleteOffice(id)
      } catch (err) {
        alert('Failed to delete: ' + (err.message || 'Unknown error'))
      }
    }

    onMounted(async () => {
      try {
        await initializeData()
      } finally {
        loading.value = false
      }
    })

    return {
      officesList,
      showModal,
      loading,
      submitting,
      error,
      form,
      openAddModal,
      closeModal,
      handleSubmit,
      handleDelete
    }
  }
}
</script>