<template>
  <div class="animate-fadeIn">
    <!-- Header -->
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-3xl font-bold text-gray-800">
        <i class="fas fa-calendar-alt text-indigo-500 mr-2"></i>Doctor Schedules
      </h2>
      <button
        @click="openAddModal"
        class="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-lg hover:from-indigo-700 hover:to-purple-700 shadow-lg transition"
      >
        <i class="fas fa-plus mr-2"></i>Add Schedule
      </button>
    </div>

    <!-- Empty State -->
    <div v-if="doctorSchedules.length === 0" class="bg-white rounded-2xl shadow-lg p-12 text-center">
      <i class="fas fa-calendar-times text-gray-300 text-6xl mb-4"></i>
      <p class="text-gray-500 text-lg">No doctors found</p>
    </div>

    <!-- Doctor List -->
    <div v-else class="space-y-4">
      <div
        v-for="item in doctorSchedules"
        :key="item.doctor.id"
        class="bg-white rounded-2xl shadow-lg overflow-hidden"
      >
        <!-- Doctor Header (Clickable) -->
        <div
          @click="toggleDoctor(item.doctor.id)"
          class="bg-gradient-to-r from-indigo-500 to-purple-600 p-4 cursor-pointer hover:from-indigo-600 hover:to-purple-700 transition"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-white bg-opacity-20 rounded-full flex items-center justify-center mr-4">
                <i class="fas fa-user-md text-white text-xl"></i>
              </div>
              <div class="text-white">
                <h3 class="font-bold text-lg">{{ item.doctor.name }}</h3>
                <p class="text-indigo-100 text-sm">{{ item.doctor.specialization_name || item.doctor.specialization }}</p>
              </div>
            </div>
            <div class="flex items-center text-white">
              <div class="text-right mr-4">
                <p class="text-sm text-indigo-100">Total</p>
                <p class="font-bold">{{ item.schedules.length }} appointments</p>  <!-- ✅ Changed -->
              </div>
              <i :class="['fas text-xl transition-transform', isExpanded(item.doctor.id) ? 'fa-chevron-up' : 'fa-chevron-down']"></i>
            </div>
          </div>
        </div>

        <!-- Nested Schedule List -->
        <div v-if="isExpanded(item.doctor.id)" class="p-4">
          <!-- No Schedules -->
          <div v-if="item.schedules.length === 0" class="text-center text-gray-500 py-6">
            <i class="fas fa-calendar-times text-2xl mb-2"></i>
            <p>No schedules for this doctor</p>
          </div>

          <!-- Schedule Items -->
          <ul v-else class="space-y-3">
            <li
              v-for="schedule in item.schedules"
              :key="schedule.id"
              class="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition"
            >
              <div class="flex items-center justify-between">
                <div class="flex items-center space-x-6">
                  <!-- Date -->
                  <div class="flex items-center">
                    <i class="fas fa-calendar text-indigo-500 mr-2"></i>
                    <span class="font-semibold text-gray-800">{{ formatDate(schedule.date) }}</span>
                  </div>

                  <!-- Time -->
                  <div class="flex items-center">
                    <i class="fas fa-clock text-green-500 mr-2"></i>
                    <span class="text-gray-700">{{ formatTime(schedule.startTime) }} - {{ formatTime(schedule.endTime) }}</span>
                  </div>

                  <!-- Office -->
                  <div class="flex items-center">
                    <i class="fas fa-door-open text-purple-500 mr-2"></i>
                    <span class="text-gray-700">Office {{ schedule.officeNumber || '-' }}</span>
                  </div>

                  <!-- Status -->
                  <span
                    :class="[
            'px-3 py-1 rounded-full text-xs font-semibold',
            schedule.isActive
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          ]"
                  >
          {{ schedule.isActive ? 'Active' : 'Inactive' }}
        </span>
                </div>

                <!-- Delete Button -->
                <button
                  @click="handleDelete(schedule.id)"
                  class="text-red-600 hover:text-red-800 p-2"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>
            </li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Add Modal -->
    <div
      v-if="showModal"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="closeModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-8 mx-4">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">Add New Schedule</h3>
          <button @click="closeModal" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>

        <form @submit.prevent="handleSubmit">
          <!-- Doctor -->
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">Doctor</label>
            <select
              v-model="form.doctorId"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select doctor...</option>
              <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                {{ doctor.name }}
              </option>
            </select>
          </div>

          <!-- Date -->
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">Date</label>
            <input
              v-model="form.date"
              type="date"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
          </div>

          <!-- Office -->
          <div class="mb-4">
            <label class="block text-gray-700 text-sm font-bold mb-2">Office Number</label>
            <input
              v-model="form.officeNumber"
              type="text"
              required
              placeholder="e.g., 101"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
          </div>

          <!-- Time -->
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Start Time</label>
              <input
                v-model="form.startTime"
                type="time"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">End Time</label>
              <input
                v-model="form.endTime"
                type="time"
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
            </div>
          </div>

          <!-- Slots -->
          <div class="mb-6">
            <label class="block text-gray-700 text-sm font-bold mb-2">Number of Appointments</label>
            <input
              v-model.number="form.appointmentCount"
              type="number"
              min="1"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
          </div>

          <!-- Buttons -->
          <div class="flex gap-4">
            <button
              type="button"
              @click="closeModal"
              class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              class="flex-1 px-4 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
            >
              Add Schedule
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
<script>
import { ref, onMounted } from 'vue'
import { useAdminData } from '../../composables/useAdminData'

