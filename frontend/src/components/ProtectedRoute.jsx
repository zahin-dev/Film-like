import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/authStore'

export function ProtectedRoute() {
  const { isAuthenticated } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/" replace state={{ from: location }} />
  }
  return <Outlet />
}

export function PublicOnlyRoute({ children }) {
  const { isAuthenticated } = useAuth()
  return isAuthenticated ? <Navigate to="/dashboard" replace /> : children
}
