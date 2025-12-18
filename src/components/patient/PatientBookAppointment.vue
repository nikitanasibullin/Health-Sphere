<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-8 max-w-3xl mx-auto">
      <h2 class="text-3xl font-bold text-gray-800 mb-6 text-center">
        <i class="fas fa-calendar-plus text-blue-500 mr-2"></i>Book an Appointment
      </h2>

      <form @submit.prevent="handleBookAppointment">
        <!-- Select Doctor -->
        <div class="mb-6">
          <label class="block text-gray-700 font-semibold mb-3">Select Doctor</label>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              v-for="doctor in doctors"
              :key="doctor.id"
              type="button"
              @click="selectDoctor(doctor.id)"
              :class="[
                'p-4 border-2 rounded-xl transition text-left',
                form.doctorId === doctor.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-300 hover:border-blue-300'
              ]"
            >
              <div class="flex items-center">
                <div class="w-12 h-12 bg-gradient-to-r from-green-400 to-teal-400 rounded-full flex items-center justify-center mr-3">
                  <i class="fas fa-user-md text-white text-xl"></i>
                </div>
                <div>
                  <h3 class="font-bold text-gray-800">{{ doctor.name }}</h3>
                  <p class="text-sm text-gray-600">{{ doctor.specialization }}</p>
                </div>
              </div>
            </button>
          </div>
          <p v-if="errors.doctorId" class="text-red-500 text-sm mt-2">
            <i class="fas fa-exclamation-circle mr-1"></i>{{ errors.doctorId }}
          </p>
        </div>

        <!-- Date and Time -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              <i class="fas fa-calendar mr-2 text-blue-500"></i>Date
            </label>


            <!-- No doctor selected -->
            <div v-if="!form.doctorId" class="text-gray-500 text-sm py-3">
              Please select a doctor first
            </div>

            <!-- No available dates -->
            <div v-if="availableDates.length === 0" class="text-yellow-600 text-sm py-3">
              <i class="fas fa-exclamation-triangle mr-1"></i>
              No available dates for this doctor
            </div>

            <!-- Date select -->
            <select
              v-else
              v-model="form.date"
              required
              @change="onDateChange"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select date...</option>
              <option v-for="date in availableDates" :key="date" :value="date">
                {{ formatDate(date) }} ({{ getSlotsCountForDate(date) }} slots)
              </option>
            </select>
            <p v-if="errors.date" class="text-red-500 text-sm mt-2">
              <i class="fas fa-exclamation-circle mr-1"></i>{{ errors.date }}
            </p>
          </div>

          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              <i class="fas fa-clock mr-2 text-blue-500"></i>Time
            </label>

            <!-- No date selected -->
            <div v-if="!form.date" class="text-gray-500 text-sm py-3">
              Please select a date first
            </div>

            <!-- No available slots -->
            <div v-else-if="availableTimeSlots.length === 0" class="text-yellow-600 text-sm py-3">
              <i class="fas fa-exclamation-triangle mr-1"></i>
              No available time slots
            </div>

            <!-- Time select -->
            <select
              v-else
              v-model="selectedSlot"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option :value="null">Select time...</option>
              <option v-for="slot in availableTimeSlots" :key="slot.id" :value="slot">
                {{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }} (Office: {{ slot.office_number }})
              </option>
            </select>
            <p v-if="errors.time" class="text-red-500 text-sm mt-2">
              <i class="fas fa-exclamation-circle mr-1"></i>{{ errors.time }}
            </p>
          </div>
        </div>



        <!-- Selected Appointment Summary -->
        <div v-if="selectedSlot" class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 class="font-semibold text-gray-800 mb-2">
            <i class="fas fa-clipboard-check mr-2 text-blue-500"></i>Appointment Summary
          </h4>
          <div class="grid grid-cols-2 gap-2 text-sm">
            <div><span class="text-gray-600">Date:</span> {{ formatDate(form.date) }}</div>
            <div><span class="text-gray-600">Time:</span> {{ formatTime(selectedSlot.start_time) }}</div>
            <div><span class="text-gray-600">Office:</span> {{ selectedSlot.office_number }}</div>
            <div><span class="text-gray-600">Doctor:</span> {{ getSelectedDoctorName() }}</div>
          </div>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="isSubmitting || !selectedSlot"
          class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-4 rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-semibold text-lg shadow-lg disabled:opacity-50"
        >
          <i v-if="isSubmitting" class="fas fa-spinner fa-spin mr-2"></i>
          <i v-else class="fas fa-calendar-plus mr-2"></i>
          {{ isSubmitting ? 'Booking...' : 'Book Appointment' }}
        </button>
      </form>

      <!-- Success Message -->
      <div
        v-if="successMessage"
        class="mt-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg animate-fadeIn"
      >
        <i class="fas fa-check-circle mr-2"></i>{{ successMessage }}
      </div>

      <!-- Error Message -->
      <div
        v-if="errorMessage"
        class="mt-6 p-4 bg-red-100 border border-red-400 text-red-700 rounded-lg animate-fadeIn"
      >
        <i class="fas fa-exclamation-circle mr-2"></i>{{ errorMessage }}
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { usePatientData } from '../../composables/usePatientData'

