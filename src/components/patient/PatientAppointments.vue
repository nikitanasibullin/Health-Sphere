<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-calendar-alt text-purple-500 mr-2"></i>My Appointments
      </h2>

      <!-- Filter Tabs -->
      <div class="mb-6 flex flex-wrap gap-2">
        <button
          v-for="filter in filters"
          :key="filter.value"
          @click="activeFilter = filter.value"
          :class="[
            'px-4 py-2 rounded-lg font-semibold transition',
            activeFilter === filter.value
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          ]"
        >
          {{ filter.label }}
        </button>
      </div>

      <!-- Appointments List -->
      <div v-if="filteredAppointments.length === 0" class="text-center py-12 text-gray-500">
        <i class="fas fa-calendar-times text-4xl mb-4"></i>
        <p>No {{ activeFilter === 'all' ? '' : activeFilter.toLowerCase() }} appointments found</p>
      </div>

      <div v-else class="space-y-4">
        <div
          v-for="apt in filteredAppointments"
          :key="apt.id"
          class="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition card-hover"
        >
          <div class="flex flex-col md:flex-row justify-between items-start">
            <div class="flex items-center flex-1 mb-4 md:mb-0">
              <div class="w-16 h-16 bg-gradient-to-r from-green-400 to-teal-400 rounded-full flex items-center justify-center mr-4">
                <i class="fas fa-user-md text-white text-2xl"></i>
              </div>
              <div>
                <h3 class="font-bold text-xl text-gray-800">{{ getDoctorName(apt.doctorId) }}</h3>
                <p class="text-gray-600">{{ getDoctorSpecialization(apt.doctorId) }}</p>
                <p class="text-gray-700 mt-2">
                  <i class="fas fa-calendar text-blue-500 mr-2"></i>
                  {{ formatDate(apt.date) }} at {{ apt.time }}
                </p>
                <p class="text-gray-700">
                  <i class="fas fa-notes-medical text-purple-500 mr-2"></i>
                  {{ apt.reason }}
                </p>
              </div>
            </div>

            <div class="text-right">
              <span :class="getStatusClass(apt.status)">{{ apt.status }}</span>
              <button
                v-if="apt.status === 'Scheduled'"
                @click="handleCancelAppointment(apt.id)"
                class="block mt-3 bg-red-100 text-red-600 px-4 py-2 rounded-lg hover:bg-red-200 transition text-sm font-semibold"
              >
                <i class="fas fa-times-circle mr-1"></i>Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { usePatientData } from '../../composables/usePatientData'

export default {
  name: 'PatientAppointments',
  props: {
    patientId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const {
      getDoctorName,
      getDoctorSpecialization,
      getPatientAppointments,
      cancelAppointment,
      addActivity
    } = usePatientData()

    const myAppointments = getPatientAppointments(props.patientId)
    const activeFilter = ref('all')

    const filters = [
      { label: 'All', value: 'all' },
      { label: 'Scheduled', value: 'Scheduled' },
      { label: 'Completed', value: 'Completed' },
      { label: 'Cancelled', value: 'Cancelled' }
    ]

    const filteredAppointments = computed(() => {
      if (!myAppointments.value) {
        return []
      }
      if (activeFilter.value === 'all') {
        return [...myAppointments.value].sort((a, b) => new Date(b.date) - new Date(a.date))
      }
      return myAppointments.value
        .filter(a => a.status === activeFilter.value)
        .sort((a, b) => new Date(b.date) - new Date(a.date))
    })

    const getFilterCount = (filterValue) => {
      if (!myAppointments.value) return 0
      if (filterValue === 'all') return myAppointments.value.length
      return myAppointments.value.filter(a => a.status === filterValue).length
    }

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const getStatusClass = (status) => {
      const classes = {
        'Scheduled': 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold',
        'Completed': 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold',
        'Cancelled': 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold'
      }
      return classes[status] || classes['Scheduled']
    }

    const handleCancelAppointment = (appointmentId) => {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        cancelAppointment(appointmentId)
        addActivity('Appointment cancelled', 'fas fa-calendar-times', 'bg-red-500')
      }
    }

    return {
      activeFilter,
      filters,
      filteredAppointments,
      getFilterCount,
      getDoctorName,
      getDoctorSpecialization,
      formatDate,
      getStatusClass,
      handleCancelAppointment
    }
  }
}
</script>
