<template>
  <!-- Loading State -->
  <div v-if="isLoading" class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="text-center">
      <i class="fas fa-spinner fa-spin text-5xl text-green-500 mb-4"></i>
      <p class="text-gray-600 text-lg">Loading dashboard...</p>
    </div>
  </div>

  <!-- Main Content -->
  <AppLayout
    v-else
    :user="currentUser"
    :notifications="notifications"
    :tabs="doctorTabs"
    :active-tab="activeTab"
    @logout="handleLogout"
    @tab-change="activeTab = $event"
    @clear-notifications="notifications = []"
  >
    <component :is="currentTabComponent" :doctor-id="doctorId" />
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from './common/AppLayout.vue'
import DoctorDashboard from './doctor/DoctorDashboard.vue'
import DoctorAppointments from './doctor/DoctorAppointments.vue'
//import DoctorPatients from './doctor/DoctorPatients.vue'
import DoctorPrescriptions from './doctor/DoctorPrescriptions.vue'
import { useDoctorData } from '../composables/useDoctorData'

export default {
  name: 'DoctorPage',
  components: {
    AppLayout,
    DoctorDashboard,
    DoctorAppointments,
    //DoctorPatients,
    DoctorPrescriptions
  },
  setup() {
    const router = useRouter()
    const { getDoctorByEmail } = useDoctorData()

    const isLoading = ref(true)
    const currentUser = ref({ name: 'Doctor', role: 'doctor' })
    const doctorId = ref(4) // Default doctor ID
    const activeTab = ref('dashboard')

    const doctorTabs = [
      { id: 'dashboard', name: 'Dashboard', icon: 'fas fa-chart-line' },
      { id: 'appointments', name: 'Appointments', icon: 'fas fa-calendar-alt' },
      //{ id: 'patients', name: 'My Patients', icon: 'fas fa-users' },
      { id: 'prescriptions', name: 'Prescriptions', icon: 'fas fa-prescription' }
    ]

    const notifications = ref([
      { id: 1, message: 'New appointment request', time: '5 min ago' },
      { id: 2, message: 'Patient John Doe checked in', time: '15 min ago' },
      { id: 3, message: 'Lab results ready for review', time: '1 hour ago' }
    ])

    const tabComponents = {
      dashboard: 'DoctorDashboard',
      appointments: 'DoctorAppointments',
      patients: 'DoctorPatients',
      prescriptions: 'DoctorPrescriptions'
    }

    const currentTabComponent = computed(() => {
      return tabComponents[activeTab.value] || 'DoctorDashboard'
    })

    const loadUser = () => {
      const userJson = localStorage.getItem('currentUser')
      if (userJson) {
        const user = JSON.parse(userJson)
        currentUser.value = user

        // Find doctor by email to get doctor ID
        const doctor = getDoctorByEmail(user.email)
        if (doctor) {
          doctorId.value = doctor.id
        }

        isLoading.value = false
      } else {
        router.push('/login')
      }
    }

    const handleLogout = () => {
      localStorage.removeItem('currentUser')
      router.push('/login')
    }

    onMounted(() => {
      setTimeout(() => {
        loadUser()
      }, 100)
    })

    return {
      isLoading,
      currentUser,
      doctorId,
      activeTab,
      doctorTabs,
      notifications,
      currentTabComponent,
      handleLogout
    }
  }
}
</script>
