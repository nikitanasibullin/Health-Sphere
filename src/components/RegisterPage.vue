<template>
  <div class="min-h-screen flex items-center justify-center gradient-bg-3 relative py-8">
    <!-- Background decorations -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"></div>
    </div>
    
    <!-- Register Card -->
    <div class="bg-white p-10 rounded-2xl shadow-2xl w-full max-w-lg relative z-10 animate-fadeIn mx-4">
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-block p-4 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full mb-4">
          <i class="fas fa-user-plus text-5xl text-white"></i>
        </div>
        <h1 class="text-4xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent">
          Create Account
        </h1>
        <p class="text-gray-600 mt-2">Join HealthSphere Today</p>
      </div>
      
      <!-- Form -->
      <form @submit.prevent="register">
        <!-- Full Name -->
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-user mr-2 text-cyan-500"></i>Full Name
          </label>
          <input 
            v-model="registerForm.name" 
            type="text" 
            required
            placeholder="Enter your full name"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          >
        </div>
        
        <!-- Email -->
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-envelope mr-2 text-cyan-500"></i>Email
          </label>
          <input 
            v-model="registerForm.email" 
            type="email" 
            required
            placeholder="Enter your email"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          >
        </div>
        
        <!-- Phone -->
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-phone mr-2 text-cyan-500"></i>Phone Number
          </label>
          <input 
            v-model="registerForm.phone" 
            type="tel" 
            required
            placeholder="Enter your phone number"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          >
        </div>
        
        <!-- Password -->
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-lock mr-2 text-cyan-500"></i>Password
          </label>
          <input 
            v-model="registerForm.password" 
            type="password" 
            required 
            minlength="6"
            placeholder="Enter your password (min 6 characters)"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          >
        </div>
        
        <!-- Role Selection -->
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-user-tag mr-2 text-cyan-500">
            </i>
            Register as
          </label>
          <div class="grid grid-cols-2 gap-3">
            <button type="button" @click="registerForm.role = 'patient'" :class="['p-4 rounded-lg border-2 transition duration-300', 
            registerForm.role === 'patient' 
            ? 'border-cyan-500 bg-cyan-50' 
            : 'border-gray-300 hover:border-cyan-300']">
              <i class="fas fa-user-injured text-3xl mb-2" :class="registerForm.role === 'patient' ? 'text-cyan-500' : 'text-gray-400'">
              </i>
              <p class="font-semibold" :class="registerForm.role === 'patient' ? 'text-cyan-700' : 'text-gray-700'">
                Patient
              </p>
            </button>
            <button type="button" @click="registerForm.role = 'doctor'" :class="['p-4 rounded-lg border-2 transition duration-300', 
            registerForm.role === 'doctor' 
            ? 'border-cyan-500 bg-cyan-50' 
            : 'border-gray-300 hover:border-cyan-300']">
              <i class="fas fa-user-md text-3xl mb-2" :class="registerForm.role === 'doctor' ? 'text-cyan-500' : 'text-gray-400'">
              </i>
              <p class="font-semibold" :class="registerForm.role === 'doctor' ? 'text-cyan-700' : 'text-gray-700'">
                Doctor
              </p>
            </button>
          </div>
        </div>
        <!-- Doctor Specialization -->
        <div v-if="registerForm.role === 'doctor'" class="mb-4 animate-fadeIn">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-stethoscope mr-2 text-cyan-500"></i>Specialization
          </label>
          <select 
            v-model="registerForm.specialization" 
            required
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          >
            <option value="">Select specialization...</option>
            <option value="Cardiology">Cardiology</option>
            <option value="Neurology">Neurology</option>
            <option value="Pediatrics">Pediatrics</option>
            <option value="Orthopedics">Orthopedics</option>
            <option value="Dermatology">Dermatology</option>
            <option value="General Practice">General Practice</option>
          </select>
        </div>
        
        <!-- Patient Age -->
        <div v-if="registerForm.role === 'patient'" class="mb-4 animate-fadeIn">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-birthday-cake mr-2 text-cyan-500"></i>Age
          </label>
          <input 
            v-model="registerForm.age" 
            type="number" 
            required 
            min="1" 
            max="120"
            placeholder="Enter your age"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          >
        </div>
        
        <!-- Submit Button -->
        <button 
          type="submit" 
          class="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white py-3 rounded-lg hover:from-cyan-700 hover:to-blue-700 transition duration-300 font-semibold shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
        >
          <i class="fas fa-user-plus mr-2"></i>Create Account
        </button>
      </form>
      
      <!-- Login Link -->
      <div class="mt-6 text-center">
        <p class="text-gray-600 text-sm">Already have an account?</p>
        <router-link 
          to="/login" 
          class="text-cyan-600 hover:text-cyan-800 font-semibold mt-2 inline-block transition duration-200"
        >
          Sign In <i class="fas fa-arrow-right ml-1"></i>
        </router-link>
      </div>
      
      <!-- Error Message -->
      <div 
        v-if="registerError" 
        class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm animate-fadeIn"
      >
        <i class="fas fa-exclamation-circle mr-2"></i>{{ registerError }}
      </div>
      
      <!-- Success Message -->
      <div 
        v-if="registerSuccess" 
        class="mt-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded-lg text-sm animate-fadeIn"
      >
        <i class="fas fa-check-circle mr-2"></i>{{ registerSuccess }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegisterPage',
  emits: ['navigate'],
  data() {
    return {
      registerForm: {
        name: '',
        email: '',
        phone: '',
        password: '',
        role: 'patient',
        specialization: '',
        age: ''
      },
      registerError: '',
      registerSuccess: ''
    }
  },
  methods: {
    register() {
      console.log('Registering:', this.registerForm);
      
      // Basic validation
      if (!this.registerForm.name || !this.registerForm.email || 
          !this.registerForm.phone || !this.registerForm.password) {
        this.registerError = 'Please fill in all required fields';
        return;
      }
      
      if (this.registerForm.role === 'doctor' && !this.registerForm.specialization) {
        this.registerError = 'Please select a specialization';
        return;
      }
      
      if (this.registerForm.role === 'patient' && !this.registerForm.age) {
        this.registerError = 'Please enter your age';
        return;
      }
      
      this.registerError = '';
      this.registerSuccess = 'Account created successfully! Redirecting to login...';
      
      // Redirect to login after 2 seconds
      setTimeout(() => {
        this.$emit('navigate', 'login');
      }, 2000);
    },
    goToLogin() {
      this.$emit('navigate', 'login');
    }
  }
}
</script>