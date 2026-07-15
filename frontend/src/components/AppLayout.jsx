import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/authStore'

const links = [
  { to: '/dashboard', label: 'Diary' },
  { to: '/catalog', label: 'Catalog' },
  { to: '/recommendations', label: 'For you' },
  { to: '/profile', label: 'Profile' },
]

function AppLayout() {
  const { logout, user } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  return (
    <div className="app-shell">
      <header className="site-header">
        <NavLink to="/dashboard" className="brand" aria-label="Film-like home">
          <span className="brand-mark" aria-hidden="true">F</span>
          <span>Film-like</span>
        </NavLink>

        <nav className="main-nav" aria-label="Primary navigation">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="header-actions">
          <span className="header-user" title={user?.email || 'Signed in'}>
            {user?.first_name || 'Viewer'}
          </span>
          <button className="button ghost compact" type="button" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </header>

      <main className="page-container">
        <Outlet />
      </main>

      <footer className="site-footer">
        <span>Film-like</span>
        <span>Films from TMDB · Recommendations verified before display</span>
      </footer>
    </div>
  )
}

export default AppLayout
