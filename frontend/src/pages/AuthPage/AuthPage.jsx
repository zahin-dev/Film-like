import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import api from '../../services/api'

/**
 * Parse an Axios error into a human-readable string.
 *
 * FastAPI returns two different error shapes depending on the source:
 *
 *   - Business logic errors (401, 409, 500...):
 *       { "detail": "Email already registered" }        ← string
 *
 *   - Pydantic validation errors (422):
 *       { "detail": [{ "msg": "Value error, ...", "loc": [...] }] }  ← array
 *
 *   - No response at all: network error or backend not running.
 *
 * @param {Error} err - The Axios error caught in the try/catch block.
 * @returns {string} A displayable error message.
 */
function parseApiError(err) {
  if (!err.response) {
    return 'Unable to reach the server. Make sure the backend is running.'
  }

  const detail = err.response.data?.detail

  // Business logic error — detail is already a plain string
  if (typeof detail === 'string') {
    return detail
  }

  // Pydantic validation error — detail is an array of error objects.
  // Each object has a "msg" field like "Value error, Invalid Email format".
  // We strip the "Value error, " prefix added by Pydantic v2.
  if (Array.isArray(detail)) {
    return detail
      .map(e => e.msg.replace('Value error, ', ''))
      .join(' — ')
  }

  return 'An error has occurred.'
}

/**
 * AuthPage — Login and registration page.
 *
 * A single page handles both modes. The user switches between them
 * with the button at the bottom. `mode` controls which fields are
 * shown and which API call is made on submit.
 *
 * Flow:
 *   - Login: POST /auth/login via AuthContext.login() → redirect to /dashboard
 *   - Register: POST /auth/register → then auto-login → redirect to /dashboard
 */
function AuthPage() {
  // 'login' or 'register' — controls the form layout and submit behaviour
  const [mode, setMode] = useState('login')

  // Controlled inputs — one state per field
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [age, setAge] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  // Holds the error message to display below the form, if any
  const [error, setError] = useState('')

  const navigate = useNavigate()
  const { login } = useAuth()

  /**
   * Handle form submission for both login and registration.
   * Prevents the default browser form submission, calls the
   * appropriate API endpoint, then redirects to the dashboard.
   */
  async function handleSubmit(e) {
    e.preventDefault()
    setError('')

    try {
      if (mode === 'register') {
        // Register the new account first.
        // Age is optional — parse to integer if provided, null otherwise.
        await api.post('/auth/register', {
          first_name: firstName,
          last_name: lastName,
          email: email,
          password: password,
          age: age ? parseInt(age, 10) : null
        })
        // Auto-login immediately after successful registration
        await login(email, password)
      } else {
        // Login directly with existing credentials
        await login(email, password)
      }

      navigate('/dashboard')
    } catch (err) {
      // Display the detail message from the API, or a generic fallback
      setError(parseApiError(err))
    }
  }

  return (
    <div>
      <h1>{mode === 'login' ? 'Login' : 'Register'}</h1>

      <form onSubmit={handleSubmit}>

        {/* Registration-only fields — hidden in login mode */}
        {mode === 'register' && (
          <>
            <input
              placeholder="First Name"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
            />
            <input
              placeholder="Last Name"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
            />
            <input
              type="number"
              placeholder="Age (optional)"
              value={age}
              onChange={(e) => setAge(e.target.value)}
            />
          </>
        )}

        {/* Common fields — always visible */}
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">
          {mode === 'login' ? 'Sign in' : 'Create Account'}
        </button>
      </form>

      {/* Error message — only rendered when non-empty */}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Toggle between login and register modes */}
      <button onClick={() => setMode(mode === 'login' ? 'register' : 'login')}>
        {mode === 'login'
          ? "Don't have an account? Register first."
          : 'Already have an account?'}
      </button>
    </div>
  )
}

export default AuthPage
