// components/http.js
import axios from 'axios'

const http = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor для добавления токена
http.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor для обработки ошибок
http.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const currentPath = window.location.pathname

      if (!currentPath.includes('/login') && !currentPath.includes('/register')) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user_type')
      }
    }
    return Promise.reject(error)
  }
)

export default http