export default {
  name: 'PatientBookAppointment',
  props: {
    patientId: {
      type: Number,
      required: false
    }
  },
  emits: ['appointment-booked'],

  setup(props, { emit }) {
    const {
      doctors,
      addAppointment,
      initializeData,
      fetchDoctorSchedule
    } = usePatientData()

    const form = ref({
      doctorId: null,
      date: ''
    })

    // Schedule data
    const doctorSchedules = ref([])
    const selectedSlot = ref(null)

    const errors = ref({})
    const isSubmitting = ref(false)
    const successMessage = ref('')
    const errorMessage = ref('')

    // only future dates with is_available=true
    const availableDates = computed(() => {
      const today = new Date()
      today.setHours(0, 0, 0, 0)

      const dates = [...new Set(
        doctorSchedules.value
          .filter(s => {
            const scheduleDate = new Date(s.date)
            scheduleDate.setHours(0, 0, 0, 0)
            return s.is_available && scheduleDate >= today
          })
          .map(s => s.date)
      )]

      return dates.sort((a, b) => new Date(a) - new Date(b))
    })

    // Get available time slots for selected date (is_available=true)
    const availableTimeSlots = computed(() => {
      if (!form.value.date) return []

      return doctorSchedules.value
        .filter(s => s.date === form.value.date && s.is_available)
        .sort((a, b) => a.start_time.localeCompare(b.start_time))
    })

    // Get slots count for a date
    const getSlotsCountForDate = (date) => {
      return doctorSchedules.value.filter(s => s.date === date && s.is_available).length
    }

    // Select doctor and fetch schedules
    const selectDoctor = async (doctorId) => {
      form.value.doctorId = doctorId
      form.value.date = ''
      selectedSlot.value = null
      errorMessage.value = ''
      try {
        const schedules = await fetchDoctorSchedule(doctorId)
        doctorSchedules.value = schedules
      } catch (error) {
        console.error('Failed to fetch schedules:', error)
        doctorSchedules.value = []
      }
    }

    // Reset time when date changes
    const onDateChange = () => {
      selectedSlot.value = null
    }

    // Format date for display
    const formatDate = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }

    // Format time from ISO string (e.g., "19:58:31.534Z" or "09:00:00")
    const formatTime = (timeString) => {
      if (!timeString) return ''

      if (timeString.includes('T') || timeString.includes('Z')) {
        const date = new Date(timeString)
        return date.toLocaleTimeString('en-US', {
          hour: '2-digit',
          minute: '2-digit',
          hour12: false
        })
      }

      // Format: HH:MM
      const parts = timeString.split(':')
      return `${parts[0]}:${parts[1]}`
    }

    // Get selected doctor name
    const getSelectedDoctorName = () => {
      const doctor = doctors.value?.find(d => d.id === form.value.doctorId)
      return doctor ? doctor.name : ''
    }

    const validate = () => {
      errors.value = {}

      if (!form.value.doctorId) {
        errors.value.doctorId = 'Please select a doctor'
      }
      if (!form.value.date) {
        errors.value.date = 'Please select a date'
      }
      if (!selectedSlot.value) {
        errors.value.time = 'Please select a time'
      }

      return Object.keys(errors.value).length === 0
    }

    const handleBookAppointment = async () => {
      if (!validate()) return

      isSubmitting.value = true
      successMessage.value = ''
      errorMessage.value = ''

      try {
        // Book using the schedule ID
        await addAppointment(selectedSlot.value.id)

        successMessage.value = 'Appointment booked successfully! You will receive a confirmation shortly.'

        // Reset form
        form.value = {
          doctorId: null,
          date: '',
          reason: ''
        }
        selectedSlot.value = null
        doctorSchedules.value = []

        emit('appointment-booked')
      } catch (error) {
        errorMessage.value = error.message || 'Failed to book appointment. Please try again.'
      } finally {
        isSubmitting.value = false
      }
    }

    onMounted(async () => {
      await initializeData()
    })

    return {
      doctors,
      form,
      errors,
      isSubmitting,
      successMessage,
      errorMessage,
      availableDates,
      availableTimeSlots,
      selectedSlot,
      selectDoctor,
      onDateChange,
      formatDate,
      formatTime,
      getSlotsCountForDate,
      getSelectedDoctorName,
      handleBookAppointment
    }
  }
}
</script>
