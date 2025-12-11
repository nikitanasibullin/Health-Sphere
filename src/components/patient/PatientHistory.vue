<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-file-medical-alt text-blue-500 mr-2"></i>Medical History
      </h2>

      <!-- Empty State -->
      <div v-if="medicalRecords.length === 0" class="text-center py-12 text-gray-500">
        <i class="fas fa-file-medical text-4xl mb-4"></i>
        <p>No medical records found</p>
      </div>

      <!-- Records List -->
      <div v-else class="space-y-4">
        <div
          v-for="record in sortedRecords"
          :key="record.id"
          class="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition card-hover"
        >
          <div class="flex flex-col md:flex-row justify-between items-start mb-4">
            <div class="flex items-center">
              <div class="w-12 h-12 bg-gradient-to-r from-blue-400 to-purple-400 rounded-full flex items-center justify-center mr-4">
                <i class="fas fa-file-medical text-white text-xl"></i>
              </div>
              <div>
                <h3 class="font-bold text-xl text-gray-800">{{ record.type }}</h3>
                <p class="text-gray-600">{{ getDoctorName(record.doctorId) }}</p>
              </div>
            </div>
            <span class="text-gray-500 mt-2 md:mt-0">
              <i class="fas fa-calendar mr-1"></i>{{ formatDate(record.date) }}
            </span>
          </div>

          <div class="bg-gradient-to-r from-gray-50 to-blue-50 rounded-lg p-4">
            <div class="mb-3">
              <p class="text-sm font-semibold text-gray-600 mb-1">Diagnosis:</p>
              <p class="text-gray-800">{{ record.diagnosis }}</p>
            </div>
            <div v-if="record.treatment">
              <p class="text-sm font-semibold text-gray-600 mb-1">Treatment:</p>
              <p class="text-gray-800">{{ record.treatment }}</p>
            </div>
          </div>

          <!-- Related Prescriptions -->
          <div v-if="getRelatedPrescriptions(record).length > 0" class="mt-4">
            <p class="text-sm font-semibold text-gray-600 mb-2">
              <i class="fas fa-prescription text-green-500 mr-1"></i>Related Prescriptions:
            </p>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="prescription in getRelatedPrescriptions(record)"
                :key="prescription.id"
                class="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm"
              >
                {{ prescription.medication }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData'

export default {
  name: 'PatientHistory',
  props: {
    patientId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const {
      getDoctorName,
      getPatientMedicalRecords,
      getPatientPrescriptions
    } = useHospitalData()

    const medicalRecords = getPatientMedicalRecords(props.patientId)
    const prescriptions = getPatientPrescriptions(props.patientId)

    const sortedRecords = computed(() => {
      return [...medicalRecords.value].sort((a, b) => new Date(b.date) - new Date(a.date))
    })

    const formatDate = (dateStr) => {
      const date = new Date(dateStr)
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    }

    const getRelatedPrescriptions = (record) => {
      return prescriptions.value.filter(p =>
        p.doctorId === record.doctorId &&
        p.date === record.date
      )
    }

    return {
      medicalRecords,
      sortedRecords,
      getDoctorName,
      formatDate,
      getRelatedPrescriptions
    }
  }
}
</script>
