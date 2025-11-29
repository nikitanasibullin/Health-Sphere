<template>
  <header v-if="user" class="bg-white shadow-lg sticky top-0 z-40">
    <div class="container mx-auto px-6 py-4">
      <div class="flex justify-between items-center">
        <!-- Logo -->
        <div class="flex items-center">
          <div class="p-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg mr-3">
            <i class="fas fa-hospital text-2xl text-white"></i>
          </div>
          <div>
            <h1 class="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              HealthSphere
            </h1>
            <p class="text-xs text-gray-500">Advanced Hospital Management</p>
          </div>
        </div>
        
        <div class="flex items-center space-x-4">
          
          <!-- User Profile -->
          <div class="flex items-center space-x-3 bg-gradient-to-r from-blue-50 to-purple-50 px-4 py-2 rounded-lg">
            <div class="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
              <i :class="[userIcon, 'text-white']"></i>
            </div>
            <div class="text-right">
              <p class="text-sm font-semibold text-gray-800">{{ userName }}</p>
              <p class="text-xs text-gray-500 capitalize">{{ userRole }}</p>
            </div>
          </div>
          
          <!-- Logout Button -->
          <button 
            @click="$emit('logout')" 
            class="bg-gradient-to-r from-red-500 to-pink-500 text-white px-4 py-2 rounded-lg hover:from-red-600 hover:to-pink-600 transition shadow-md"
          >
            <i class="fas fa-sign-out-alt mr-2"></i>Logout
          </button>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'AppHeader',
  props: {
    user: {
      type: Object,
      default: null
    }
  },
  emits: ['logout', 'notification-click', 'clear-notifications'],
  setup(props) {
    
    // Safe computed properties with null checks
    const userName = computed(() => {
      return props.user?.name || 'User'
    })
    
    const userRole = computed(() => {
      return props.user?.role || 'guest'
    })
    
    const userIcon = computed(() => {
      if (!props.user?.role) return 'fas fa-user'
      
      const icons = {
        admin: 'fas fa-user-shield',
        doctor: 'fas fa-user-md',
        patient: 'fas fa-user'
      }
      return icons[props.user.role] || 'fas fa-user'
    })
    
    return {
      userName,
      userRole,
      userIcon
    }
  }
}
</script>