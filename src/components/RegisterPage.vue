<template>
  <div class="min-h-screen flex items-center justify-center gradient-bg-3 relative py-8">
    <!-- Background decorations -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div
        class="absolute -top-40 -right-40 w-80 h-80 bg-blue-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"
      ></div>
      <div
        class="absolute -bottom-40 -left-40 w-80 h-80 bg-cyan-300 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-pulse"
      ></div>
    </div>

    <!-- Register Card -->
    <div
      class="bg-white p-10 rounded-2xl shadow-2xl w-full max-w-lg relative z-10 animate-fadeIn mx-4"
    >
      <!-- Header -->
      <div class="text-center mb-8">
        <div class="inline-block p-4 bg-gradient-to-r from-cyan-500 to-blue-600 rounded-full mb-4">
          <i class="fas fa-user-plus text-5xl text-white"></i>
        </div>
        <h1
          class="text-4xl font-bold bg-gradient-to-r from-cyan-600 to-blue-600 bg-clip-text text-transparent"
        >
          Create Account
        </h1>
        <p class="text-gray-600 mt-2">Join HealthSphere Today</p>
      </div>

      <!-- Form -->
      <form @submit.prevent="register">
        <!-- Full Name -->
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-user mr-2 text-cyan-500"></i>First Name
          </label>
          <input
            v-model="registerForm.firstName"
            type="text"
            required
            placeholder="First Name"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          />
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-user mr-2 text-cyan-500"></i>Last Name
          </label>
          <input
            v-model="registerForm.lastName"
            type="text"
            required
            placeholder="Last Name"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          />
        </div>
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-user mr-2 text-cyan-500"></i>Patronymic
          </label>
          <input
            v-model="registerForm.patronymic"
            type="text"
            required
            placeholder="Patronymic"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
          />
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
          />
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
          />
        </div>

        <!-- Birth Date and Gender Row -->
        <div class="grid grid-cols-2 gap-4 mb-4">
          <!-- Birth Date -->
          <div>
            <label class="block text-gray-700 text-sm font-bold mb-2">
              <i class="fas fa-calendar-alt mr-2 text-cyan-500"></i>Birth Date
            </label>
            <input
              v-model="registerForm.birthDate"
              type="date"
              required
              :max="maxDate"
              :min="minDate"
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200"
            />
          </div>

          <!-- Gender -->
          <div>
            <label class="block text-gray-700 text-sm font-bold mb-2">
              <i class="fas fa-venus-mars mr-2 text-cyan-500"></i>Gender
            </label>
            <select
              v-model="registerForm.gender"
              required
              class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200 bg-white"
            >
              <option value="" disabled>Select gender</option>
              <option value="male">Male</option>
              <option value="female">Female</option>
            </select>
          </div>
        </div>

        <!-- Passport Data -->
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-id-card mr-2 text-cyan-500"></i>Passport Series & Number
          </label>
          <div class="grid grid-cols-1 gap-3">
            <div>
              <input
                v-model="registerForm.passportNumber"
                type="text"
                required
                maxlength="10"
                placeholder="Series (4 digits) & Number (6 digits)"
                @input="validatePassportNumber"
                :class="[
                  'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200',
                  passportNumberError ? 'border-red-400 bg-red-50' : 'border-gray-300',
                ]"
              />
              <p v-if="passportNumberError" class="text-red-500 text-xs mt-1">
                {{ passportNumberError }}
              </p>
            </div>
          </div>
        </div>

        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-id-card mr-2 text-cyan-500"></i>Insurance number
          </label>
          <div class="grid grid-cols-1 gap-3">
            <div>
              <input
                v-model="registerForm.insuranceNumber"
                type="text"
                required
                maxlength="16"
                placeholder="Number (16 digits)"
                @input="validateInsuranceNumber"
                :class="[
                  'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200',
                  insuranceNumberError ? 'border-red-400 bg-red-50' : 'border-gray-300',
                ]"
              />
              <p v-if="insuranceNumberError" class="text-red-500 text-xs mt-1">
                {{ insuranceNumberError }}
              </p>
            </div>
          </div>
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
          />
        </div>

        <!-- Confirm Password -->
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2">
            <i class="fas fa-lock mr-2 text-cyan-500"></i>Confirm Password
          </label>
          <input
            v-model="registerForm.confirmPassword"
            type="password"
            required
            minlength="6"
            placeholder="Repeat your password"
            :class="[
              'w-full px-4 py-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent transition duration-200',
              passwordMismatch ? 'border-red-400 bg-red-50' : 'border-gray-300',
            ]"
          />
          <p v-if="passwordMismatch" class="text-red-500 text-xs mt-1">
            <i class="fas fa-exclamation-circle mr-1"></i>Passwords do not match
          </p>
          <p v-else-if="passwordsMatch" class="text-green-500 text-xs mt-1">
            <i class="fas fa-check-circle mr-1"></i>Passwords match
          </p>
        </div>

        <!-- Submit Button -->
        <button
          type="submit"
          :disabled="!isFormValid"
          :class="[
            'w-full py-3 rounded-lg transition duration-300 font-semibold shadow-lg transform',
            isFormValid
              ? 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white hover:from-cyan-700 hover:to-blue-700 hover:shadow-xl hover:-translate-y-0.5'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed',
          ]"
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
import http from './http.js'
export default {
  name: 'RegisterPage',
  emits: ['navigate'],
  data() {
    return {
      registerForm: {
        firstName: '',
        lastName: '',
        patronymic: '',
        email: '',
        phone: '',
        password: '',
        confirmPassword: '',
        birthDate: '',
        gender: '',
        passportNumber: '',
        insuranceNumber: '',
      },
      insuranceNumberError: '',
      passportNumberError: '',
      registerError: '',
      registerSuccess: '',
    }
  },
  computed: {
    maxDate() {
      const today = new Date()
      today.setFullYear(today.getFullYear() - 1)
      return today.toISOString().split('T')[0]
    },
    minDate() {
      const today = new Date()
      today.setFullYear(today.getFullYear() - 120)
      return today.toISOString().split('T')[0]
    },
    passwordMismatch() {
      return (
        this.registerForm.confirmPassword.length > 0 &&
        this.registerForm.password !== this.registerForm.confirmPassword
      )
    },
    passwordsMatch() {
      return (
        this.registerForm.password.length >= 6 &&
        this.registerForm.confirmPassword.length >= 6 &&
        this.registerForm.password === this.registerForm.confirmPassword
      )
    },
    isPassportValid() {
      return (
        this.registerForm.passportNumber.length === 10 &&
        /^\d{10}$/.test(this.registerForm.passportNumber)
      )
    },

    isInsuranceValid() {
      return (
        this.registerForm.insuranceNumber.length === 16 &&
        /^\d{16}$/.test(this.registerForm.insuranceNumber)
      )
    },
    isFormValid() {
      return (
        this.registerForm.firstName &&
        this.registerForm.lastName &&
        this.registerForm.patronymic &&
        this.registerForm.email &&
        this.registerForm.phone &&
        this.registerForm.birthDate &&
        this.registerForm.gender &&
        this.registerForm.password.length >= 6 &&
        this.passwordsMatch &&
        this.isPassportValid &&
        this.isInsuranceValid &&
        !this.passportNumberError &&
        !this.insuranceNumberError
      )
    },
  },
  methods: {
    validatePassportNumber() {
      this.registerForm.passportNumber = this.registerForm.passportNumber.replace(/\D/g, '')

      if (
        this.registerForm.passportNumber.length > 0 &&
        this.registerForm.passportNumber.length < 10
      ) {
        this.passportNumberError = 'Must be 10 digits'
      } else {
        this.passportNumberError = ''
      }
    },
    validateInsuranceNumber() {
      this.registerForm.insuranceNumber = this.registerForm.insuranceNumber.replace(/\D/g, '')

      if (
        this.registerForm.insuranceNumber.length > 0 &&
        this.registerForm.insuranceNumber.length < 16
      ) {
        this.insuranceNumberError = 'Must be 16 digits'
      } else {
        this.insuranceNumberError = ''
      }
    },
    async register() {
      console.log('Registering:', this.registerForm)

      if (
        !this.registerForm.firstName ||
        !this.registerForm.lastName ||
        !this.registerForm.patronymic ||
        !this.registerForm.email ||
        !this.registerForm.phone ||
        !this.registerForm.password
      ) {
        this.registerError = 'Please fill in all required fields'
        return
      }

      if (!this.registerForm.birthDate) {
        this.registerError = 'Please select your birth date'
        return
      }

      if (!this.registerForm.gender) {
        this.registerError = 'Please select your gender'
        return
      }

      if (!this.isPassportValid) {
        this.registerError = 'Please enter valid passport data (4-digit series and 6-digit number)'
        return
      }

      if (this.registerForm.password !== this.registerForm.confirmPassword) {
        this.registerError = 'Passwords do not match'
        return
      }

      if (this.registerForm.password.length < 6) {
        this.registerError = 'Password must be at least 6 characters'
        return
      }

      this.registerError = ''

      const dataToSend = {
        first_name: this.registerForm.firstName,
        last_name: this.registerForm.lastName,
        patronymic: this.registerForm.patronymic,
        gender: this.registerForm.gender,
        passport_number: this.registerForm.passportNumber,
        insurance_number: this.registerForm.insuranceNumber,
        birth_date: this.registerForm.birthDate,
        phone_number: this.registerForm.phone,
        email: this.registerForm.email,
        password: this.registerForm.password,
      }

      try {
        const response = await http.post('/api/patient/register', JSON.stringify(dataToSend))

        if (response.status === 200 || response.status === 201) {
          this.registerError = ''
          this.registerSuccess = 'Account created successfully! Now you can login...'
          alert('Account created successfully!')
        }
      } catch (error) {
        this.registerError = 'Something went wrong'
        this.registerSuccess = ''
        console.error(error)
      }
    }
  }
}
</script>
