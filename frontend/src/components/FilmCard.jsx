import { Link } from 'react-router-dom'

function Poster({ film, className = '' }) {
  if (film.poster_url) {
    return (
      <img
        className={`poster ${className}`}
        src={film.poster_url}
        alt={`${film.title} poster`}
      />
    )
  }
  return (
    <div className={`poster poster-placeholder ${className}`} role="img" aria-label={`No poster available for ${film.title}`}>
      <span aria-hidden="true">FL</span>
    </div>
  )
}

function FilmCard({ film, reason, children }) {
  return (
    <article className="film-card">
      <Link to={`/films/${film.tmdb_id}`} className="poster-link" aria-label={`View details for ${film.title}`}>
        <Poster film={film} />
      </Link>
      <div className="film-card-body">
        <p className="eyebrow">{film.year || 'Release year unavailable'}</p>
        <h2><Link to={`/films/${film.tmdb_id}`}>{film.title}</Link></h2>
        {film.synopsis && <p className="muted line-clamp">{film.synopsis}</p>}
        {reason && <p className="recommendation-reason">{reason}</p>}
        {children}
      </div>
    </article>
  )
}

export { Poster }
export default FilmCard
