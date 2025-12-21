<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-pills text-teal-500 mr-2"></i>Medicaments Management
      </h2>

      <!-- Header with Search and Add Button -->
      <div class="mb-6 flex flex-wrap justify-between items-center gap-4">
        <div class="relative">
          <i class="fas fa-search absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input
              v-model="searchQuery"
              type="text"
              placeholder="Search medicaments..."
              class="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-teal-500 w-64"
          />
        </div>
        <button
            @click="openAddModal"
            class="px-4 py-2 bg-teal-600 text-white rounded-lg font-semibold hover:bg-teal-700 transition flex items-center gap-2"
        >
          <i class="fas fa-plus"></i>
          Add Medicament
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <i class="fas fa-spinner fa-spin text-4xl text-teal-500 mb-4"></i>
        <p class="text-gray-600">Loading medicaments...</p>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-teal-50 to-cyan-50">
          <tr>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Medicament Name
            </th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Medicament Contraindications
            </th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Other Contraindications
            </th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Actions
            </th>
          </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
          <tr
              v-for="med in filteredMedicaments"
              :key="med.id"
              class="hover:bg-gray-50 transition"
          >
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex items-center">
                <div class="w-10 h-10 bg-gradient-to-r from-teal-400 to-cyan-400 rounded-full flex items-center justify-center mr-3">
                  <i class="fas fa-capsules text-white"></i>
                </div>
                <span class="font-semibold text-gray-900">{{ med.medicament_name }}</span>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex flex-wrap gap-2 max-w-xs">
                <span
                    v-for="contra in med.med_contraindications"
                    :key="contra"
                    class="px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-semibold"
                >
                  <i class="fas fa-pills mr-1"></i>{{ contra }}
                </span>
                <span v-if="!med.med_contraindications?.length" class="text-gray-400 text-sm italic">
                  None
                </span>
              </div>
            </td>
            <td class="px-6 py-4">
              <div class="flex flex-wrap gap-2 max-w-xs">
                <span
                    v-for="contra in med.other_contraindications"
                    :key="contra"
                    class="px-2 py-1 bg-yellow-100 text-yellow-700 rounded-full text-xs font-semibold"
                >
                  <i class="fas fa-exclamation-triangle mr-1"></i>{{ contra }}
                </span>
                <span v-if="!med.other_contraindications?.length" class="text-gray-400 text-sm italic">
                  None
                </span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <div class="flex gap-2">
                <button
                    @click="confirmDelete(med)"
                    class="bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg font-semibold transition"
                    title="Delete"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="filteredMedicaments.length === 0">
            <td colspan="4" class="px-6 py-12 text-center text-gray-500">
              <i class="fas fa-prescription-bottle text-4xl mb-4 block text-gray-300"></i>
              <p class="text-lg">No medicaments found</p>
            </td>
          </tr>
          </tbody>
        </table>
      </div>

      <!-- Stats Cards -->
      <div class="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="bg-gradient-to-r from-teal-500 to-cyan-500 rounded-xl p-4 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-teal-100 text-sm">Total Medicaments</p>
              <p class="text-2xl font-bold">{{ medicaments.length }}</p>
            </div>
            <i class="fas fa-pills text-3xl text-teal-200"></i>
          </div>
        </div>
        <div class="bg-gradient-to-r from-red-500 to-pink-500 rounded-xl p-4 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-red-100 text-sm">Med Contraindications</p>
              <p class="text-2xl font-bold">{{ totalMedContraindications }}</p>
            </div>
            <i class="fas fa-pills text-3xl text-red-200"></i>
          </div>
        </div>
        <div class="bg-gradient-to-r from-yellow-500 to-orange-500 rounded-xl p-4 text-white">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-yellow-100 text-sm">Other Contraindications</p>
              <p class="text-2xl font-bold">{{ totalOtherContraindications }}</p>
            </div>
            <i class="fas fa-exclamation-triangle text-3xl text-yellow-200"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div
        v-if="showModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center z-10">
          <h3 class="text-2xl font-bold text-gray-800">
            <i class="fas fa-pills text-teal-500 mr-2"></i>
            Add Medicament
          </h3>
          <button @click="closeModal" class="text-gray-400 hover:text-gray-600 transition">
            <i class="fas fa-times text-2xl"></i>
          </button>
        </div>

        <form @submit.prevent="saveMedicament" class="p-6 space-y-6">
          <!-- Medicament Name -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Medicament Name <span class="text-red-500">*</span>
            </label>
            <input
                v-model="medicamentForm.name"
                type="text"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Enter medicament name"
                required
            />
          </div>

          <!-- Medicament Contraindications -->
          <div class="border-2 border-red-200 rounded-xl p-4 bg-red-50">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              <i class="fas fa-pills text-red-500 mr-1"></i>
              Medicament Contraindications (Drug Interactions)
            </label>

            <div class="flex gap-2 mb-3">
              <select
                  v-model="selectedMedContraId"
                  class="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-red-500 bg-white"
              >
                <option value="">Select medicament...</option>
                <option
                    v-for="med in availableMedicamentsForContra"
                    :key="med.id"
                    :value="med.id"
                >
                  {{ med.name }}
                </option>
              </select>
              <button
                  type="button"
                  @click="addMedContra"
                  :disabled="!selectedMedContraId"
                  class="px-4 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition disabled:opacity-50"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>

            <div class="min-h-[60px]">
              <div v-if="medicamentForm.med_contraindications.length > 0" class="flex flex-wrap gap-2">
                <span
                    v-for="(contra, index) in medicamentForm.med_contraindications"
                    :key="contra.id"
                    class="px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold flex items-center gap-2"
                >
                  {{ contra.name }}
                  <button
                      type="button"
                      @click="medicamentForm.med_contraindications.splice(index, 1)"
                      class="text-red-500 hover:text-red-700"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </span>
              </div>
              <div v-else class="text-center text-gray-400 py-2">
                <p class="text-sm">No medicament contraindications added</p>
              </div>
            </div>
          </div>

          <!-- Other Contraindications -->
          <div class="border-2 border-yellow-200 rounded-xl p-4 bg-yellow-50">
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              <i class="fas fa-exclamation-triangle text-yellow-500 mr-1"></i>
              Other Contraindications (Allergies, Conditions, etc.)
            </label>

            <div class="flex gap-2 mb-3">
              <input
                  v-model="newOtherContra"
                  type="text"
                  class="flex-1 border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-yellow-500 bg-white"
                  placeholder="Type contraindication (e.g., Pregnancy, Allergy to penicillin)..."
                  @keyup.enter.prevent="addOtherContra"
              />
              <button
                  type="button"
                  @click="addOtherContra"
                  :disabled="!newOtherContra?.trim()"
                  class="px-4 py-3 bg-yellow-600 text-white rounded-lg font-semibold hover:bg-yellow-700 transition disabled:opacity-50"
              >
                <i class="fas fa-plus"></i>
              </button>
            </div>

            <div class="min-h-[60px]">
              <div v-if="medicamentForm.other_contraindications.length > 0" class="flex flex-wrap gap-2">
                <span
                    v-for="(contra, index) in medicamentForm.other_contraindications"
                    :key="index"
                    class="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm font-semibold flex items-center gap-2"
                >
                  {{ contra }}
                  <button
                      type="button"
                      @click="medicamentForm.other_contraindications.splice(index, 1)"
                      class="text-yellow-500 hover:text-yellow-700"
                  >
                    <i class="fas fa-times"></i>
                  </button>
                </span>
              </div>
              <div v-else class="text-center text-gray-400 py-2">
                <p class="text-sm">No other contraindications added</p>
              </div>
            </div>
          </div>

          <!-- Info Note -->
          <div class="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div class="flex items-start gap-3">
              <i class="fas fa-info-circle text-blue-500 mt-0.5"></i>
              <div class="text-sm text-blue-700">
                <p class="font-semibold mb-1">Note:</p>
                <p>Contraindications can only be added during medicament creation. To modify contraindications, you need to delete the medicament and create it again.</p>
              </div>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end gap-4 pt-4 border-t">
            <button
                type="button"
                @click="closeModal"
                class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
                type="submit"
                :disabled="isSaving || !medicamentForm.name.trim()"
                class="px-6 py-3 bg-teal-600 text-white rounded-lg font-semibold hover:bg-teal-700 transition flex items-center gap-2 disabled:opacity-50"
            >
              <i :class="isSaving ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
              {{ isSaving ? 'Saving...' : 'Add Medicament' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div
        v-if="showDeleteModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeDeleteModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
        <div class="text-center">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="fas fa-exclamation-triangle text-red-600 text-3xl"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">Delete Medicament</h3>
          <p class="text-gray-600 mb-2">Are you sure you want to delete</p>
          <p class="font-bold text-lg text-gray-800 mb-4">"{{ medicamentToDelete?.medicament_name }}"?</p>
          <p class="text-sm text-gray-500 mb-4">
            This will also remove all associated contraindications and interactions.
          </p>
          <div class="flex justify-center gap-4">
            <button
                @click="closeDeleteModal"
                class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
                @click="deleteMedicament"
                :disabled="isDeleting"
                class="px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition flex items-center gap-2 disabled:opacity-50"
            >
              <i :class="isDeleting ? 'fas fa-spinner fa-spin' : 'fas fa-trash'"></i>
              {{ isDeleting ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useDoctorData } from '../../composables/useDoctorData'

export default {
  name: 'DoctorMedicaments',
  setup() {
    const {
      getMedicamentContraindications,
      getAllMedicaments,
      addMedicamentWithContraindications,
      deleteMedicamentById,
    } = useDoctorData()

    const medicaments = ref([])
    const allMedicamentsList = ref([])
    const searchQuery = ref('')
    const showModal = ref(false)
    const showDeleteModal = ref(false)
    const isLoading = ref(false)
    const isSaving = ref(false)
    const isDeleting = ref(false)
    const medicamentToDelete = ref(null)

    const selectedMedContraId = ref('')
    const newOtherContra = ref('')

    const medicamentForm = ref({
      name: '',
      med_contraindications: [], // [{id, name}]
      other_contraindications: [], // [string]
    })

    const filteredMedicaments = computed(() => {
      if (!searchQuery.value) return medicaments.value
      const query = searchQuery.value.toLowerCase()
      return medicaments.value.filter(m => m.medicament_name.toLowerCase().includes(query))
    })

    const availableMedicamentsForContra = computed(() => {
      const selectedIds = medicamentForm.value.med_contraindications.map(c => c.id)
      return allMedicamentsList.value.filter(med => !selectedIds.includes(med.id))
    })

    const totalMedContraindications = computed(() => {
      return medicaments.value.reduce((sum, m) => sum + (m.med_contraindications?.length || 0), 0)
    })

    const totalOtherContraindications = computed(() => {
      return medicaments.value.reduce((sum, m) => sum + (m.other_contraindications?.length || 0), 0)
    })

    const loadMedicaments = async () => {
      isLoading.value = true
      try {
        // Загружаем список всех лекарств для выпадающего списка
        allMedicamentsList.value = await getAllMedicaments()

        // Загружаем противопоказания
        const data = await getMedicamentContraindications()

        // Получаем уникальные имена лекарств
        const allMedicamentNames = new Set()
        const medicamentIdMap = {}

        data.forEach(item => {
          allMedicamentNames.add(item.medicament_name)
          medicamentIdMap[item.medicament_name] = item.medicament_id
        })

        // Группируем по лекарству
        const grouped = {}
        allMedicamentNames.forEach(name => {
          grouped[name] = {
            id: medicamentIdMap[name],
            medicament_name: name,
            med_contraindications: [],
            other_contraindications: [],
          }
        })

        // Распределяем противопоказания
        data.forEach(item => {
          if (!item.contradiction) return

          const isMedicament = allMedicamentNames.has(item.contradiction)

          if (isMedicament) {
            if (!grouped[item.medicament_name].med_contraindications.includes(item.contradiction)) {
              grouped[item.medicament_name].med_contraindications.push(item.contradiction)
            }
          } else {
            if (!grouped[item.medicament_name].other_contraindications.includes(item.contradiction)) {
              grouped[item.medicament_name].other_contraindications.push(item.contradiction)
            }
          }
        })

        medicaments.value = Object.values(grouped)

      } catch (error) {
        console.error('Error loading medicaments:', error)
      } finally {
        isLoading.value = false
      }
    }

    const openAddModal = () => {
      medicamentForm.value = {
        name: '',
        med_contraindications: [],
        other_contraindications: [],
      }
      selectedMedContraId.value = ''
      newOtherContra.value = ''
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
      medicamentForm.value = {
        name: '',
        med_contraindications: [],
        other_contraindications: [],
      }
      selectedMedContraId.value = ''
      newOtherContra.value = ''
    }

    const addMedContra = () => {
      if (!selectedMedContraId.value) return

      const selectedMed = allMedicamentsList.value.find(m => m.id === selectedMedContraId.value)
      if (selectedMed && !medicamentForm.value.med_contraindications.find(c => c.id === selectedMed.id)) {
        medicamentForm.value.med_contraindications.push({
          id: selectedMed.id,
          name: selectedMed.name
        })
      }
      selectedMedContraId.value = ''
    }

    const addOtherContra = () => {
      const contra = newOtherContra.value.trim()
      if (contra && !medicamentForm.value.other_contraindications.includes(contra)) {
        medicamentForm.value.other_contraindications.push(contra)
        newOtherContra.value = ''
      }
    }

    const saveMedicament = async () => {
      if (!medicamentForm.value.name.trim()) return

      isSaving.value = true

      try {
        const medContraindicationIds = medicamentForm.value.med_contraindications.map(c => c.id)

        await addMedicamentWithContraindications(
            medicamentForm.value.name,
            medContraindicationIds,
            medicamentForm.value.other_contraindications
        )

        await loadMedicaments()
        closeModal()
      } catch (error) {
        console.error('Error saving medicament:', error)
        alert('Error saving medicament: ' + (error.response?.data?.detail || error.message))
      } finally {
        isSaving.value = false
      }
    }

    const confirmDelete = (med) => {
      medicamentToDelete.value = med
      showDeleteModal.value = true
    }

    const closeDeleteModal = () => {
      showDeleteModal.value = false
      medicamentToDelete.value = null
    }

    const deleteMedicament = async () => {
      if (!medicamentToDelete.value) return

      isDeleting.value = true

      try {
        await deleteMedicamentById(medicamentToDelete.value.id)
        await loadMedicaments()
        closeDeleteModal()
      } catch (error) {
        console.error('Error deleting medicament:', error)
        alert('Error deleting medicament: ' + (error.response?.data?.detail?.message || error.response?.data?.detail || error.message))
      } finally {
        isDeleting.value = false
      }
    }

    onMounted(async () => {
      await loadMedicaments()
    })

    return {
      medicaments,
      searchQuery,
      filteredMedicaments,
      availableMedicamentsForContra,
      totalMedContraindications,
      totalOtherContraindications,
      showModal,
      showDeleteModal,
      isLoading,
      isSaving,
      isDeleting,
      medicamentForm,
      medicamentToDelete,
      selectedMedContraId,
      newOtherContra,
      openAddModal,
      closeModal,
      addMedContra,
      addOtherContra,
      saveMedicament,
      confirmDelete,
      closeDeleteModal,
      deleteMedicament,
    }
  },
}
</script>