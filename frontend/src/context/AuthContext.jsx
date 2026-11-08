import { useState } from 'react'
import api from '../services/api'

import { AuthContext } from './authStore'

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(() => sessionStorage.getItem('token'))

  const login = async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    const { user, token } = response.data
    setToken(token)
    setUser(user)
    sessionStorage.setItem('token', token)
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    sessionStorage.removeItem('token')
  }

  const isAuthenticated = !!token

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  )
}
