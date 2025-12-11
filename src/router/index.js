import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../components/LoginPage.vue'
import RegisterPage from '../components/RegisterPage.vue'
import AdminPage from '../components/AdminPage.vue'
import DoctorPage from '../components/DoctorPage.vue'
import PatientPage from '../components/PatientPage.vue'

const routes = [
  {
    path: '/',
    redirect: '/login'
  },
  {
    path: '/login',
    name: 'Login',
    component: LoginPage,
    meta: { requiresGuest: true }  // Only for non-logged users
  },
  {
    path: '/register',
    name: 'Register',
    component: RegisterPage,
    meta: { requiresGuest: true }
  },
  {
    path: '/admin',
    name: 'Admin',
    component: AdminPage,
    meta: { requiresAuth: true, role: 'admin' }  // Requires admin login
  },
  {
    path: '/doctor',
    name: 'Doctor',
    component: DoctorPage,
    meta: { requiresAuth: true, role: 'doctor' }
  },
  {
    path: '/patient',
    name: 'Patient',
    component: PatientPage,
    meta: { requiresAuth: true, role: 'patient' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Navigation Guard - Check auth before each route
router.beforeEach((to, from, next) => {
  // Get user from localStorage
  const userJson = localStorage.getItem('currentUser')
  const currentUser = userJson ? JSON.parse(userJson) : null

  // Route requires authentication
  if (to.meta.requiresAuth) {
    if (!currentUser) {
      // Not logged in - redirect to login
      next('/login')
    } else if (to.meta.role && currentUser.role !== to.meta.role) {
      // Wrong role - redirect to correct dashboard
      next(`/${currentUser.role}`)
    } else {
      // Authorized - proceed
      next()
    }
  }
  // Route is for guests only (login/register)
  else if (to.meta.requiresGuest) {
    if (currentUser) {
      // Already logged in - redirect to dashboard
      next(`/${currentUser.role}`)
    } else {
      next()
    }
  }
  else {
    next()
  }
})

export default router
