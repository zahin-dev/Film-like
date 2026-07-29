import { Link } from 'react-router-dom'

const apiBaseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')

function posterSource(path) {
  if (!path) return null
  return path.startsWith('/') ? `${apiBaseUrl}${path}` : path
}

function Poster({ film, className = '' }) {
  const src = posterSource(film.poster_url)
  if (src) {
    return (
      <img
        className={`poster ${className}`}
        src={src}
        alt={`${film.title}のポスター`}
      />
    )
  }
  return (
    <div className={`poster poster-placeholder ${className}`} role="img" aria-label={`${film.title}のポスター画像はありません`}>
      <span aria-hidden="true">FL</span>
    </div>
  )
}

function FilmCard({ film, reason, children }) {
  return (
    <article className="film-card">
      <Link to={`/films/${film.id}`} className="poster-link" aria-label={`${film.title}の詳細を見る`}>
        <Poster film={film} />
      </Link>
      <div className="film-card-body">
        <p className="eyebrow">{film.year ? `${film.year}年` : '公開年情報なし'}</p>
        <h2><Link to={`/films/${film.id}`}>{film.title}</Link></h2>
        <p className="muted line-clamp">{film.synopsis || '日本語のあらすじ情報はありません'}</p>
        {reason && <p className="recommendation-reason">{reason}</p>}
        {children}
      </div>
    </article>
  )
}

export { Poster }
export default FilmCard
