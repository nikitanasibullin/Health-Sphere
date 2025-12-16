<template>
  <div class="animate-fadeIn">
    <h2 class="text-3xl font-bold text-gray-800 mb-6">Doctor Dashboard</h2>

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
            <i class="fas fa-calendar-check text-3xl"></i>
          </div>
        </div>
      </div>

      <!-- Today's Appointments -->
      <div class="bg-gradient-to-br from-green-500 to-green-700 p-6 rounded-2xl shadow-lg text-white card-hover">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-green-100 text-sm font-semibold">Today's Appointments</p>
            <p class="text-4xl font-bold mt-2">{{ todaysAppointments.length }}</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-clock text-3xl"></i>
          </div>
        </div>
      </div>

      <!-- Total Patients -->
      <div class="bg-gradient-to-br from-purple-500 to-purple-700 p-6 rounded-2xl shadow-lg text-white card-hover">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-purple-100 text-sm font-semibold">Total Patients</p>
            <p class="text-4xl font-bold mt-2">{{ myPatients.length }}</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-users text-3xl"></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Today's Schedule -->
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h3 class="text-2xl font-bold text-gray-800 mb-4">
        <i class="fas fa-calendar-day text-blue-500 mr-2"></i>Today's Schedule
      </h3>

      <div v-if="todaysAppointments.length === 0" class="text-center py-8 text-gray-500">
        <i class="fas fa-calendar-check text-4xl mb-4"></i>
        <p>No appointments scheduled for today</p>
      </div>

      <div v-else class="space-y-3">
        <div
          v-for="apt in todaysAppointments"
          :key="apt.id"
          class="flex items-center justify-between p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg hover:shadow-md transition"
        >
          <div class="flex items-center">
            <div class="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center mr-4">
              <i class="fas fa-user text-white text-xl"></i>
            </div>
            <div>
              <h4 class="font-bold text-gray-800">{{ getPatientName(apt.patient_id) }}</h4>
              <p class="text-sm text-gray-600">
                <i class="fas fa-clock mr-1"></i>{{ apt.schedule?.time_slot }} - {{ apt.reason || 'Consultation' }}
              </p>
            </div>
          </div>
          <span :class="getStatusClass(apt.status)">{{ apt.status }}</span>
        </div>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
      <!-- Upcoming Appointments -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">
          <i class="fas fa-calendar-alt text-purple-500 mr-2"></i>Upcoming Appointments
        </h3>
        <div class="space-y-3">
          <div
            v-for="apt in upcomingAppointments.slice(0, 5)"
            :key="apt.id"
            class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
          >
            <div>
              <p class="font-semibold text-gray-800">{{ getPatientName(apt.patient_id) }}</p>
              <p class="text-sm text-gray-500">{{ apt.schedule?.date }} at {{ apt.schedule?.time_slot }}</p>
            </div>
            <span :class="getStatusClass(apt.status)">{{ apt.status }}</span>
          </div>
          <div v-if="upcomingAppointments.length === 0" class="text-center py-4 text-gray-500">
            No upcoming appointments
          </div>
        </div>
      </div>

      <!-- Recent Prescriptions -->
      <div class="bg-white rounded-2xl shadow-lg p-6">
        <h3 class="text-xl font-bold text-gray-800 mb-4">
          <i class="fas fa-prescription text-green-500 mr-2"></i>Recent Prescriptions
        </h3>
        <div class="space-y-3">
          <div
            v-for="prescription in recentPrescriptions.slice(0, 5)"
            :key="prescription.id"
            class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
          >
            <div>
              <p class="font-semibold text-gray-800">{{ getPatientName(prescription.patient_id) }}</p>
              <p class="text-sm text-gray-500">{{ prescription.medication }}</p>
            </div>
            <span class="text-xs text-gray-400">{{ prescription.date }}</span>
          </div>
          <div v-if="recentPrescriptions.length === 0" class="text-center py-4 text-gray-500">
            No prescriptions yet
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData'

export default {
  name: 'DoctorDashboard',
  props: {
    doctorId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const {
      getPatientName,
      getDoctorAppointments,
      getDoctorTodayAppointments,
      getDoctorPatients,
      getDoctorPrescriptions
    } = useHospitalData()

    const myAppointments = ref([])
    const todaysAppointments = ref([])
    const myPatients = getDoctorPatients(props.doctorId)
    const myPrescriptions = getDoctorPrescriptions(props.doctorId)

    onMounted(async () => {
      myAppointments.value = await getDoctorAppointments() || []
      todaysAppointments.value = await getDoctorTodayAppointments() || []
    })

    const upcomingAppointments = computed(() => {
      const today = new Date().toISOString().split('T')[0]
      return myAppointments.value
        .filter(a => (a.schedule?.date >= today) && a.status === 'scheduled')
        .sort((a, b) => new Date(a.schedule?.date + ' ' + a.schedule?.time_slot) - new Date(b.schedule?.date + ' ' + b.schedule?.time_slot))
    })

    const recentPrescriptions = computed(() => {
      return [...myPrescriptions.value].sort((a, b) => new Date(b.date) - new Date(a.date))
    })

    const getStatusClass = (status) => {
      const classes = {
        'scheduled': 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold',
        'Scheduled': 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold',
        'completed': 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold',
        'Completed': 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold',
        'cancelled': 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold',
        'Cancelled': 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold'
      }
      return classes[status] || classes['scheduled']
    }

    return {
      myAppointments,
      todaysAppointments,
      myPatients,
      upcomingAppointments,
      recentPrescriptions,
      getPatientName,
      getStatusClass
    }
  }
}
</script>
