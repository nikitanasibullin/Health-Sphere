<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <h2 class="text-3xl font-bold text-gray-800 mb-6">
        <i class="fas fa-file-medical text-blue-500 mr-2"></i>Medical Records
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div
          v-for="record in medicalRecords"
          :key="record.id"
          class="border border-gray-200 rounded-xl p-6 hover:shadow-lg transition card-hover"
        >
          <div class="flex items-center justify-between mb-4">
            <h3 class="font-bold text-lg text-gray-800">{{ getPatientName(record.patientId) }}</h3>
            <span class="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-xs font-semibold">
              {{ record.type }}
            </span>
          </div>
          <p class="text-gray-600 text-sm mb-2">
            <i class="fas fa-user-md text-gray-400 mr-2"></i>
            {{ getDoctorName(record.doctorId) }}
          </p>
          <p class="text-gray-600 text-sm mb-4">
            <i class="fas fa-calendar text-gray-400 mr-2"></i>
            {{ record.date }}
          </p>
          <p class="text-gray-700 bg-gray-50 p-3 rounded-lg">{{ record.diagnosis }}</p>
        </div>

        <div v-if="medicalRecords.length === 0" class="col-span-full text-center py-12 text-gray-500">
          <i class="fas fa-file-medical text-4xl mb-4"></i>
          <p>No medical records found</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useHospitalData } from '../../composables/useHospitalData.js'

export default {
  name: 'AdminRecords',
  setup() {
    const { medicalRecords, getPatientName, getDoctorName } = useHospitalData()

    return {
      medicalRecords,
      getPatientName,
      getDoctorName
    }
  }
}
</script>
