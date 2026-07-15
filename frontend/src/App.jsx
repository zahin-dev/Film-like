import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppLayout from './components/AppLayout'
import { ProtectedRoute, PublicOnlyRoute } from './components/ProtectedRoute'
import AuthPage from './pages/AuthPage'
import DashboardPage from './pages/DashboardPage'
import CatalogPage from './pages/CatalogPage'
import FilmDetailPage from './pages/FilmDetailPage'
import RecommendationPage from './pages/RecommendationPage'
import ProfilePage from './pages/ProfilePage'

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<PublicOnlyRoute><AuthPage /></PublicOnlyRoute>} />
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/catalog" element={<CatalogPage />} />
            <Route path="/films/:tmdbId" element={<FilmDetailPage />} />
            <Route path="/recommendations" element={<RecommendationPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Route>
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
