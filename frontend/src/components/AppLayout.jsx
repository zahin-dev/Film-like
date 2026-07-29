import { NavLink, Outlet, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/authStore'

const links = [
  { to: '/dashboard', label: '映画日記' },
  { to: '/catalog', label: '映画を探す' },
  { to: '/recommendations', label: 'おすすめ' },
  { to: '/profile', label: 'プロフィール' },
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
        <NavLink to="/dashboard" className="brand" aria-label="Film-like ホーム">
          <span className="brand-mark" aria-hidden="true">F</span>
          <span>Film-like</span>
        </NavLink>

        <nav className="main-nav" aria-label="メインナビゲーション">
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
          <span className="header-user" title={user?.email || 'ログイン中'}>
            {user?.first_name || 'ユーザー'}
          </span>
          <button className="button ghost compact" type="button" onClick={handleLogout}>
            ログアウト
          </button>
        </div>
      </header>

      <main className="page-container">
        <Outlet />
      </main>

      <footer className="site-footer">
        <span>Film-like</span>
        <span>ローカル映画カタログ · APIキー不要のおすすめ</span>
      </footer>
    </div>
  )
}

export default AppLayout
