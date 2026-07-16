import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Poster } from '../../components/FilmCard'
import { EmptyState, ErrorState, LoadingState } from '../../components/PageState'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'

function formatDate(value) {
  return new Intl.DateTimeFormat('en', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  }).format(new Date(value))
}

function DashboardPage() {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const loadHistory = useCallback(async () => {
    try {
      const response = await api.get('/films/history')
      setEntries(response.data)
    } catch (requestError) {
      setError(getApiError(requestError, 'Your viewing history could not be loaded.'))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const task = window.setTimeout(loadHistory, 0)
    return () => window.clearTimeout(task)
  }, [loadHistory])

  function retryHistory() {
    setLoading(true)
    setError('')
    loadHistory()
  }

  const ratedCount = entries.filter((entry) => entry.prestige_tier).length
  const tagCount = new Set(entries.flatMap((entry) => entry.tags.map((tag) => tag.name))).size

  return (
    <div className="page-stack">
      <section className="page-hero compact-hero">
        <div>
          <p className="eyebrow light">Your film diary</p>
          <h1>Every watch leaves a trace.</h1>
          <p>Revisit what moved you, what missed, and the moods you keep returning to.</p>
        </div>
        <Link className="button light" to="/catalog">Find a film</Link>
      </section>

      {!loading && !error && entries.length > 0 && (
        <section className="stat-row" aria-label="Viewing history summary">
          <div><strong>{entries.length}</strong><span>Films logged</span></div>
          <div><strong>{ratedCount}</strong><span>Tier rated</span></div>
          <div><strong>{tagCount}</strong><span>Moods captured</span></div>
        </section>
      )}

      <section aria-labelledby="history-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Chronicle</p>
            <h2 id="history-heading">Viewing history</h2>
          </div>
          {!loading && entries.length > 0 && (
            <button className="button ghost compact" type="button" onClick={retryHistory}>Refresh</button>
          )}
        </div>

        {loading && <LoadingState message="Bringing your film diary up to date…" />}
        {!loading && error && <ErrorState message={error} onRetry={retryHistory} />}
        {!loading && !error && entries.length === 0 && (
          <EmptyState
            title="Your opening scene is waiting"
            message="Search the catalog and log a film to start shaping your diary and recommendations."
            action={<Link className="button primary" to="/catalog">Explore the catalog</Link>}
          />
        )}

        {!loading && !error && entries.length > 0 && (
          <div className="diary-grid">
            {entries.map((entry) => {
              const displayFilm = { tmdb_id: entry.tmdb_id, title: entry.title || `TMDB #${entry.tmdb_id}`, poster_url: entry.poster_url }
              return (
                <article className="diary-card" key={entry.id}>
                  <Link to={`/films/${entry.tmdb_id}`} aria-label={`View ${displayFilm.title}`}>
                    <Poster film={displayFilm} />
                  </Link>
                  <div className="diary-card-body">
                    <div className="diary-meta">
                      <span>{formatDate(entry.created_at)}</span>
                      {entry.prestige_tier && <span className="tier-badge">{entry.prestige_tier}</span>}
                    </div>
                    <h3><Link to={`/films/${entry.tmdb_id}`}>{displayFilm.title}</Link></h3>
                    {entry.tags.length > 0 && (
                      <ul className="tag-list" aria-label="Your tags">
                        {entry.tags.map((tag) => <li key={tag.id}>{tag.name}</li>)}
                      </ul>
                    )}
                    {entry.personal_note && <blockquote>“{entry.personal_note}”</blockquote>}
                  </div>
                </article>
              )
            })}
          </div>
        )}
      </section>
    </div>
  )
}

export default DashboardPage
