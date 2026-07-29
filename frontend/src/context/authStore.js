import { createContext, useContext } from 'react'

const AuthContext = createContext(null)

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuthはAuthProvider内で使用してください')
  }
  return context
}

export default AuthContext
