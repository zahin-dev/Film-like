import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authStore'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'
import usePageTitle from '../../utils/usePageTitle'

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
  const isLogin = mode === 'login'
  usePageTitle(isLogin ? 'ログイン' : '新規登録')

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
      setError(getApiError(requestError, '認証に失敗しました。'))
    } finally {
      setSubmitting(false)
    }
  }

  function toggleMode() {
    setMode((current) => current === 'login' ? 'register' : 'login')
    setError('')
  }

  return (
    <main className="auth-page">
      <section className="auth-story" aria-labelledby="brand-heading">
        <div className="auth-brand">
          <span className="brand-mark large" aria-hidden="true">F</span>
          <span>Film-like</span>
        </div>
        <p className="eyebrow light">映画の記憶を、自分の言葉で</p>
        <h1 id="brand-heading">今の気分と、これまで観た映画をつなぐ映画日記。</h1>
        <p>
          日本語のローカルカタログから映画を探し、感想を記録できます。
          おすすめは外部AIを使わず、この端末のデータだけで選びます。
        </p>
        <div className="auth-proof" aria-label="主な機能">
          <span>自分だけの映画日記</span>
          <span>気分から作品を発見</span>
          <span>APIキー不要</span>
        </div>
      </section>

      <section className="auth-form-panel" aria-labelledby="auth-heading">
        <div className="auth-form-wrap">
          <p className="eyebrow">{isLogin ? 'おかえりなさい' : '映画日記を始める'}</p>
          <h2 id="auth-heading">{isLogin ? 'Film-likeにログイン' : 'アカウントを作成'}</h2>
          <p className="muted">
            {isLogin
              ? '前回の続きから、映画の記録を振り返りましょう。'
              : '必要な情報を入力して、最初の一本を記録しましょう。'}
          </p>

          <form className="form-stack" onSubmit={handleSubmit}>
            {!isLogin && (
              <div className="form-grid two-column">
                <label>
                  名
                  <input name="firstName" value={form.firstName} onChange={updateField} autoComplete="given-name" required />
                </label>
                <label>
                  姓
                  <input name="lastName" value={form.lastName} onChange={updateField} autoComplete="family-name" required />
                </label>
              </div>
            )}

            {!isLogin && (
              <label>
                年齢 <span className="optional">任意</span>
                <input name="age" type="number" min="1" max="120" value={form.age} onChange={updateField} inputMode="numeric" placeholder="例：25" />
              </label>
            )}

            <label>
              メールアドレス
              <input name="email" type="email" value={form.email} onChange={updateField} autoComplete="email" placeholder="you@example.com" required />
            </label>

            <label>
              パスワード
              <input name="password" type="password" minLength="8" maxLength="64" value={form.password} onChange={updateField} autoComplete={isLogin ? 'current-password' : 'new-password'} required />
              {!isLogin && <span className="field-hint">8〜64文字で、数字と記号を1文字以上含めてください。</span>}
            </label>

            {error && <p className="inline-alert" role="alert">{error}</p>}

            <button className="button primary full" type="submit" disabled={submitting}>
              {submitting ? '処理中です…' : isLogin ? 'ログイン' : 'アカウントを作成'}
            </button>
          </form>

          <p className="auth-switch">
            {isLogin ? '初めて利用しますか？' : 'すでにアカウントをお持ちですか？'}{' '}
            <button type="button" className="text-button" onClick={toggleMode}>
              {isLogin ? '新規登録' : 'ログイン'}
            </button>
          </p>
        </div>
      </section>
    </main>
  )
}

export default AuthPage
