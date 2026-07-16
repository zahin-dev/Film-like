import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authStore'

function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/', { replace: true })
  }

  const initials = [user?.first_name, user?.last_name]
    .filter(Boolean)
    .map((name) => name[0])
    .join('') || 'FL'

  return (
    <div className="profile-page page-stack">
      <section className="profile-hero">
        <div className="profile-avatar" aria-hidden="true">{initials}</div>
        <div>
          <p className="eyebrow light">Viewer profile</p>
          <h1>{user?.username || 'Film-like viewer'}</h1>
          <p>Your account keeps the diary personal and recommendations tied to your own reactions.</p>
        </div>
      </section>

      <section className="profile-grid" aria-labelledby="profile-details-heading">
        <div className="profile-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Account</p>
              <h2 id="profile-details-heading">Profile details</h2>
            </div>
          </div>
          <dl className="profile-details">
            <div><dt>First name</dt><dd>{user?.first_name || 'Unavailable'}</dd></div>
            <div><dt>Last name</dt><dd>{user?.last_name || 'Unavailable'}</dd></div>
            <div><dt>Email</dt><dd>{user?.email || 'Unavailable'}</dd></div>
            <div><dt>Age</dt><dd>{user?.age || 'Not provided'}</dd></div>
          </dl>
          <p className="field-hint">Profile editing is not part of the current backend API.</p>
        </div>

        <aside className="profile-card session-card" aria-labelledby="session-heading">
          <p className="eyebrow">Session</p>
          <h2 id="session-heading">Signed in on this device</h2>
          <p className="muted">Logging out clears the access token and profile snapshot from session storage.</p>
          <button className="button danger full" type="button" onClick={handleLogout}>Log out of Film-like</button>
        </aside>
      </section>
    </div>
  )
}

export default ProfilePage
