import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authStore'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'

function AuthPage() {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({
    firstName: '',
    lastName: '',
    age: '',
    email: '',
    password: '',
  })
  const [error, setError] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const { login } = useAuth()

  function updateField(event) {
    setForm((current) => ({ ...current, [event.target.name]: event.target.value }))
  }

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSubmitting(true)
    try {
      if (mode === 'register') {
        await api.post('/auth/register', {
          first_name: form.firstName.trim(),
          last_name: form.lastName.trim(),
          email: form.email.trim(),
          password: form.password,
          age: form.age ? Number.parseInt(form.age, 10) : null,
        })
      }
      await login(form.email.trim(), form.password)
      const destination = location.state?.from?.pathname || '/dashboard'
      navigate(destination, { replace: true })
    } catch (requestError) {
      setError(getApiError(requestError, 'Authentication failed.'))
    } finally {
      setSubmitting(false)
    }
  }

  function toggleMode() {
    setMode((current) => current === 'login' ? 'register' : 'login')
    setError('')
  }

  const isLogin = mode === 'login'

  return (
    <main className="auth-page">
      <section className="auth-story" aria-labelledby="brand-heading">
        <div className="auth-brand">
          <span className="brand-mark large" aria-hidden="true">F</span>
          <span>Film-like</span>
        </div>
        <p className="eyebrow light">Your taste, in motion</p>
        <h1 id="brand-heading">A film diary that understands the mood you are in.</h1>
        <p>
          Search the TMDB catalog, keep a personal viewing history, and turn
          your reactions into verified recommendations powered by Mistral AI.
        </p>
        <div className="auth-proof" aria-label="Product features">
          <span>Personal diary</span>
          <span>Mood-led discovery</span>
          <span>TMDB verified</span>
        </div>
      </section>

      <section className="auth-form-panel" aria-labelledby="auth-heading">
        <div className="auth-form-wrap">
          <p className="eyebrow">{isLogin ? 'Welcome back' : 'Start your diary'}</p>
          <h2 id="auth-heading">{isLogin ? 'Sign in to Film-like' : 'Create your account'}</h2>
          <p className="muted">
            {isLogin
              ? 'Continue where your last film left off.'
              : 'A few details, then your next great film.'}
          </p>

          <form className="form-stack" onSubmit={handleSubmit}>
            {!isLogin && (
              <div className="form-grid two-column">
                <label>
                  First name
                  <input name="firstName" value={form.firstName} onChange={updateField} autoComplete="given-name" required />
                </label>
                <label>
                  Last name
                  <input name="lastName" value={form.lastName} onChange={updateField} autoComplete="family-name" required />
                </label>
              </div>
            )}

            {!isLogin && (
              <label>
                Age <span className="optional">Optional</span>
                <input name="age" type="number" min="1" max="120" value={form.age} onChange={updateField} inputMode="numeric" />
              </label>
            )}

            <label>
              Email address
              <input name="email" type="email" value={form.email} onChange={updateField} autoComplete="email" required />
            </label>

            <label>
              Password
              <input name="password" type="password" minLength="8" maxLength="64" value={form.password} onChange={updateField} autoComplete={isLogin ? 'current-password' : 'new-password'} required />
              {!isLogin && <span className="field-hint">8–64 characters with a number and symbol.</span>}
            </label>

            {error && <p className="inline-alert" role="alert">{error}</p>}

            <button className="button primary full" type="submit" disabled={submitting}>
              {submitting ? 'Please wait…' : isLogin ? 'Sign in' : 'Create account'}
            </button>
          </form>

          <p className="auth-switch">
            {isLogin ? 'New to Film-like?' : 'Already have an account?'}{' '}
            <button type="button" className="text-button" onClick={toggleMode}>
              {isLogin ? 'Create one' : 'Sign in'}
            </button>
          </p>
        </div>
      </section>
    </main>
  )
}

export default AuthPage
