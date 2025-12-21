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
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200',
          ]"
        >
          {{ filter.label }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="text-center py-12">
        <i class="fas fa-spinner fa-spin text-4xl text-purple-500 mb-4"></i>
        <p class="text-gray-600">Loading appointments...</p>
      </div>

      <!-- Table -->
      <div v-else class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-purple-50 to-pink-50">
          <tr>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Patient
            </th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Date
            </th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Time
            </th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Status
            </th>
            <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">
              Actions
            </th>
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
                  <span class="text-white font-bold">{{ getInitials(apt.patient) }}</span>
                </div>
                <span class="font-semibold text-gray-900">
                  {{ formatPatientName(apt.patient) }}
                </span>
              </div>
            </td>
            <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ apt.schedule?.date || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ apt.schedule?.start_time || 'N/A' }}</td>
            <td class="px-6 py-4 whitespace-nowrap">
              <span :class="getStatusClass(apt.status)">{{ capitalizeStatus(apt.status) }}</span>
            </td>
            <td class="px-6 py-4 whitespace-nowrap">
              <button
                  @click="openEditModal(apt)"
                  class="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-semibold transition flex items-center gap-2"
              >
                <i class="fas fa-edit"></i>
                Edit
              </button>
            </td>
          </tr>
          <tr v-if="filteredAppointments.length === 0">
            <td colspan="5" class="px-6 py-12 text-center text-gray-500">
              <i class="fas fa-calendar-times text-4xl mb-4 block"></i>
              <p>No appointments found</p>
            </td>
          </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Edit Modal -->
    <div
        v-if="showEditModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
        @click.self="closeEditModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <div class="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center z-10">
          <h3 class="text-2xl font-bold text-gray-800">
            <i class="fas fa-edit text-purple-500 mr-2"></i>Edit Appointment
          </h3>
          <button @click="closeEditModal" class="text-gray-400 hover:text-gray-600 transition">
            <i class="fas fa-times text-2xl"></i>
          </button>
        </div>

        <!-- Loading State in Modal -->
        <div v-if="isLoadingDetails" class="p-12 text-center">
          <i class="fas fa-spinner fa-spin text-4xl text-purple-500 mb-4"></i>
          <p class="text-gray-600">Loading appointment details...</p>
        </div>

        <form v-else @submit.prevent="saveAppointment" class="p-6 space-y-6">
          <!-- Patient Info -->
          <div class="bg-gray-50 rounded-lg p-4">
            <h4 class="text-sm font-semibold text-gray-500 uppercase mb-2">Patient</h4>
            <p class="text-lg font-bold text-gray-800">
              {{ formatPatientName(currentAppointment?.patient) }}
            </p>
            <p class="text-sm text-gray-600">
              {{ currentAppointment?.schedule?.date }} at {{ currentAppointment?.schedule?.start_time }}
            </p>
          </div>

          <!-- Appointment Status -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Appointment Status
            </label>
            <select
                v-model="editForm.status"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                required
            >
              <option value="scheduled">Scheduled</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>

          <!-- Appointment Information -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-2">
              Appointment Notes / Diagnosis
            </label>
            <textarea
                v-model="editForm.information"
                rows="5"
                class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                placeholder="Enter detailed appointment information, diagnosis, recommendations..."
            ></textarea>
          </div>

          <!-- Validation Errors -->
          <div v-if="validationErrors.length > 0" class="p-4 bg-yellow-50 border-2 border-yellow-300 rounded-lg">
            <h4 class="font-bold text-yellow-700 mb-2">
              <i class="fas fa-exclamation-circle mr-2"></i>Validation Errors
            </h4>
            <ul class="list-disc list-inside text-yellow-600 text-sm space-y-1">
              <li v-for="(error, idx) in validationErrors" :key="idx">{{ error }}</li>
            </ul>
          </div>

          <!-- This Appointment's Prescriptions -->
          <div class="border-t pt-6">
            <h4 class="text-lg font-bold text-gray-800 mb-4">
              <i class="fas fa-prescription text-purple-500 mr-2"></i>Prescriptions for This Appointment
              <span class="text-sm font-normal text-gray-500 ml-2">({{ appointmentMedicaments.length }} items)</span>
            </h4>

            <!-- Appointment Medicaments List -->
            <div v-if="appointmentMedicaments.length > 0" class="space-y-3">
              <div
                  v-for="med in appointmentMedicaments"
                  :key="'apt-' + med.id"
                  class="p-4 border-2 border-purple-200 rounded-lg bg-purple-50"
              >
                <div class="flex justify-between items-start">
                  <div class="flex-1">
                    <div class="flex items-center gap-3 mb-2 flex-wrap">
                      <span class="font-bold text-gray-800 text-lg">{{ med.medicament_name }}</span>
                      <span class="px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full text-xs font-semibold">
                        This Appointment
                      </span>
                      <span :class="getMedicamentBadgeClass(med)">
                        {{ getMedicamentStatus(med) }}
                      </span>
                    </div>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm text-gray-600">
                      <div v-if="med.dosage">
                        <span class="font-semibold text-gray-700">Dosage:</span>
                        <span class="ml-1">{{ med.dosage }}</span>
                      </div>
                      <div v-if="med.frequency">
                        <span class="font-semibold text-gray-700">Frequency:</span>
                        <span class="ml-1">{{ med.frequency }}</span>
                      </div>
                      <div v-if="med.start_date">
                        <span class="font-semibold text-gray-700">Start:</span>
                        <span class="ml-1">{{ formatDate(med.start_date) }}</span>
                      </div>
                      <div v-if="med.end_date">
                        <span class="font-semibold text-gray-700">End:</span>
                        <span class="ml-1">{{ formatDate(med.end_date) }}</span>
                      </div>
                    </div>
                    <div v-if="med.notes" class="mt-2 text-sm text-gray-500 italic">
                      <i class="fas fa-comment mr-1"></i>{{ med.notes }}
                    </div>
                  </div>
                  <button
                      type="button"
                      @click="confirmDeleteMedicament(med)"
                      class="text-red-500 hover:text-red-700 transition ml-4 p-2"
                      title="Delete prescription"
                  >
                    <i class="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            </div>

            <!-- No Appointment Medicaments Message -->
            <div v-else class="text-center py-6 text-gray-500 bg-gray-50 rounded-lg">
              <i class="fas fa-prescription-bottle text-3xl mb-2"></i>
              <p>No prescriptions added for this appointment yet</p>
            </div>
          </div>

          <!-- Patient's All Medicaments Section (Collapsed by default) -->
          <div class="border-t pt-6">
            <div
                class="flex justify-between items-center cursor-pointer"
                @click="showAllPatientMeds = !showAllPatientMeds"
            >
              <h4 class="text-lg font-bold text-gray-800">
                <i class="fas fa-pills text-green-500 mr-2"></i>All Patient's Medicaments
                <span class="text-sm font-normal text-gray-500 ml-2">({{ allPatientMedicaments.length }} total)</span>
              </h4>
              <button type="button" class="text-gray-500 hover:text-gray-700 transition">
                <i :class="showAllPatientMeds ? 'fas fa-chevron-up' : 'fas fa-chevron-down'"></i>
              </button>
            </div>

            <!-- All Patient Medicaments List -->
            <div v-if="showAllPatientMeds" class="mt-4 space-y-3">
              <div v-if="allPatientMedicaments.length > 0">
                <div
                    v-for="med in allPatientMedicaments"
                    :key="'patient-' + med.id"
                    class="p-4 border-2 rounded-lg"
                    :class="getMedicamentStatusClass(med)"
                >
                  <div class="flex justify-between items-start">
                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-2 flex-wrap">
                        <span class="font-bold text-gray-800 text-lg">{{ med.medicament_name }}</span>
                        <span :class="getMedicamentBadgeClass(med)">
                          {{ getMedicamentStatus(med) }}
                        </span>
                      </div>
                      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm text-gray-600">
                        <div v-if="med.dosage">
                          <span class="font-semibold text-gray-700">Dosage:</span>
                          <span class="ml-1">{{ med.dosage }}</span>
                        </div>
                        <div v-if="med.frequency">
                          <span class="font-semibold text-gray-700">Frequency:</span>
                          <span class="ml-1">{{ med.frequency }}</span>
                        </div>
                        <div v-if="med.start_date">
                          <span class="font-semibold text-gray-700">Start:</span>
                          <span class="ml-1">{{ formatDate(med.start_date) }}</span>
                        </div>
                        <div v-if="med.end_date">
                          <span class="font-semibold text-gray-700">End:</span>
                          <span class="ml-1">{{ formatDate(med.end_date) }}</span>
                        </div>
                      </div>
                      <div v-if="med.notes" class="mt-2 text-sm text-gray-500 italic">
                        <i class="fas fa-comment mr-1"></i>{{ med.notes }}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="text-center py-6 text-gray-500 bg-gray-50 rounded-lg">
                <i class="fas fa-prescription-bottle text-3xl mb-2"></i>
                <p>No medicaments prescribed for this patient</p>
              </div>
            </div>
          </div>

          <!-- Add New Prescriptions Section -->
          <div class="border-t pt-6">
            <div class="flex justify-between items-center mb-4">
              <h4 class="text-lg font-bold text-gray-800">
                <i class="fas fa-plus-circle text-green-500 mr-2"></i>Add New Prescriptions
              </h4>
              <button
                  type="button"
                  @click="addNewPrescription"
                  class="px-4 py-2 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition flex items-center gap-2"
              >
                <i class="fas fa-plus"></i>
                Add Prescription
              </button>
            </div>

            <!-- New Prescription Items -->
            <div
                v-for="(prescription, index) in editForm.newPrescriptions"
                :key="'new-' + index"
                class="mb-6 p-4 border-2 rounded-lg"
                :class="getPrescriptionConflicts(index).length > 0 ? 'border-red-300 bg-red-50' : 'border-green-200 bg-green-50'"
            >
              <div class="flex justify-between items-center mb-4">
                <h5 class="font-bold text-gray-800">
                  <span class="px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs font-semibold mr-2">
                    New
                  </span>
                  Prescription #{{ index + 1 }}
                  <span v-if="getPrescriptionConflicts(index).length > 0" class="ml-2 px-2 py-0.5 bg-red-100 text-red-700 rounded-full text-xs font-semibold">
                    <i class="fas fa-exclamation-triangle mr-1"></i>Has Conflicts
                  </span>
                </h5>
                <button
                    type="button"
                    @click="removeNewPrescription(index)"
                    class="text-red-600 hover:text-red-800 transition"
                >
                  <i class="fas fa-trash"></i>
                </button>
              </div>

              <div class="space-y-4">
                <!-- Medicament Name - Select -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2">
                    Medicament Name <span class="text-red-500">*</span>
                  </label>
                  <select
                      v-model="prescription.medicament_id"
                      @change="onMedicamentSelect(index)"
                      class="w-full border rounded-lg px-4 py-3 focus:outline-none focus:ring-2 bg-white"
                      :class="getPrescriptionConflicts(index).length > 0
                        ? 'border-red-400 focus:ring-red-500'
                        : 'border-gray-300 focus:ring-green-500'"
                      required
                  >
                    <option value="">-- Select medicament --</option>
                    <option
                        v-for="med in allMedicaments"
                        :key="med.id"
                        :value="med.id"
                    >
                      {{ med.name }}
                    </option>
                  </select>
                </div>

                <!-- Drug Conflicts Warning - Right after medicament selection -->
                <div v-if="getPrescriptionConflicts(index).length > 0" class="p-4 bg-red-100 border-2 border-red-400 rounded-lg">
                  <h4 class="font-bold text-red-700 mb-2">
                    <i class="fas fa-exclamation-triangle mr-2"></i>Drug Interactions Detected!
                  </h4>
                  <ul class="list-disc list-inside text-red-600 text-sm space-y-1">
                    <li v-for="(conflict, idx) in getPrescriptionConflicts(index)" :key="idx">{{ conflict }}</li>
                  </ul>
                  <p class="text-red-600 text-sm mt-3 font-semibold">
                    <i class="fas fa-hand-paper mr-1"></i>
                    Remove this medication or adjust dates to resolve conflict.
                  </p>
                </div>

                <!-- Loading contraindications -->
                <div v-if="prescription.isLoadingContraindications" class="text-center py-2">
                  <i class="fas fa-spinner fa-spin text-orange-500"></i>
                  <span class="text-sm text-gray-600 ml-2">Loading contraindications...</span>
                </div>

                <!-- Medicament Contraindications Display -->
                <div v-if="prescription.medicamentContraindications?.length > 0" class="p-3 bg-orange-50 border border-orange-200 rounded-lg">
                  <p class="text-sm font-semibold text-orange-700 mb-2">
                    <i class="fas fa-exclamation-triangle mr-1"></i>Medicament other contraindications:
                  </p>
                  <div class="flex flex-wrap gap-1">
                    <span
                        v-for="contra in prescription.medicamentContraindications"
                        :key="contra"
                        class="px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full text-xs"
                    >
                      {{ contra }}
                    </span>
                  </div>
                </div>

                <!-- No contraindications message -->
                <div v-else-if="prescription.medicament_id && !prescription.isLoadingContraindications && getPrescriptionConflicts(index).length === 0" class="p-3 bg-green-50 border border-green-200 rounded-lg">
                  <p class="text-sm text-green-700">
                    <i class="fas fa-check-circle mr-1"></i>No contraindications or conflicts found for this medicament
                  </p>
                </div>

                <!-- Dosage and Frequency -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">Dosage</label>
                    <input
                        v-model="prescription.dosage"
                        type="text"
                        class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                        placeholder="e.g., 500mg"
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">Frequency</label>
                    <input
                        v-model="prescription.frequency"
                        type="text"
                        class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                        placeholder="e.g., Twice daily"
                    />
                  </div>
                </div>

                <!-- Dates -->
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">
                      Start Date <span class="text-red-500">*</span>
                    </label>
                    <input
                        v-model="prescription.start_date"
                        type="date"
                        @change="() => {}"
                        class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                        required
                    />
                  </div>
                  <div>
                    <label class="block text-sm font-semibold text-gray-700 mb-2">
                      End Date <span class="text-red-500">*</span>
                    </label>
                    <input
                        v-model="prescription.end_date"
                        type="date"
                        @change="() => {}"
                        class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                        :class="{ 'border-red-500 ring-2 ring-red-200': prescription.medicament_id && !prescription.end_date }"
                        required
                    />
                    <p v-if="prescription.medicament_id && !prescription.end_date" class="text-red-500 text-xs mt-1">
                      <i class="fas fa-exclamation-circle mr-1"></i>End date is required
                    </p>
                  </div>
                </div>

                <!-- Date validation error -->
                <div v-if="prescription.start_date && prescription.end_date && prescription.start_date > prescription.end_date"
                     class="p-2 bg-red-50 border border-red-200 rounded-lg">
                  <p class="text-red-600 text-sm">
                    <i class="fas fa-exclamation-circle mr-1"></i>
                    End date must be after or equal to start date
                  </p>
                </div>

                <!-- Notes -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 mb-2">
                    Notes
                  </label>
                  <textarea
                      v-model="prescription.notes"
                      rows="3"
                      class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-green-500 bg-white"
                      placeholder="Additional notes for this prescription..."
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- No New Prescriptions Message -->
            <div v-if="editForm.newPrescriptions.length === 0" class="text-center py-8 text-gray-500 border-2 border-dashed border-gray-300 rounded-lg">
              <i class="fas fa-prescription-bottle text-4xl mb-2"></i>
              <p>Click "Add Prescription" to add new medications</p>
            </div>
          </div>

          <!-- Patient General Contraindications Section -->
          <div class="border-t pt-6">
            <h4 class="text-lg font-bold text-gray-800 mb-4">
              <i class="fas fa-exclamation-triangle text-red-500 mr-2"></i>Patient General Contraindications
            </h4>

            <!-- Current Patient Contraindications Display with Delete -->
            <div v-if="patientOtherContraindications.length > 0" class="mb-4">
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Current Patient Contraindications:
              </label>
              <div class="flex flex-wrap gap-2 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div
                    v-for="contra in patientOtherContraindications"
                    :key="contra.contraindication_id"
                    class="flex items-center gap-1 px-3 py-1 bg-red-100 text-red-700 rounded-full text-sm font-semibold group hover:bg-red-200 transition"
                >
                  <i class="fas fa-exclamation-triangle mr-1"></i>
                  <span>{{ contra.contraindication_name }}</span>
                  <button
                      type="button"
                      @click="confirmDeleteContraindication(contra)"
                      class="ml-1 w-5 h-5 flex items-center justify-center bg-red-200 hover:bg-red-400 hover:text-white rounded-full transition"
                      title="Remove this contraindication"
                  >
                    <i class="fas fa-times text-xs"></i>
                  </button>
                </div>
              </div>
            </div>
            <div v-else class="mb-4 p-4 bg-gray-50 border border-gray-200 rounded-lg text-gray-500 text-sm">
              <i class="fas fa-info-circle mr-2"></i>No general contraindications recorded for this patient
            </div>

            <!-- Add New Patient Contraindications -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 mb-2">
                Add New Patient Contraindications
                <span class="text-gray-400 font-normal">(comma-separated, e.g., allergies, conditions)</span>
              </label>
              <textarea
                  v-model="editForm.newContraindications"
                  rows="3"
                  class="w-full border border-gray-300 rounded-lg px-4 py-3 focus:outline-none focus:ring-2 focus:ring-purple-500"
                  placeholder="Enter patient-specific contraindications, e.g., 'Allergy to penicillin, Pregnancy, Diabetes'"
              ></textarea>
              <p class="text-xs text-gray-500 mt-1">
                <i class="fas fa-info-circle mr-1"></i>
                These will be saved when you click "Save Changes"
              </p>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="flex justify-end gap-4 pt-4 border-t sticky bottom-0 bg-white py-4">
            <button
                type="button"
                @click="closeEditModal"
                class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
                type="submit"
                :disabled="isSaving || hasAnyConflicts"
                class="px-6 py-3 bg-purple-600 text-white rounded-lg font-semibold hover:bg-purple-700 transition flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i :class="isSaving ? 'fas fa-spinner fa-spin' : 'fas fa-save'"></i>
              {{ isSaving ? 'Saving...' : 'Save Changes' }}
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- Delete Medicament Confirmation Modal -->
    <div
        v-if="showDeleteMedicamentModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4"
        @click.self="closeDeleteMedicamentModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
        <div class="text-center">
          <div class="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="fas fa-exclamation-triangle text-red-600 text-3xl"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">Delete Prescription</h3>
          <p class="text-gray-600 mb-2">Are you sure you want to delete this prescription?</p>
          <p class="font-bold text-lg text-gray-800 mb-4">"{{ medicamentToDelete?.medicament_name }}"</p>
          <div class="flex justify-center gap-4">
            <button
                @click="closeDeleteMedicamentModal"
                class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
                @click="deleteMedicament"
                :disabled="isDeletingMedicament"
                class="px-6 py-3 bg-red-600 text-white rounded-lg font-semibold hover:bg-red-700 transition flex items-center gap-2 disabled:opacity-50"
            >
              <i :class="isDeletingMedicament ? 'fas fa-spinner fa-spin' : 'fas fa-trash'"></i>
              {{ isDeletingMedicament ? 'Deleting...' : 'Delete' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Contraindication Confirmation Modal -->
    <div
        v-if="showDeleteContraindicationModal"
        class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[60] p-4"
        @click.self="closeDeleteContraindicationModal"
    >
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6">
        <div class="text-center">
          <div class="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <i class="fas fa-exclamation-triangle text-orange-600 text-3xl"></i>
          </div>
          <h3 class="text-xl font-bold text-gray-800 mb-2">Remove Contraindication</h3>
          <p class="text-gray-600 mb-2">Are you sure you want to remove this contraindication?</p>
          <p class="font-bold text-lg text-gray-800 mb-4">"{{ contraindicationToDelete?.contraindication_name }}"</p>
          <p class="text-sm text-orange-600 mb-4">
            <i class="fas fa-info-circle mr-1"></i>
            This condition will no longer be tracked for this patient.
          </p>
          <div class="flex justify-center gap-4">
            <button
                @click="closeDeleteContraindicationModal"
                class="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-semibold hover:bg-gray-200 transition"
            >
              Cancel
            </button>
            <button
                @click="deleteContraindication"
                :disabled="isDeletingContraindication"
                class="px-6 py-3 bg-orange-600 text-white rounded-lg font-semibold hover:bg-orange-700 transition flex items-center gap-2 disabled:opacity-50"
            >
              <i :class="isDeletingContraindication ? 'fas fa-spinner fa-spin' : 'fas fa-trash'"></i>
              {{ isDeletingContraindication ? 'Removing...' : 'Remove' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useDoctorData } from '../../composables/useDoctorData'

export default {
  name: 'DoctorAppointments',
  setup() {
    const {
      addPatientContraindications,
      deletePatientOtherContraindication,
      addMedicamentsForAppointment,
      getDoctorAppointments,
      updateAppointmentStatus,
      getAllMedicaments,
      getPatientMedicaments,
      getAppointmentMedicaments,
      getPatientOtherContraindications,
      deletePatientMedicament,
      getMedicamentAllContraindications,
      getMedicamentInteractions,
    } = useDoctorData()

    // Data
    const myAppointments = ref([])
    const allMedicaments = ref([])
    const medicamentInteractions = ref([])
    const patientOtherContraindications = ref([])
    const appointmentMedicaments = ref([])
    const allPatientMedicaments = ref([])
    const showAllPatientMeds = ref(false)
    const activeFilter = ref('all')
    const showEditModal = ref(false)
    const showDeleteMedicamentModal = ref(false)
    const showDeleteContraindicationModal = ref(false)
    const currentAppointment = ref(null)
    const medicamentToDelete = ref(null)
    const contraindicationToDelete = ref(null)
    const isLoading = ref(false)
    const isLoadingDetails = ref(false)
    const isSaving = ref(false)
    const isDeletingMedicament = ref(false)
    const isDeletingContraindication = ref(false)

    const editForm = ref({
      status: '',
      information: '',
      newPrescriptions: [],
      newContraindications: '',
    })

    const filters = [
      { label: 'All', value: 'all' },
      { label: 'Scheduled', value: 'scheduled' },
      { label: 'Completed', value: 'completed' },
      { label: 'Cancelled', value: 'cancelled' },
    ]

    // Computed
    const filteredAppointments = computed(() => {
      if (!myAppointments.value) return []
      if (activeFilter.value === 'all') return myAppointments.value
      return myAppointments.value.filter((a) => a.status === activeFilter.value)
    })

    // Helper function to check if two date ranges overlap
    const datesOverlap = (start1, end1, start2, end2) => {
      if (!start1 || !end1 || !start2 || !end2) {
        return false
      }
      return start1 <= end2 && start2 <= end1
    }

    // Get medicament name by ID
    const getMedicamentName = (medicamentId) => {
      const med = allMedicaments.value.find(m => m.id === medicamentId)
      return med ? med.name : `Medicament #${medicamentId}`
    }

    // Get conflicts for a specific prescription by index
    const getPrescriptionConflicts = (prescriptionIndex) => {
      const prescription = editForm.value.newPrescriptions[prescriptionIndex]
      if (!prescription || !prescription.medicament_id || !prescription.start_date || !prescription.end_date) {
        return []
      }

      const conflicts = []
      const newMedId = parseInt(prescription.medicament_id)
      const newMedName = getMedicamentName(newMedId)

      // Get all existing meds
      const existingMeds = [
        ...appointmentMedicaments.value.map(m => ({
          id: m.medicament_id,
          name: m.medicament_name,
          start_date: m.start_date,
          end_date: m.end_date
        })),
        ...allPatientMedicaments.value.map(m => ({
          id: m.medicament_id,
          name: m.medicament_name,
          start_date: m.start_date,
          end_date: m.end_date
        }))
      ]

      // Remove duplicates
      const existingMedsMap = new Map()
      for (const med of existingMeds) {
        const key = `${med.id}-${med.start_date}-${med.end_date}`
        if (!existingMedsMap.has(key)) {
          existingMedsMap.set(key, med)
        }
      }
      const allExistingMeds = Array.from(existingMedsMap.values())

      // Check interactions with existing meds
      for (const interaction of medicamentInteractions.value) {
        const id1 = interaction.first_medicament_id
        const id2 = interaction.second_medicament_id

        for (const existingMed of allExistingMeds) {
          const isInteraction =
              (newMedId === id1 && existingMed.id === id2) ||
              (newMedId === id2 && existingMed.id === id1)

          if (isInteraction && datesOverlap(prescription.start_date, prescription.end_date, existingMed.start_date, existingMed.end_date)) {
            const conflictWith = newMedId === id1 ? interaction.second_medicament_name : interaction.first_medicament_name
            conflicts.push(
                `Conflicts with existing "${conflictWith}" (${existingMed.start_date} - ${existingMed.end_date})`
            )
          }
        }
      }

      // Check interactions with other new prescriptions
      for (let j = 0; j < editForm.value.newPrescriptions.length; j++) {
        if (j === prescriptionIndex) continue

        const otherPrescription = editForm.value.newPrescriptions[j]
        if (!otherPrescription.medicament_id || !otherPrescription.start_date || !otherPrescription.end_date) continue

        const otherMedId = parseInt(otherPrescription.medicament_id)

        // Check for same medicament with overlapping dates
        if (newMedId === otherMedId) {
          if (datesOverlap(prescription.start_date, prescription.end_date, otherPrescription.start_date, otherPrescription.end_date)) {
            conflicts.push(`Same medicament added in Prescription #${j + 1} with overlapping dates`)
          }
        }

        // Check for interactions between new prescriptions
        for (const interaction of medicamentInteractions.value) {
          const id1 = interaction.first_medicament_id
          const id2 = interaction.second_medicament_id

          const isInteraction =
              (newMedId === id1 && otherMedId === id2) ||
              (newMedId === id2 && otherMedId === id1)

          if (isInteraction && datesOverlap(prescription.start_date, prescription.end_date, otherPrescription.start_date, otherPrescription.end_date)) {
            const conflictWith = newMedId === id1 ? interaction.second_medicament_name : interaction.first_medicament_name
            conflicts.push(`Conflicts with Prescription #${j + 1} "${conflictWith}"`)
          }
        }
      }

      // Check if same medicament already exists with overlapping dates
      for (const existingMed of allExistingMeds) {
        if (newMedId === existingMed.id) {
          if (datesOverlap(prescription.start_date, prescription.end_date, existingMed.start_date, existingMed.end_date)) {
            conflicts.push(`Already prescribed (${existingMed.start_date} - ${existingMed.end_date})`)
          }
        }
      }

      return [...new Set(conflicts)]
    }

    // Check if any prescription has conflicts
    const hasAnyConflicts = computed(() => {
      for (let i = 0; i < editForm.value.newPrescriptions.length; i++) {
        if (getPrescriptionConflicts(i).length > 0) {
          return true
        }
      }
      return false
    })

    // Validation errors for required fields
    const validationErrors = computed(() => {
      const errors = []

      for (let i = 0; i < editForm.value.newPrescriptions.length; i++) {
        const prescription = editForm.value.newPrescriptions[i]
        const prescNum = i + 1

        if (prescription.medicament_id) {
          if (!prescription.start_date) {
            errors.push(`Prescription #${prescNum}: Start date is required`)
          }
          if (!prescription.end_date) {
            errors.push(`Prescription #${prescNum}: End date is required`)
          }
          if (prescription.start_date && prescription.end_date && prescription.start_date > prescription.end_date) {
            errors.push(`Prescription #${prescNum}: End date must be after or equal to start date`)
          }
        }
      }

      return errors
    })

    // Methods
    const getInitials = (patient) => {
      if (!patient) return '?'
      return patient.first_name?.charAt(0) || '?'
    }

    const formatPatientName = (patient) => {
      if (!patient) return 'Unknown Patient'
      return `${patient.first_name || ''} ${patient.last_name || ''} ${patient.patronymic || ''}`.trim()
    }

    const capitalizeStatus = (status) => {
      if (!status) return ''
      return status.charAt(0).toUpperCase() + status.slice(1)
    }

    const getStatusClass = (status) => {
      const classes = {
        scheduled: 'px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-semibold',
        completed: 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold',
        cancelled: 'px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold',
      }
      return classes[status] || classes['scheduled']
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return dateStr
    }

    const getMedicamentStatus = (med) => {
      const today = new Date().toISOString().split('T')[0]

      if (!med.end_date) {
        return 'Active (Ongoing)'
      }

      if (med.end_date < today) {
        return 'Completed'
      }

      if (med.start_date > today) {
        return 'Scheduled'
      }

      return 'Active'
    }

    const getMedicamentStatusClass = (med) => {
      const today = new Date().toISOString().split('T')[0]

      if (!med.end_date || (med.start_date <= today && med.end_date >= today)) {
        return 'border-green-200 bg-green-50'
      }

      if (med.end_date < today) {
        return 'border-gray-200 bg-gray-50'
      }

      if (med.start_date > today) {
        return 'border-blue-200 bg-blue-50'
      }

      return 'border-green-200 bg-green-50'
    }

    const getMedicamentBadgeClass = (med) => {
      const today = new Date().toISOString().split('T')[0]

      if (!med.end_date || (med.start_date <= today && med.end_date >= today)) {
        return 'px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs font-semibold'
      }

      if (med.end_date < today) {
        return 'px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full text-xs font-semibold'
      }

      if (med.start_date > today) {
        return 'px-2 py-0.5 bg-blue-100 text-blue-700 rounded-full text-xs font-semibold'
      }

      return 'px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs font-semibold'
    }

    const createEmptyPrescription = () => ({
      medicament_id: '',
      dosage: '',
      frequency: '',
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      notes: '',
      medicamentContraindications: [],
      isLoadingContraindications: false,
    })

    const addNewPrescription = () => {
      editForm.value.newPrescriptions.push(createEmptyPrescription())
    }

    const removeNewPrescription = (index) => {
      editForm.value.newPrescriptions.splice(index, 1)
    }

    // When medicament is selected - load its contraindications
    const onMedicamentSelect = async (index) => {
      const prescription = editForm.value.newPrescriptions[index]

      if (!prescription.medicament_id) {
        prescription.medicamentContraindications = []
        return
      }

      prescription.isLoadingContraindications = true

      try {
        const data = await getMedicamentAllContraindications(prescription.medicament_id)

        if (data?.contraindications) {
          const otherContras = data.contraindications.other_contraindications || []
          const contraNames = otherContras.map(c => c.name)
          prescription.medicamentContraindications = contraNames
        } else {
          prescription.medicamentContraindications = []
        }
      } catch (error) {
        console.error('Error loading medicament contraindications:', error)
        prescription.medicamentContraindications = []
      } finally {
        prescription.isLoadingContraindications = false
      }
    }

    // Confirm delete contraindication
    const confirmDeleteContraindication = (contra) => {
      contraindicationToDelete.value = contra
      showDeleteContraindicationModal.value = true
    }

    const closeDeleteContraindicationModal = () => {
      showDeleteContraindicationModal.value = false
      contraindicationToDelete.value = null
    }

    // Delete contraindication
    const deleteContraindication = async () => {
      if (!contraindicationToDelete.value || !currentAppointment.value?.patient?.id) return

      isDeletingContraindication.value = true

      try {
        await deletePatientOtherContraindication(
            currentAppointment.value.patient.id,
            contraindicationToDelete.value.contraindication_id
        )

        // Remove from local list
        patientOtherContraindications.value = patientOtherContraindications.value.filter(
            c => c.contraindication_id !== contraindicationToDelete.value.contraindication_id
        )

        closeDeleteContraindicationModal()
      } catch (error) {
        console.error('Error deleting contraindication:', error)
        alert('Failed to delete contraindication: ' + (error.response?.data?.detail || error.message))
      } finally {
        isDeletingContraindication.value = false
      }
    }

    const openEditModal = async (appointment) => {
      currentAppointment.value = appointment
      showEditModal.value = true
      isLoadingDetails.value = true
      showAllPatientMeds.value = false

      try {
        const [rawAppointmentMeds, rawPatientMeds, otherContras, interactions] = await Promise.all([
          getAppointmentMedicaments(appointment.id),
          getPatientMedicaments(appointment.patient.id),
          getPatientOtherContraindications(appointment.patient.id),
          getMedicamentInteractions(),
        ])

        medicamentInteractions.value = interactions || []
        patientOtherContraindications.value = otherContras || []

        appointmentMedicaments.value = (rawAppointmentMeds || []).map(med => ({
          ...med,
          medicament_name: getMedicamentName(med.medicament_id)
        })).sort((a, b) => new Date(b.start_date) - new Date(a.start_date))

        allPatientMedicaments.value = (rawPatientMeds || []).map(med => ({
          ...med,
          medicament_name: getMedicamentName(med.medicament_id)
        })).sort((a, b) => new Date(b.start_date) - new Date(a.start_date))

        editForm.value = {
          status: appointment.status || 'scheduled',
          information: appointment.information || '',
          newPrescriptions: [],
          newContraindications: '',
        }
      } catch (error) {
        console.error('Error loading appointment details:', error)

        appointmentMedicaments.value = []
        allPatientMedicaments.value = []
        patientOtherContraindications.value = []
        medicamentInteractions.value = []
        editForm.value = {
          status: appointment.status || 'scheduled',
          information: appointment.information || '',
          newPrescriptions: [],
          newContraindications: '',
        }
      } finally {
        isLoadingDetails.value = false
      }
    }

    const closeEditModal = () => {
      showEditModal.value = false
      currentAppointment.value = null
      patientOtherContraindications.value = []
      appointmentMedicaments.value = []
      allPatientMedicaments.value = []
      medicamentInteractions.value = []
      showAllPatientMeds.value = false
      isSaving.value = false
      editForm.value = {
        status: '',
        information: '',
        newPrescriptions: [],
        newContraindications: '',
      }
    }

    const confirmDeleteMedicament = (med) => {
      medicamentToDelete.value = med
      showDeleteMedicamentModal.value = true
    }

    const closeDeleteMedicamentModal = () => {
      showDeleteMedicamentModal.value = false
      medicamentToDelete.value = null
    }

    const deleteMedicament = async () => {
      if (!medicamentToDelete.value) return

      isDeletingMedicament.value = true

      try {
        await deletePatientMedicament(medicamentToDelete.value.id)

        appointmentMedicaments.value = appointmentMedicaments.value.filter(
            m => m.id !== medicamentToDelete.value.id
        )

        allPatientMedicaments.value = allPatientMedicaments.value.filter(
            m => m.id !== medicamentToDelete.value.id
        )

        closeDeleteMedicamentModal()
      } catch (error) {
        console.error('Error deleting medicament:', error)
        alert('Failed to delete medicament: ' + (error.response?.data?.detail || error.message))
      } finally {
        isDeletingMedicament.value = false
      }
    }

    const saveAppointment = async () => {
      if (!currentAppointment.value || isSaving.value) return

      // Check for conflicts
      if (hasAnyConflicts.value) {
        alert('❌ Cannot save!\n\nPlease resolve all drug conflicts before saving.')
        return
      }

      if (validationErrors.value.length > 0) {
        alert(
            '❌ Cannot save!\n\n' +
            '🟡 Validation errors:\n\n' +
            '• ' + validationErrors.value.join('\n• ') +
            '\n\n📋 Fix errors before saving.'
        )
        return
      }

      const prescriptionsWithMeds = editForm.value.newPrescriptions.filter(p => p.medicament_id)

      for (let i = 0; i < prescriptionsWithMeds.length; i++) {
        const p = prescriptionsWithMeds[i]
        const medName = getMedicamentName(parseInt(p.medicament_id))

        if (!p.end_date) {
          alert(`❌ Cannot save!\n\n🔴 Prescription "${medName}":\n\nEnd date is REQUIRED.`)
          return
        }

        if (!p.start_date) {
          alert(`❌ Cannot save!\n\n🔴 Prescription "${medName}":\n\nStart date is REQUIRED.`)
          return
        }

        if (p.start_date > p.end_date) {
          alert(`❌ Cannot save!\n\n🔴 Prescription "${medName}":\n\nEnd date must be after or equal to start date.`)
          return
        }
      }

      isSaving.value = true

      try {
        await updateAppointmentStatus(currentAppointment.value.id, {
          status: editForm.value.status,
          information: editForm.value.information,
        })

        const validNewPrescriptions = editForm.value.newPrescriptions.filter(
            p => p.medicament_id && p.start_date && p.end_date
        )

        let successCount = 0
        let errorMessages = []

        for (const prescription of validNewPrescriptions) {
          const prescriptionData = {
            medicament_id: prescription.medicament_id,
            dosage: prescription.dosage || '',
            frequency: prescription.frequency || '',
            start_date: prescription.start_date,
            end_date: prescription.end_date,
            notes: prescription.notes || '',
          }

          try {
            await addMedicamentsForAppointment(currentAppointment.value.id, prescriptionData)
            successCount++
          } catch (error) {
            console.error('Error adding medicament:', error)
            const medName = getMedicamentName(parseInt(prescription.medicament_id))
            errorMessages.push(`${medName}: ${error.response?.data?.detail || error.message}`)
          }
        }

        if (editForm.value.newContraindications && editForm.value.newContraindications.trim()) {
          const contraindications = editForm.value.newContraindications
              .split(',')
              .map(c => c.trim())
              .filter(c => c.length > 0)

          if (contraindications.length > 0) {
            try {
              await addPatientContraindications(
                  currentAppointment.value.patient.id,
                  contraindications
              )
            } catch (error) {
              console.error('Error adding contraindications:', error)
              errorMessages.push(`Contraindications: ${error.response?.data?.detail || error.message}`)
            }
          }
        }

        myAppointments.value = (await getDoctorAppointments()) || []

        if (errorMessages.length > 0) {
          alert(
              `⚠️ Appointment saved with warnings:\n\n` +
              `✅ Successfully added prescriptions: ${successCount}\n` +
              `❌ Errors:\n• ${errorMessages.join('\n• ')}`
          )
        } else {
          alert('✅ Appointment saved successfully!')
        }

        closeEditModal()

      } catch (error) {
        console.error('Error updating appointment:', error)
        alert('❌ Save error!\n\n' + (error.response?.data?.detail || error.message))
      } finally {
        isSaving.value = false
      }
    }

    const loadData = async () => {
      isLoading.value = true
      try {
        const [appointments, medicaments] = await Promise.all([
          getDoctorAppointments(),
          getAllMedicaments()
        ])
        myAppointments.value = appointments || []
        allMedicaments.value = medicaments || []
      } catch (error) {
        console.error('Error loading data:', error)
      } finally {
        isLoading.value = false
      }
    }

    onMounted(async () => {
      await loadData()
    })

    return {
      activeFilter,
      filters,
      filteredAppointments,
      allMedicaments,
      patientOtherContraindications,
      appointmentMedicaments,
      allPatientMedicaments,
      showAllPatientMeds,
      currentAppointment,
      isLoading,
      isLoadingDetails,
      isSaving,
      isDeletingMedicament,
      isDeletingContraindication,
      showEditModal,
      showDeleteMedicamentModal,
      showDeleteContraindicationModal,
      medicamentToDelete,
      contraindicationToDelete,
      editForm,
      validationErrors,
      hasAnyConflicts,
      getInitials,
      formatPatientName,
      formatDate,
      getStatusClass,
      capitalizeStatus,
      getMedicamentStatus,
      getMedicamentStatusClass,
      getMedicamentBadgeClass,
      getPrescriptionConflicts,
      openEditModal,
      closeEditModal,
      saveAppointment,
      addNewPrescription,
      removeNewPrescription,
      onMedicamentSelect,
      confirmDeleteMedicament,
      closeDeleteMedicamentModal,
      deleteMedicament,
      confirmDeleteContraindication,
      closeDeleteContraindicationModal,
      deleteContraindication,
    }
  },
}
</script>