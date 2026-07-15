import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

// Inject the JWT into every API request from one central location.
api.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Clear the local session when the backend rejects an expired or invalid JWT.
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      sessionStorage.removeItem('token')
      sessionStorage.removeItem('user')
      window.location.href = '/'
    }
    return Promise.reject(error)
  }
)

export default api
