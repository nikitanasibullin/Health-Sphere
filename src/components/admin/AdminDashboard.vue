<template>
  <div class="animate-fadeIn">
    <h2 class="text-3xl font-bold text-gray-800 mb-6">Admin Dashboard</h2>

    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Total Patients -->
      <div
        class="bg-gradient-to-br from-blue-500 to-blue-700 p-6 rounded-2xl shadow-lg text-white card-hover"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-blue-100 text-sm font-semibold">Total Patients</p>
            <p class="text-4xl font-bold mt-2">{{ patients.length }}</p>
            <p class="text-blue-100 text-xs mt-2">+12% from last month</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-users text-3xl"></i>
          </div>
        </div>
      </div>

      <!-- Total Doctors -->
      <div
        class="bg-gradient-to-br from-green-500 to-green-700 p-6 rounded-2xl shadow-lg text-white card-hover"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-green-100 text-sm font-semibold">Total Doctors</p>
            <p class="text-4xl font-bold mt-2">{{ doctors.length }}</p>
            <p class="text-green-100 text-xs mt-2">Active staff members</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-user-md text-3xl"></i>
          </div>
        </div>
      </div>

      <!-- Appointments -->
      <div
        class="bg-gradient-to-br from-purple-500 to-purple-700 p-6 rounded-2xl shadow-lg text-white card-hover"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-purple-100 text-sm font-semibold">Appointments</p>
            <p class="text-4xl font-bold mt-2">{{ appointments.length }}</p>
            <p class="text-purple-100 text-xs mt-2">Total scheduled</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-calendar-alt text-3xl"></i>
          </div>
        </div>
      </div>

      <!-- Today's Appointments -->
      <div
        class="bg-gradient-to-br from-orange-500 to-orange-700 p-6 rounded-2xl shadow-lg text-white card-hover"
      >
        <div class="flex items-center justify-between">
          <div>
            <p class="text-orange-100 text-sm font-semibold">Today's Appointments</p>
            <p class="text-4xl font-bold mt-2">{{ todayAppointments }}</p>
            <p class="text-orange-100 text-xs mt-2">{{ scheduledToday }} scheduled</p>
          </div>
          <div class="bg-white bg-opacity-20 p-4 rounded-full">
            <i class="fas fa-clock text-3xl"></i>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAdminData } from '../../composables/useAdminData'
import { onMounted } from 'vue'

export default {
  name: 'AdminDashboard',
  setup() {
    const {
      patients,
      doctors,
      appointments,
      departments,
      recentActivities,
      todayAppointments,
      scheduledToday,
      totalRevenue,
      monthlyRevenue,
      initializeData
    } = useAdminData()
    onMounted(async () => {
      await initializeData()
    })
    return {
      patients,
      doctors,
      appointments,
      departments,
      recentActivities,
      todayAppointments,
      scheduledToday,

    }
  },
}
</script>
