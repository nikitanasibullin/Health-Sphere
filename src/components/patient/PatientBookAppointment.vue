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
              @click="form.doctorId = doctor.id"
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
            <input
              v-model="form.date"
              type="date"
              :min="minDate"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
            <p v-if="errors.date" class="text-red-500 text-sm mt-2">
              <i class="fas fa-exclamation-circle mr-1"></i>{{ errors.date }}
            </p>
          </div>

          <div>
            <label class="block text-gray-700 font-semibold mb-2">
              <i class="fas fa-clock mr-2 text-blue-500"></i>Time
            </label>
            <select
              v-model="form.time"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select time...</option>
              <option v-for="slot in timeSlots" :key="slot" :value="slot">{{ slot }}</option>
            </select>
            <p v-if="errors.time" class="text-red-500 text-sm mt-2">
              <i class="fas fa-exclamation-circle mr-1"></i>{{ errors.time }}
            </p>
          </div>
        </div>

        <!-- Reason -->
        <div class="mb-6">
          <label class="block text-gray-700 font-semibold mb-2">
            <i class="fas fa-notes-medical mr-2 text-blue-500"></i>Reason for Visit
          </label>
          <textarea
            v-model="form.reason"
            rows="4"
            required
            placeholder="Please describe the reason for your visit..."
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          ></textarea>
          <p v-if="errors.reason" class="text-red-500 text-sm mt-2">
            <i class="fas fa-exclamation-circle mr-1"></i>{{ errors.reason }}
          </p>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="isSubmitting"
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
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData'



export default {
  name: 'PatientBookAppointment',
  props: {
    patientId: {
      type: Number,
      required: true
    }
  },
  emits: ['appointment-booked'],

  setup(props, { emit }) {
    const { doctors, addAppointment, addActivity, getDoctorName } = useHospitalData()

    const form = ref({
      doctorId: null,
      date: '',
      time: '',
      reason: ''
    })

    const errors = ref({})
    const isSubmitting = ref(false)
    const successMessage = ref('')

    // Minimum date is today
    const minDate = computed(() => {
      return new Date().toISOString().split('T')[0]
    })

    // Available time slots
    const timeSlots = [
      '09:00', '09:30', '10:00', '10:30', '11:00', '11:30',
      '14:00', '14:30', '15:00', '15:30', '16:00', '16:30'
    ]

    const validate = () => {
      errors.value = {}

      if (!form.value.doctorId) {
        errors.value.doctorId = 'Please select a doctor'
      }
      if (!form.value.date) {
        errors.value.date = 'Please select a date'
      }
      if (!form.value.time) {
        errors.value.time = 'Please select a time'
      }
      if (!form.value.reason || form.value.reason.trim().length < 10) {
        errors.value.reason = 'Please provide a reason (at least 10 characters)'
      }

      return Object.keys(errors.value).length === 0
    }

    const handleBookAppointment = async () => {
      if (!validate()) return

      isSubmitting.value = true
      successMessage.value = ''

      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000))

      addAppointment({
        patientId: props.patientId,
        doctorId: form.value.doctorId,
        date: form.value.date,
        time: form.value.time,
        reason: form.value.reason
      })

      addActivity(
        `Appointment booked with ${getDoctorName(form.value.doctorId)}`,
        'fas fa-calendar-plus',
        'bg-blue-500'
      )

      successMessage.value = 'Appointment booked successfully! You will receive a confirmation shortly.'

      // Reset form
      form.value = {
        doctorId: null,
        date: '',
        time: '',
        reason: ''
      }

      isSubmitting.value = false
      emit('appointment-booked')
    }
    onMounted(async () => {
      const {initializeData} = useHospitalData()
      await initializeData()
    })

    return {
      doctors,
      form,
      errors,
      isSubmitting,
      successMessage,
      minDate,
      timeSlots,
      handleBookAppointment
    }
  }
}
</script>
