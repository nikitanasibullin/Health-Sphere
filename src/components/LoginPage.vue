<template>
  <div class="min-h-screen flex items-center justify-center gradient-bg relative">
    <!-- Background decorations -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
    </div>
    
    <!-- Login Card -->
    <div class="bg-white p-10 rounded-2xl shadow-2xl w-full max-w-md relative z-10 animate-fadeIn mx-4">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-block p-4 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-4">
          <i class="fas fa-hospital text-5xl text-white"></i>
        </div>
        <h1 class="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
          MediCare Plus
        </h1>
        <p class="text-gray-600 mt-2">Your Health, Our Priority</p>
      </div>
      
      <!-- Form -->
      <form @submit.prevent="login">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-envelope mr-2 text-blue-500"></i>Email
          </label>
          <input 
            v-model="loginForm.email" 
            type="email" 
            required
            placeholder="Enter your email"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
          >
        </div>
        
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-lock mr-2 text-blue-500"></i>Password
          </label>
          <input 
            v-model="loginForm.password" 
            type="password" 
            required
            placeholder="Enter your password"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition duration-200"
          >
        </div>
        
        <button 
          type="submit" 
          class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition duration-300 font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        >
          <i class="fas fa-sign-in-alt mr-2"></i>Sign In
        </button>
      </form>
      
      <!-- Register Link -->
      <div class="mt-6 text-center">
        <p class="text-gray-600 text-sm">Don't have an account?</p>
        <button 
          @click="goToRegister" 
          type="button"
          class="text-blue-600 hover:text-blue-800 font-semibold mt-2 transition duration-200"
        >
          Register Now <i class="fas fa-arrow-right ml-1"></i>
        </button>
      </div>
      
      <!-- Demo Accounts -->
      <div class="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg text-xs">
        <p class="font-bold mb-2 text-gray-700">Demo Accounts:</p>
        <p class="text-gray-600"><strong>Admin:</strong> admin@hospital.com / admin123</p>
        <p class="text-gray-600"><strong>Doctor:</strong> doctor@hospital.com / doctor123</p>
        <p class="text-gray-600"><strong>Patient:</strong> patient@hospital.com / patient123</p>
      </div>
      
      <!-- Error Message -->
      <div 
        v-if="loginError" 
        class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm animate-fadeIn"
      >
        <i class="fas fa-exclamation-circle mr-2"></i>{{ loginError }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoginPage',
  emits: ['navigate'],
  data() {
    return {
      loginForm: {
        email: '',
        password: ''
      },
      loginError: ''
    }
  },
  methods: {
    login() {
      console.log('Logging in:', this.loginForm);
      // Add your login logic here
      // Example validation:
      if (!this.loginForm.email || !this.loginForm.password) {
        this.loginError = 'Please fill in all fields';
        return;
      }
      this.loginError = '';
      // Proceed with login...
    },
    goToRegister() {
      this.$emit('navigate', 'register');
    }
  }
}
</script>