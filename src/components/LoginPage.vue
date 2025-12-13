<template>
  <div class="min-h-screen flex items-center justify-center gradient-bg relative overflow-hidden">
    <!-- Background -->
    <div
      class="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"
    ></div>
    <div
      class="absolute -bottom-40 -left-40 w-80 h-80 bg-yellow-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"
    ></div>

    <!-- Login Card -->
    <div
      class="bg-white p-8 rounded-2xl shadow-2xl w-full max-w-md relative z-10 animate-fadeIn mx-4"
    >
      <div class="text-center mb-8">
        <div
          class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full mb-4"
        >
          <i class="fas fa-hospital text-4xl text-white"></i>
        </div>
        <h1
          class="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent"
        >
          HealthSphere
        </h1>
        <p class="text-gray-600 mt-2">Your Health, Our Priority</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-envelope mr-2 text-blue-500"></i>Email
          </label>
          <input
            v-model="form.email"
            type="email"
            required
            placeholder="Enter your email"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
          />
        </div>

        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-lock mr-2 text-blue-500"></i>Password
          </label>
          <input
            v-model="form.password"
            type="password"
            required
            placeholder="Enter your password"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 transition"
          />
        </div>

        <button
          type="submit"
          class="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition font-semibold shadow-lg"
        >
          <i class="fas fa-sign-in-alt mr-2"></i>Sign In
        </button>
      </form>

      <div class="mt-6 text-center">
        <p class="text-gray-600 text-sm">Don't have an account?</p>
        <!-- Use router-link instead of @click -->
        <router-link
          to="/register"
          class="text-blue-600 hover:text-blue-800 font-semibold mt-2 inline-block"
        >
          Register Now <i class="fas fa-arrow-right ml-1"></i>
        </router-link>
      </div>

      <!-- Demo Accounts -->
      <div class="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg text-xs">
        <p class="font-bold mb-2 text-gray-700">Demo Accounts (click to fill):</p>
        <p @click="fillDemo('admin')" class="text-gray-600 cursor-pointer hover:text-blue-600">
          <strong>Admin:</strong> admin@hospital.com / admin123
        </p>
        <p @click="fillDemo('doctor')" class="text-gray-600 cursor-pointer hover:text-blue-600">
          <strong>Doctor:</strong> doctor@hospital.com / doctor123
        </p>
        <p @click="fillDemo('patient')" class="text-gray-600 cursor-pointer hover:text-blue-600">
          <strong>Patient:</strong> patient@hospital.com / patient123
        </p>
      </div>

      <div
        v-if="error"
        class="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded-lg text-sm"
      >
        <i class="fas fa-exclamation-circle mr-2"></i>{{ error }}
      </div>
    </div>
  </div>
</template>

<script>

import { useHospitalData } from '../composables/useHospitalData'
export default {
  name: 'LoginPage',
  data() {
    return {
      form: {
        email: '',
        password: '',
      },
      error: '',
      // Demo users database
      demoUsers: {
        'admin@hospital.com': { password: 'admin123', name: 'Admin User', role: 'admin' },
        'doctor@hospital.com': { password: 'doctor123', name: 'Dr. John Smith', role: 'doctor' },
        'patient@hospital.com': { password: 'patient123', name: 'Jane Doe', role: 'patient' },
      },
    }
  },
  methods: {
    async handleLogin() {
      const { login } = useHospitalData()
      const response = await login(this.form.email, this.form.password)
      console.log(response)
      const currentUser = {
        email: this.form.email,
        name: this.form.email,
        role: response.data.user_type,
      }
      if (response.status === 200) {
        localStorage.setItem('currentUser', JSON.stringify(currentUser))
        this.error = ''
        this.$router.push(`/${response.data.user_type}`)
      } else {
        alert('Validation Error')
        this.error = 'Validation Error'
        console.log('error', response.status)
      }
    },

    fillDemo(role) {
      const demos = {
        admin: { email: 'admin@hospital.com', password: 'admin123' },
        doctor: { email: 'doctor@hospital.com', password: 'doctor123' },
        patient: { email: 'patient@hospital.com', password: 'patient123' },
      }
      this.form.email = demos[role].email
      this.form.password = demos[role].password
    },
  },
}
</script>
