<template>
  <div class="animate-fadeIn">
    <div class="bg-white rounded-2xl shadow-lg p-6">
      <!-- Header -->
      <div class="flex justify-between items-center mb-6">
        <h2 class="text-3xl font-bold text-gray-800">
          <i class="fas fa-file-invoice-dollar text-green-500 mr-2"></i>Billing & Invoices
        </h2>
        <button 
          @click="showAddModal = true" 
          class="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-lg hover:from-green-700 hover:to-emerald-700 shadow-lg transition"
        >
          <i class="fas fa-plus mr-2"></i>Create Invoice
        </button>
      </div>
      
      <!-- Stats -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div class="bg-green-50 p-4 rounded-lg">
          <p class="text-green-600 text-sm font-semibold">Total Revenue</p>
          <p class="text-2xl font-bold text-green-700">${{ totalRevenue.toLocaleString() }}</p>
        </div>
        <div class="bg-yellow-50 p-4 rounded-lg">
          <p class="text-yellow-600 text-sm font-semibold">Pending</p>
          <p class="text-2xl font-bold text-yellow-700">${{ pendingAmount.toLocaleString() }}</p>
        </div>
        <div class="bg-blue-50 p-4 rounded-lg">
          <p class="text-blue-600 text-sm font-semibold">This Month</p>
          <p class="text-2xl font-bold text-blue-700">${{ monthlyRevenue.toLocaleString() }}</p>
        </div>
      </div>
      
      <!-- Table -->
      <div class="overflow-x-auto">
        <table class="min-w-full">
          <thead class="bg-gradient-to-r from-green-50 to-emerald-50">
            <tr>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Invoice #</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Patient</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Service</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Amount</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Status</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Date</th>
              <th class="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Actions</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="bill in billings" :key="bill.id" class="hover:bg-gray-50 transition">
              <td class="px-6 py-4 whitespace-nowrap font-semibold text-gray-900">#{{ bill.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ getPatientName(bill.patientId) }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ bill.service }}</td>
              <td class="px-6 py-4 whitespace-nowrap font-bold text-green-600">${{ bill.amount }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="bill.status === 'Paid' 
                  ? 'px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-semibold' 
                  : 'px-3 py-1 bg-yellow-100 text-yellow-800 rounded-full text-sm font-semibold'">
                  {{ bill.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-gray-700">{{ bill.date }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <button @click="printInvoice(bill)" class="text-blue-600 hover:text-blue-800 mr-3" title="Print">
                  <i class="fas fa-print"></i>
                </button>
                <button 
                  v-if="bill.status !== 'Paid'"
                  @click="handleMarkPaid(bill.id)" 
                  class="text-green-600 hover:text-green-800"
                  title="Mark as Paid"
                >
                  <i class="fas fa-check-circle"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Add Invoice Modal -->
    <div 
      v-if="showAddModal" 
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      @click.self="showAddModal = false"
    >
      <div class="bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 animate-fadeIn">
        <div class="flex justify-between items-center mb-6">
          <h3 class="text-2xl font-bold text-gray-800">Create Invoice</h3>
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
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
                <option value="">Select patient...</option>
                <option v-for="patient in patients" :key="patient.id" :value="patient.id">
                  {{ patient.name }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Service</label>
              <input 
                v-model="form.service" 
                type="text" 
                required
                placeholder="e.g., General Checkup"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
              >
            </div>
            <div>
              <label class="block text-gray-700 text-sm font-bold mb-2">Amount ($)</label>
              <input 
                v-model="form.amount" 
                type="number" 
                required
                min="0"
                placeholder="0.00"
                class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
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
              class="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-lg hover:from-green-700 hover:to-emerald-700 transition"
            >
              Create Invoice
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useHospitalData } from '../../composables/useHospitalData'

export default {
  name: 'AdminBilling',
  setup() {
    const { 
      patients, 
      billings, 
      totalRevenue,
      monthlyRevenue,
      getPatientName,
      addBilling,
      markBillingPaid,
      addActivity
    } = useHospitalData()
    
    const showAddModal = ref(false)
    const form = ref({
      patientId: '',
      service: '',
      amount: ''
    })
    
    const pendingAmount = computed(() => {
      return billings.value
        .filter(b => b.status === 'Pending')
        .reduce((sum, b) => sum + b.amount, 0)
    })
    
    const printInvoice = (bill) => {
      alert(`Printing invoice #${bill.id} for ${getPatientName(bill.patientId)}`)
    }
    
    const handleMarkPaid = (id) => {
      markBillingPaid(id)
      addActivity('Payment received', 'fas fa-dollar-sign', 'bg-green-500')
    }
    
    const handleSubmit = () => {
      addBilling({
        patientId: parseInt(form.value.patientId),
        service: form.value.service,
        amount: parseInt(form.value.amount),
        date: new Date().toISOString().split('T')[0]
      })
      addActivity('New invoice created', 'fas fa-file-invoice', 'bg-blue-500')
      showAddModal.value = false
      form.value = { patientId: '', service: '', amount: '' }
    }
    
    return {
      patients,
      billings,
      totalRevenue,
      monthlyRevenue,
      pendingAmount,
      showAddModal,
      form,
      getPatientName,
      printInvoice,
      handleMarkPaid,
      handleSubmit
    }
  }
}
</script>