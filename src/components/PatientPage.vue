<template>
  <!-- Loading State -->
  <div v-if="isLoading" class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="text-center">
      <i class="fas fa-spinner fa-spin text-5xl text-blue-500 mb-4"></i>
      <p class="text-gray-600 text-lg">Loading dashboard...</p>
    </div>
  </div>

  <!-- Main Content -->
  <AppLayout
    v-else
    :user="currentUser"
    :notifications="notifications"
    :tabs="patientTabs"
    :active-tab="activeTab"
    @logout="handleLogout"
    @tab-change="activeTab = $event"
    @clear-notifications="notifications = []"
  >
    <component
      :is="currentTabComponent"
      :patient-id="patientId"
      @navigate-to="activeTab = $event"
      @appointment-booked="handleAppointmentBooked"
    />
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from './common/AppLayout.vue'
import PatientDashboard from './patient/PatientDashboard.vue'
import PatientBookAppointment from './patient/PatientBookAppointment.vue'
import PatientAppointments from './patient/PatientAppointments.vue'
//import PatientHistory from './patient/PatientHistory.vue'
//import PatientPrescriptions from './patient/PatientPrescriptions.vue'
import { usePatientData } from '../composables/usePatientData'

export default {
  name: 'PatientPage',
  components: {
    AppLayout,
    PatientDashboard,
    PatientBookAppointment,
    PatientAppointments,
    //PatientHistory,
    //PatientPrescriptions
  },
  setup() {
    const router = useRouter()
    const { getPatientByEmail, logout } = usePatientData()

    const isLoading = ref(true)
    const currentUser = ref({ name: 'Patient', role: 'patient' })
    const patientId = ref(5) // Default patient ID
    const activeTab = ref('dashboard')

    const patientTabs = [
      { id: 'dashboard', name: 'Dashboard', icon: 'fas fa-home' },
      { id: 'book', name: 'Book Appointment', icon: 'fas fa-calendar-plus' },
      { id: 'appointments', name: 'My Appointments', icon: 'fas fa-calendar-alt' },
      //{ id: 'history', name: 'Medical History', icon: 'fas fa-file-medical-alt' },
      //{ id: 'prescriptions', name: 'Prescriptions', icon: 'fas fa-prescription-bottle' }
    ]

    const notifications = ref([
      { id: 1, message: 'Upcoming appointment tomorrow at 09:00', time: '1 hour ago' },
      { id: 2, message: 'Your prescription is ready for pickup', time: '3 hours ago' },
      { id: 3, message: 'Lab results are now available', time: '1 day ago' }
    ])

    const tabComponents = {
      dashboard: 'PatientDashboard',
      book: 'PatientBookAppointment',
      appointments: 'PatientAppointments',
      //history: 'PatientHistory',
      prescriptions: 'PatientPrescriptions'
    }

    const currentTabComponent = computed(() => {
      return tabComponents[activeTab.value] || 'PatientDashboard'
    })

    const loadUser = () => {
      const userJson = localStorage.getItem('currentUser')
      if (userJson) {
        const user = JSON.parse(userJson)
        currentUser.value = user

        // Find patient by email to get patient ID
        const patient = getPatientByEmail(user.email)
        if (patient) {
          patientId.value = patient.id
        }

        isLoading.value = false
      } else {
        router.push('/login')
      }
    }

    const handleLogout = () => {
      logout()
      router.push('/login')
    }

    const handleAppointmentBooked = () => {
      // Add notification
      notifications.value.unshift({
        id: Date.now(),
        message: 'Appointment booked successfully!',
        time: 'Just now'
      })
    }

    onMounted(() => {
      setTimeout(() => {
        loadUser()
      }, 100)
    })

    return {
      isLoading,
      currentUser,
      patientId,
      activeTab,
      patientTabs,
      notifications,
      currentTabComponent,
      handleLogout,
      handleAppointmentBooked
    }
  }
}
</script>
