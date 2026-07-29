import { useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/authStore'
import usePageTitle from '../../utils/usePageTitle'

function ProfilePage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  usePageTitle('プロフィール')

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
          <p className="eyebrow light">プロフィール</p>
          <h1>{user?.username || 'Film-likeユーザー'}</h1>
          <p>映画日記とおすすめは、このアカウントの視聴記録だけを使用します。</p>
        </div>
      </section>

      <section className="profile-grid" aria-labelledby="profile-details-heading">
        <div className="profile-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">アカウント</p>
              <h2 id="profile-details-heading">登録情報</h2>
            </div>
          </div>
          <dl className="profile-details">
            <div><dt>名</dt><dd>{user?.first_name || '情報なし'}</dd></div>
            <div><dt>姓</dt><dd>{user?.last_name || '情報なし'}</dd></div>
            <div><dt>メールアドレス</dt><dd>{user?.email || '情報なし'}</dd></div>
            <div><dt>年齢</dt><dd>{user?.age ? `${user.age}歳` : '未登録'}</dd></div>
          </dl>
          <p className="field-hint">現在のバックエンドAPIでは、登録情報の編集には対応していません。</p>
        </div>

        <aside className="profile-card session-card" aria-labelledby="session-heading">
          <p className="eyebrow">ログイン状態</p>
          <h2 id="session-heading">この端末でログイン中</h2>
          <p className="muted">ログアウトすると、このブラウザーに保存されたアクセストークンとプロフィール情報を削除します。</p>
          <button className="button danger full" type="button" onClick={handleLogout}>Film-likeからログアウト</button>
        </aside>
      </section>
    </div>
  )
}

export default ProfilePage
