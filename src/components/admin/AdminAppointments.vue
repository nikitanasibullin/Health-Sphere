<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-3xl font-bold text-gray-800">
          <i class="fas fa-calendar-alt text-purple-500 mr-2"></i>Manage Appointments
        </h2>
        <button 
          @click="showAddModal = true" 
          class="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-lg hover:from-purple-700 hover:to-pink-700 shadow-lg transition"
        >
          <i class="fas fa-plus mr-2"></i>Add Appointment
        </button>
      </div>
      
      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-purple-50 to-pink-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">ID</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Patient</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Doctor</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Date</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Time</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="apt in appointments" :key="apt.id" class="hover:bg-gray-50 transition">
              <td class="px-6 py-4 whitespace-nowrap font-semibold text-gray-900">{{ apt.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ getPatientName(apt.patientId) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ getDoctorName(apt.doctorId) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ apt.date }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ apt.time }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="getStatusClass(apt.status)">{{ apt.status }}</span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button @click="cycleStatus(apt)" class="text-blue-600 hover:text-blue-800 mr-3" title="Change Status">
                  <i class="fas fa-sync-alt"></i>
                </button>
                <button @click="handleDelete(apt.id)" class="text-red-600 hover:text-red-800" title="Delete">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Add Modal -->
    <div 
      v-if="showAddModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showAddModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fadeIn">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">Add New Appointment</h3>
          <button @click="showAddModal = false" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>
        
        <form @submit.prevent="handleSubmit">
          <div class="space-y-4">
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Patient</label>
              <select 
                v-model="form.patientId" 
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Select patient...</option>
                <option v-for="patient in patients" :key="patient.id" :value="patient.id">
                  {{ patient.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Doctor</label>
              <select 
                v-model="form.doctorId" 
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <option value="">Select doctor...</option>
                <option v-for="doctor in doctors" :key="doctor.id" :value="doctor.id">
                  {{ doctor.name }} - {{ doctor.specialization }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Date</label>
              <input 
                v-model="form.date" 
                type="date" 
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Time</label>
              <input 
                v-model="form.time" 
                type="time" 
                required
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
            </div>
          </div>
          
          <div class="flex gap-4 mt-6">
            <button 
              type="button"
              @click="showAddModal = false"
              class="flex-1 px-4 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
            >
              Cancel
            </button>
            <button 
              type="submit"
              class="flex-1 px-4 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition"
            >
              Add Appointment
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData'

export default {
  name: 'AdminAppointments',
  setup() {
    const { 
      patients, 
      doctors, 
      appointments, 
      getPatientName, 
      getDoctorName,
      addAppointment,
      updateAppointmentStatus,
      deleteAppointment,
      addActivity
    } = useHospitalData()
    
    const showAddModal = ref(false)
    const form = ref({
      patientId: '',
      doctorId: '',
      date: '',
      time: ''
    })
    
    const getStatusClass = (status) => {
      const classes = {
        'Scheduled': 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold',
        'Completed': 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold',
        'Cancelled': 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold'
      }
      return classes[status] || classes['Scheduled']
    }
    
    const cycleStatus = (apt) => {
      const statuses = ['Scheduled', 'Completed', 'Cancelled']
      const currentIndex = statuses.indexOf(apt.status)
      const nextStatus = statuses[(currentIndex + 1) % statuses.length]
      updateAppointmentStatus(apt.id, nextStatus)
    }
    
    const handleSubmit = () => {
      addAppointment({
        patientId: parseInt(form.value.patientId),
        doctorId: parseInt(form.value.doctorId),
        date: form.value.date,
        time: form.value.time
      })
      addActivity('New appointment scheduled', 'fas fa-calendar-plus', 'bg-purple-500')
      showAddModal.value = false
      form.value = { patientId: '', doctorId: '', date: '', time: '' }
    }
    
    const handleDelete = (id) => {
      if (confirm('Are you sure you want to delete this appointment?')) {
        deleteAppointment(id)
        addActivity('Appointment cancelled', 'fas fa-calendar-times', 'bg-red-500')
      }
    }
    
    return {
      patients,
      doctors,
      appointments,
      showAddModal,
      form,
      getPatientName,
      getDoctorName,
      getStatusClass,
      cycleStatus,
      handleSubmit,
      handleDelete
    }
  }
}
</script>