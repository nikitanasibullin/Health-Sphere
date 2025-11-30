<template>
  <!-- Show loading until user is loaded -->
  <div v-if="isLoading" class="min-h-screen flex items-center justify-center bg-gray-100">
    <div class="text-center">
      <i class="fas fa-spinner fa-spin text-4xl text-blue-500 mb-4"></i>
      <p class="text-gray-600">Loading...</p>
    </div>
  </div>
  
  <!-- Show content only when user is loaded -->
  <AppLayout
    v-else-if="currentUser"
    :user="currentUser"
    :notifications="notifications"
    :tabs="adminTabs"
    :active-tab="activeTab"
    @logout="handleLogout"
    @tab-change="activeTab = $event"
    @clear-notifications="notifications = []"
  >
    <component :is="currentTabComponent" />
  </AppLayout>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from './common/AppLayout.vue'
import AdminDashboard from './admin/AdminDashboard.vue'
import AdminPatients from './admin/AdminPatients.vue'
import AdminDoctors from './admin/AdminDoctors.vue'
import AdminAppointments from './admin/AdminAppointments.vue'
import AdminRecords from './admin/AdminRecords.vue'
import AdminBilling from './admin/AdminBilling.vue'

export default {
  name: 'AdminPage',
  components: {
    AppLayout,
    AdminDashboard,
    AdminPatients,
    AdminDoctors,
    AdminAppointments,
    AdminRecords,
    AdminBilling
  },
  setup() {
    const router = useRouter()
    const currentUser = ref(null)
    const isLoading = ref(true)  // Add loading state
    const activeTab = ref('dashboard')
    
    const adminTabs = [
      { id: 'dashboard', name: 'Dashboard', icon: 'fas fa-chart-line' },
      { id: 'patients', name: 'Patients', icon: 'fas fa-users' },
      { id: 'doctors', name: 'Doctors', icon: 'fas fa-user-md' },
      { id: 'appointments', name: 'Appointments', icon: 'fas fa-calendar-alt' },
      { id: 'records', name: 'Records', icon: 'fas fa-file-medical' },
      { id: 'billing', name: 'Billing', icon: 'fas fa-file-invoice-dollar' }
    ]
    
    const notifications = ref([
      { id: 1, message: 'New patient registered', time: '5 min ago' },
      { id: 2, message: 'Appointment scheduled', time: '10 min ago' }
    ])
    
    const tabComponents = {
      dashboard: 'AdminDashboard',
      patients: 'AdminPatients',
      doctors: 'AdminDoctors',
      appointments: 'AdminAppointments',
      records: 'AdminRecords',
      billing: 'AdminBilling'
    }
    
    const currentTabComponent = computed(() => {
      return tabComponents[activeTab.value] || 'AdminDashboard'
    })
    
    const loadUser = () => {
      const userJson = localStorage.getItem('currentUser')
      if (userJson) {
        currentUser.value = JSON.parse(userJson)
      } else {
        router.push('/login')
      }
      isLoading.value = false  // Done loading
    }
    
    const handleLogout = () => {
      localStorage.removeItem('currentUser')
      router.push('/login')
    }
    
    onMounted(() => {
      loadUser()
    })
    
    return {
      currentUser,
      isLoading,
      activeTab,
      adminTabs,
      notifications,
      currentTabComponent,
      handleLogout
    }
  }
}
</script>