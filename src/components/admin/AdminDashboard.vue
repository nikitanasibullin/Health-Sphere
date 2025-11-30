<template>
  <div class="animate-fadeIn">
    <h2 class="text-3xl font-bold text-gray-800 mb-6">Admin Dashboard</h2>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <!-- Total Patients -->
      <div class="bg-gradient-to-br from-blue-500 to-blue-700 p-6 rounded-2xl shadow-lg text-white card-hover">
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
      <div class="bg-gradient-to-br from-green-500 to-green-700 p-6 rounded-2xl shadow-lg text-white card-hover">
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
      <div class="bg-gradient-to-br from-purple-500 to-purple-700 p-6 rounded-2xl shadow-lg text-white card-hover">
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
      <div class="bg-gradient-to-br from-orange-500 to-orange-700 p-6 rounded-2xl shadow-lg text-white card-hover">
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
    
    <!-- Revenue and Department Stats -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
      <!-- Revenue Overview -->
      <div class="bg-white p-6 rounded-2xl shadow-lg card-hover">
        <h3 class="text-xl font-bold text-gray-800 mb-4">
          <i class="fas fa-dollar-sign text-green-500 mr-2"></i>Revenue Overview
        </h3>
        <div class="space-y-4">
          <div class="flex justify-between items-center p-4 bg-green-50 rounded-lg">
            <span class="text-gray-700 font-semibold">Total Revenue</span>
            <span class="text-2xl font-bold text-green-600">${{ totalRevenue.toLocaleString() }}</span>
          </div>
          <div class="flex justify-between items-center p-4 bg-blue-50 rounded-lg">
            <span class="text-gray-700 font-semibold">This Month</span>
            <span class="text-xl font-bold text-blue-600">${{ monthlyRevenue.toLocaleString() }}</span>
          </div>
        </div>
      </div>
      
      <!-- Departments -->
      <div class="bg-white p-6 rounded-2xl shadow-lg card-hover">
        <h3 class="text-xl font-bold text-gray-800 mb-4">
          <i class="fas fa-building text-blue-500 mr-2"></i>Departments
        </h3>
        <div class="space-y-2">
          <div 
            v-for="dept in departments" 
            :key="dept.name" 
            class="flex justify-between items-center p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
          >
            <span class="text-gray-700">{{ dept.name }}</span>
            <span class="text-blue-600 font-semibold">{{ dept.patients }} patients</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Recent Activity -->
    <div class="bg-white p-6 rounded-2xl shadow-lg">
      <h3 class="text-xl font-bold text-gray-800 mb-4">
        <i class="fas fa-history text-purple-500 mr-2"></i>Recent Activity
      </h3>
      <div class="space-y-3">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id" 
          class="flex items-center p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition"
        >
          <div :class="['w-10 h-10 rounded-full flex items-center justify-center mr-4', activity.color]">
            <i :class="[activity.icon, 'text-white']"></i>
          </div>
          <div class="flex-1">
            <p class="text-gray-800 font-semibold">{{ activity.text }}</p>
            <p class="text-gray-500 text-sm">{{ activity.time }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useHospitalData } from '../../composables/useHospitalData'

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
      monthlyRevenue
    } = useHospitalData()
    
    return {
      patients,
      doctors,
      appointments,
      departments,
      recentActivities,
      todayAppointments,
      scheduledToday,
      totalRevenue,
      monthlyRevenue
    }
  }
}
</script>