export default {
  name: 'AdminSchedule',
  setup() {
    const {
      doctors,
      initializeData,
      fetchAdminDoctorSchedule,
      addScheduleBatch,
      deleteSchedule
    } = useAdminData()

    const doctorSchedules = ref([])
    const expandedDoctors = ref([])
    const showModal = ref(false)
    const form = ref({
      doctorId: '',
      date: new Date().toISOString().split('T')[0],
      startTime: '09:00',
      endTime: '17:00',
      appointmentCount: 16,
      officeNumber: '101'
    })

    const toggleDoctor = (doctorId) => {
      const index = expandedDoctors.value.indexOf(doctorId)
      if (index === -1) {
        expandedDoctors.value.push(doctorId)
      } else {
        expandedDoctors.value.splice(index, 1)
      }
    }

    const isExpanded = (doctorId) => {
      return expandedDoctors.value.includes(doctorId)
    }

    const loadAllSchedules = async () => {
      const result = []
      for (const doctor of doctors.value) {
        const schedules = await fetchAdminDoctorSchedule(doctor.id)
        result.push({
          doctor,
          schedules: schedules.sort((a, b) => new Date(a.date) - new Date(b.date))
        })
      }
      doctorSchedules.value = result
      expandedDoctors.value = doctors.value.map(d => d.id)
    }

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const [year, month, day] = dateString.split('-')
      return `${day}.${month}.${year}`
    }

    const formatTime = (timeString) => {
      if (!timeString) return ''
      return timeString.slice(0, 5)  // "21:48:12.738Z" → "21:48"
    }

    const openAddModal = () => {
      form.value = {
        doctorId: '',
        date: new Date().toISOString().split('T')[0],
        startTime: '09:00',
        endTime: '17:00',
        appointmentCount: 16,
        officeNumber: '101'
      }
      showModal.value = true
    }

    const closeModal = () => {
      showModal.value = false
    }

    const handleSubmit = async () => {
      try {
        const data = {
          doctor_id: parseInt(form.value.doctorId),
          date: form.value.date,
          start_time: form.value.startTime,        // ✅ Send as "09:00"
          end_time: form.value.endTime,            // ✅ Send as "17:00"
          slots_count: parseInt(form.value.appointmentCount),
          office_number: form.value.officeNumber
        }
        console.log(data)
        await addScheduleBatch(data)

        await loadAllSchedules()
        closeModal()
      } catch (error) {
        console.error('Failed to add schedule:', error)
        alert('Failed: ' + error.message)
      }
    }

    const handleDelete = async (id) => {
      if (!confirm('Delete this schedule?')) return
      try {
        await deleteSchedule(id)
        await loadAllSchedules()
      } catch (error) {
        console.error('Failed to delete:', error)
        alert('Failed: ' + error.message)
      }
    }

    onMounted(async () => {
      await initializeData()
      await loadAllSchedules()
    })

    return {
      doctors,
      doctorSchedules,
      showModal,
      form,
      formatTime,
      formatDate,
      toggleDoctor,
      isExpanded,
      openAddModal,
      closeModal,
      handleSubmit,
      handleDelete
    }
  }
}
</script>
