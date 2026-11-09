import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import { useAuth } from './context/authStore'

export default function App() {
  const { isAuthenticated } = useAuth()
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <AuthPage />} />
        <Route path="/dashboard" element={isAuthenticated ? <DashboardPage /> : <Navigate to="/" replace />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <footer aria-label="About Film-like" className="mx-auto max-w-4xl space-y-2 px-4 py-6 text-center text-sm text-slate-600">
        <p>About Film-like</p>
        <a href="https://www.themoviedb.org" className="inline-block">
          <img src="/tmdb-logo.svg" alt="The Movie Database" width="92" />
        </a>
        <p>This product uses the TMDB API but is not endorsed or certified by TMDB.</p>
      </footer>
    </BrowserRouter>
  )
}
