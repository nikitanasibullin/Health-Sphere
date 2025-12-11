<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-users text-blue-500 mr-2"></i>My Patients
      </h2>
      
      <!-- Search -->
      <div class="mb-6">
        <div class="relative">
          <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
          <input 
            v-model="search" 
            type="text" 
            placeholder="Search patients..."
            class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
        </div>
      </div>
      
      <!-- Patients Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="patient in filteredPatients" 
          :key="patient.id" 
          class="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition card-hover"
        >
          <div class="flex items-center mb-4">
            <div class="w-16 h-16 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center mr-4">
              <span class="text-white font-bold text-2xl">{{ patient.name.charAt(0) }}</span>
            </div>
            <div>
              <h3 class="font-bold text-xl text-gray-800">{{ patient.name }}</h3>
              <p class="text-sm text-gray-600">Age: {{ patient.age }}</p>
            </div>
          </div>
          
          <div class="space-y-2 mb-4">
            <p class="text-sm text-gray-600">
              <i class="fas fa-envelope text-blue-500 mr-2 w-5"></i>{{ patient.email }}
            </p>
            <p class="text-sm text-gray-600">
              <i class="fas fa-phone text-green-500 mr-2 w-5"></i>{{ patient.phone }}
            </p>
            <p class="text-sm text-gray-600">
              <i class="fas fa-calendar text-purple-500 mr-2 w-5"></i>{{ getAppointmentCount(patient.id) }} appointments
            </p>
          </div>
          
          <button 
            @click="viewPatientDetails(patient)" 
            class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-2 rounded-lg hover:from-blue-700 hover:to-purple-700 transition"
          >
            <i class="fas fa-eye mr-2"></i>View Details
          </button>
        </div>
        
        <div v-if="filteredPatients.length === 0" class="col-span-full text-center py-12 text-gray-500">
          <i class="fas fa-users text-4xl mb-4"></i>
          <p>No patients found</p>
        </div>
      </div>
    </div>
    
    <!-- Patient Details Modal -->
    <div 
      v-if="showDetailsModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showDetailsModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-2xl p-8 animate-fadeIn max-h-[90vh] overflow-y-auto">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">Patient Details</h3>
          <button @click="showDetailsModal = false" class="text-gray-500 hover:text-gray-700">
            <i class="fas fa-times text-xl"></i>
          </button>
        </div>
        
        <div v-if="selectedPatient">
          <!-- Patient Info -->
          <div class="flex items-center mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl">
            <div class="w-20 h-20 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center mr-4">
              <span class="text-white font-bold text-3xl">{{ selectedPatient.name.charAt(0) }}</span>
            </div>
            <div>
              <h4 class="text-2xl font-bold text-gray-800">{{ selectedPatient.name }}</h4>
              <p class="text-gray-600">{{ selectedPatient.email }}</p>
              <p class="text-gray-600">{{ selectedPatient.phone }}</p>
            </div>
          </div>
          
          <!-- Patient Appointments -->
          <div class="mb-6">
            <h4 class="font-bold text-lg text-gray-800 mb-3">
              <i class="fas fa-calendar-alt text-purple-500 mr-2"></i>Appointments History
            </h4>
            <div class="space-y-2">
              <div 
                v-for="apt in getPatientAppointments(selectedPatient.id)" 
                :key="apt.id"
                class="flex justify-between items-center p-3 bg-gray-50 rounded-lg"
              >
                <div>
                  <p class="font-semibold">{{ apt.date }} at {{ apt.time }}</p>
                  <p class="text-sm text-gray-500">{{ apt.reason || 'Consultation' }}</p>
                </div>
                <span :class="getStatusClass(apt.status)">{{ apt.status }}</span>
              </div>
              <div v-if="getPatientAppointments(selectedPatient.id).length === 0" class="text-gray-500 text-center py-4">
                No appointments found
              </div>
            </div>
          </div>
          
          <!-- Patient Prescriptions -->
          <div>
            <h4 class="font-bold text-lg text-gray-800 mb-3">
              <i class="fas fa-prescription text-green-500 mr-2"></i>Prescriptions
            </h4>
            <div class="space-y-2">
              <div 
                v-for="prescription in getPatientPrescriptions(selectedPatient.id)" 
                :key="prescription.id"
                class="p-3 bg-gray-50 rounded-lg"
              >
                <div class="flex justify-between items-start">
                  <div>
                    <p class="font-semibold text-gray-800">{{ prescription.medication }}</p>
                    <p class="text-sm text-gray-600">{{ prescription.dosage }} - {{ prescription.duration }}</p>
                  </div>
                  <span class="text-xs text-gray-400">{{ prescription.date }}</span>
                </div>
              </div>
              <div v-if="getPatientPrescriptions(selectedPatient.id).length === 0" class="text-gray-500 text-center py-4">
                No prescriptions found
              </div>
            </div>
          </div>
        </div>
        
        <button 
          @click="showDetailsModal = false"
          class="w-full mt-6 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData'

export default {
  name: 'DoctorPatients',
  props: {
    doctorId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const { 
      appointments, 
      prescriptions, 
      getDoctorPatients, 
      getDoctorAppointments 
    } = useHospitalData()
    
    const myPatients = getDoctorPatients(props.doctorId)
    const myAppointments = getDoctorAppointments(props.doctorId)
    
    const search = ref('')
    const showDetailsModal = ref(false)
    const selectedPatient = ref(null)
    
    const filteredPatients = computed(() => {
      if (!search.value) return myPatients.value
      const searchLower = search.value.toLowerCase()
      return myPatients.value.filter(p => 
        p.name.toLowerCase().includes(searchLower) ||
        p.email.toLowerCase().includes(searchLower)
      )
    })
    
    const getAppointmentCount = (patientId) => {
      return myAppointments.value.filter(a => a.patientId === patientId).length
    }
    
    const getPatientAppointments = (patientId) => {
      return myAppointments.value.filter(a => a.patientId === patientId)
    }
    
    const getPatientPrescriptions = (patientId) => {
      return prescriptions.value.filter(p => p.patientId === patientId && p.doctorId === props.doctorId)
    }
    
    const getStatusClass = (status) => {
      const classes = {
        'Scheduled': 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold',
        'Completed': 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold',
        'Cancelled': 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold'
      }
      return classes[status] || classes['Scheduled']
    }
    
    const viewPatientDetails = (patient) => {
      selectedPatient.value = patient
      showDetailsModal.value = true
    }
    
    return {
      search,
      showDetailsModal,
      selectedPatient,
      filteredPatients,
      getAppointmentCount,
      getPatientAppointments,
      getPatientPrescriptions,
      getStatusClass,
      viewPatientDetails
    }
  }
}
</script>