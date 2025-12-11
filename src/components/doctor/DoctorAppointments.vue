<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-calendar-alt text-purple-500 mr-2"></i>My Appointments
      </h2>
      
      <!-- Filter -->
      <div class="mb-6 flex flex-wrap gap-4">
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
      
      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-purple-50 to-pink-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Patient</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Date</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Time</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Reason</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr 
              v-for="apt in filteredAppointments" 
              :key="apt.id" 
              class="hover:bg-gray-50 transition"
            >
              <td class="px-6 py-4 whitespace-nowrap">
                <div class="flex items-center">
                  <div class="w-10 h-10 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full flex items-center justify-center mr-3">
                    <span class="text-white font-bold">{{ getPatientName(apt.patientId).charAt(0) }}</span>
                  </div>
                  <span class="font-semibold text-gray-900">{{ getPatientName(apt.patientId) }}</span>
                </div>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ formatDate(apt.date) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ apt.time }}</td>
              <td class="px-6 py-4 text-gray-700">{{ apt.reason || 'Consultation' }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(apt.status)">{{ apt.status }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <select 
                  @change="handleStatusChange(apt.id, $event.target.value)" 
                  :value="apt.status"
                  class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500"
                >
                  <option value="Scheduled">Scheduled</option>
                  <option value="Completed">Completed</option>
                  <option value="Cancelled">Cancelled</option>
                </select>
              </td>
            </tr>
            <tr v-if="filteredAppointments.length === 0">
              <td colspan="6" class="px-6 py-12 text-center text-gray-500">
                <i class="fas fa-calendar-times text-4xl mb-4"></i>
                <p>No appointments found</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData'

export default {
  name: 'DoctorAppointments',
  props: {
    doctorId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const { getPatientName, getDoctorAppointments, updateAppointmentStatus, addActivity } = useHospitalData()
    
    const myAppointments = getDoctorAppointments(props.doctorId)
    const activeFilter = ref('all')
    
    const filters = [
      { label: 'All', value: 'all' },
      { label: 'Scheduled', value: 'Scheduled' },
      { label: 'Completed', value: 'Completed' },
      { label: 'Cancelled', value: 'Cancelled' }
    ]
    
    const filteredAppointments = computed(() => {
      if (activeFilter.value === 'all') {
        return myAppointments.value
      }
      return myAppointments.value.filter(a => a.status === activeFilter.value)
    })
    
    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
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
    
    const handleStatusChange = (appointmentId, newStatus) => {
      updateAppointmentStatus(appointmentId, newStatus)
      addActivity(`Appointment marked as ${newStatus}`, 'fas fa-calendar-check', 'bg-purple-500')
    }
    
    return {
      activeFilter,
      filters,
      filteredAppointments,
      getPatientName,
      formatDate,
      getStatusClass,
      handleStatusChange
    }
  }
}
</script>