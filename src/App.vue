<template>
  <div id="app" class="min-h-screen">
    <LoginPage 
      v-if="currentPage === 'login'" 
      @navigate="handleNavigation" 
    />
    <RegisterPage 
      v-else-if="currentPage === 'register'" 
      @navigate="handleNavigation" 
    />
  </div>
</template>

<script>
import LoginPage from './components/LoginPage.vue'
import RegisterPage from './components/RegisterPage.vue'

export default {
  name: 'App',
  components: {
    LoginPage,
    RegisterPage
  },
  data() {
    return {
      currentPage: 'login'
    }
  },
  methods: {
    handleNavigation(page) {
      console.log('Navigating to:', page)
      this.currentPage = page
    }
  }
}
</script>