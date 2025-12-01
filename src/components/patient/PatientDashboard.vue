<template>
  <div class="animate-fadeIn">
    <h2 class="text-3xl font-bold text-gray-800 mb-6">Patient Dashboard</h2>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <!-- My Appointments -->
      <div class="bg-gradient-to-br from-blue-500 to-blue-700 p-6 rounded-2xl shadow-lg text-white card-hover">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-100 text-sm font-semibold">My Appointments</p>
            <p class="text-4xl font-bold mt-2">{{ myAppointments.length }}</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-calendar-alt text-3xl"></i>
          </div>
        </div>
      </div>

      <!-- Upcoming -->
      <div class="bg-gradient-to-br from-green-500 to-green-700 p-6 rounded-2xl shadow-lg text-white card-hover">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-green-100 text-sm font-semibold">Upcoming</p>
            <p class="text-4xl font-bold mt-2">{{ upcomingAppointments.length }}</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-clock text-3xl"></i>
          </div>
        </div>
      </div>

      <!-- Completed -->
      <div class="bg-gradient-to-br from-purple-500 to-purple-700 p-6 rounded-2xl shadow-lg text-white card-hover">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-purple-100 text-sm font-semibold">Completed</p>
            <p class="text-4xl font-bold mt-2">{{ completedAppointments.length }}</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-check-circle text-3xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Upcoming Appointments -->
    <div class="bg-white rounded-2xl shadow-lg p-6 mb-6">
      <h3 class="text-2xl font-bold text-gray-800 mb-4">
        <i class="fas fa-calendar-check text-blue-500 mr-2"></i>Upcoming Appointments
      </h3>

      <div v-if="upcomingAppointments.length === 0" class="text-center py-8 text-gray-500">
        <i class="fas fa-calendar-times text-4xl mb-4"></i>
        <p>No upcoming appointments</p>
        <button
          @click="$emit('navigate-to', 'book')"
          class="mt-4 bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
        >
          Book an Appointment
        </button>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="apt in upcomingAppointments.slice(0, 5)"
          :key="apt.id"
          class="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg hover:shadow-md transition"
        >
          <div class="flex items-center">
            <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mr-4">
              <i class="fas fa-user-md text-white text-xl"></i>
            </div>
            <div>
              <h4 class="font-bold text-gray-800">{{ getDoctorName(apt.doctorId) }}</h4>
              <p class="text-sm text-gray-600">
                <i class="fas fa-calendar mr-1"></i>{{ formatDate(apt.date) }} at {{ apt.time }}
              </p>
              <p class="text-sm text-gray-500">{{ apt.reason }}</p>
            </div>
          </div>
          <button
            @click="handleCancelAppointment(apt.id)"
            class="text-red-600 hover:text-red-800 transition px-3 py-1 rounded hover:bg-red-50"
          >
            <i class="fas fa-times-circle mr-1"></i>Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Quick Actions & Recent Prescriptions -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <!-- Quick Actions -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">
          <i class="fas fa-bolt text-yellow-500 mr-2"></i>Quick Actions
        </h3>
        <div class="grid grid-cols-2 gap-4">
          <button
            @click="$emit('navigate-to', 'book')"
            class="p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl hover:shadow-md transition text-center"
          >
            <i class="fas fa-calendar-plus text-blue-600 text-2xl mb-2"></i>
            <p class="font-semibold text-gray-700">Book Appointment</p>
          </button>
          <button
            @click="$emit('navigate-to', 'history')"
            class="p-4 bg-gradient-to-r from-green-50 to-teal-50 rounded-xl hover:shadow-md transition text-center"
          >
            <i class="fas fa-file-medical-alt text-green-600 text-2xl mb-2"></i>
            <p class="font-semibold text-gray-700">Medical History</p>
          </button>
          <button
            @click="$emit('navigate-to', 'prescriptions')"
            class="p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl hover:shadow-md transition text-center"
          >
            <i class="fas fa-prescription-bottle text-purple-600 text-2xl mb-2"></i>
            <p class="font-semibold text-gray-700">Prescriptions</p>
          </button>
          <button
            @click="$emit('navigate-to', 'appointments')"
            class="p-4 bg-gradient-to-r from-orange-50 to-yellow-50 rounded-xl hover:shadow-md transition text-center"
          >
            <i class="fas fa-calendar-alt text-orange-600 text-2xl mb-2"></i>
            <p class="font-semibold text-gray-700">All Appointments</p>
          </button>
        </div>
      </div>

      <!-- Recent Prescriptions -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">
          <i class="fas fa-prescription text-green-500 mr-2"></i>Active Prescriptions
        </h3>
        <div class="space-y-3">
          <div
            v-for="prescription in myPrescriptions.slice(0, 4)"
            :key="prescription.id"
            class="p-3 bg-gradient-to-r from-green-50 to-teal-50 rounded-lg"
          >
            <div class="flex justify-between items-start">
              <div>
                <p class="font-semibold text-gray-800">{{ prescription.medication }}</p>
                <p class="text-sm text-gray-600">{{ prescription.dosage }}</p>
              </div>
              <span class="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-semibold">
                Active
              </span>
            </div>
          </div>
          <div v-if="myPrescriptions.length === 0" class="text-center py-4 text-gray-500">
            No active prescriptions
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useHospitalData } from '../../composables/useHospitalData'

export default {
  name: 'PatientDashboard',
  props: {
    patientId: {
      type: Number,
      required: true
    }
  },
  emits: ['navigate-to'],
  setup(props) {
    const {
      getDoctorName,
      getPatientAppointments,
      getPatientUpcomingAppointments,
      getPatientCompletedAppointments,
      getPatientPrescriptions,
      cancelAppointment,
      addActivity
    } = useHospitalData()

    const myAppointments = getPatientAppointments(props.patientId)
    const upcomingAppointments = getPatientUpcomingAppointments(props.patientId)
    const completedAppointments = getPatientCompletedAppointments(props.patientId)
    const myPrescriptions = getPatientPrescriptions(props.patientId)

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric'
      })
    }

    const handleCancelAppointment = (appointmentId) => {
      if (confirm('Are you sure you want to cancel this appointment?')) {
        cancelAppointment(appointmentId)
        addActivity('Appointment cancelled', 'fas fa-calendar-times', 'bg-red-500')
      }
    }

    return {
      myAppointments,
      upcomingAppointments,
      completedAppointments,
      myPrescriptions,
      getDoctorName,
      formatDate,
      handleCancelAppointment
    }
  }
}
</script>
