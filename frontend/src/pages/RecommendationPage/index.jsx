import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Poster } from '../../components/FilmCard'
import { EmptyState, LoadingState } from '../../components/PageState'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'

const moods = [
  { value: 'relaxed', label: 'Relaxed', cue: 'Soft landing' },
  { value: 'uplifting', label: 'Uplifting', cue: 'Leave lighter' },
  { value: 'excited', label: 'Excited', cue: 'High energy' },
  { value: 'thoughtful', label: 'Thoughtful', cue: 'Ideas that linger' },
  { value: 'emotional', label: 'Emotional', cue: 'Feel everything' },
  { value: 'romantic', label: 'Romantic', cue: 'A little chemistry' },
  { value: 'adventurous', label: 'Adventurous', cue: 'Go somewhere else' },
  { value: 'scared', label: 'Scared', cue: 'Lights off' },
]

function RecommendationPage() {
  const [mood, setMood] = useState('thoughtful')
  const [recommendations, setRecommendations] = useState([])
  const [historyTags, setHistoryTags] = useState([])
  const [activeIndex, setActiveIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [hasRequested, setHasRequested] = useState(false)

  async function requestRecommendations() {
    setLoading(true)
    setError('')
    setHasRequested(true)
    setActiveIndex(0)
    try {
      const response = await api.post('/recommendations', { mood, limit: 5 })
      setRecommendations(response.data.recommendations)
      setHistoryTags(response.data.history_tags_used)
    } catch (requestError) {
      setRecommendations([])
      setHistoryTags([])
      setError(getApiError(requestError, 'Recommendations are unavailable right now.'))
    } finally {
      setLoading(false)
    }
  }

  const active = recommendations[activeIndex]
  const exhausted = recommendations.length > 0 && activeIndex >= recommendations.length

  return (
    <div className="page-stack recommendation-page">
      <section className="recommendation-intro">
        <div>
          <p className="eyebrow light">Mistral AI × TMDB</p>
          <h1>What kind of film do you need tonight?</h1>
          <p>
            Your mood meets the tags in your diary. Every AI candidate is
            checked against TMDB before it reaches this screen.
          </p>
        </div>
        <span className="ai-orbit" aria-hidden="true">AI</span>
      </section>

      <section className="mood-panel" aria-labelledby="mood-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">Set the tone</p>
            <h2 id="mood-heading">Choose your current mood</h2>
          </div>
          <span className="result-count">One choice</span>
        </div>

        <div className="mood-grid" role="radiogroup" aria-label="Current mood">
          {moods.map((item) => (
            <button
              key={item.value}
              type="button"
              role="radio"
              aria-checked={mood === item.value}
              className={mood === item.value ? 'mood-button selected' : 'mood-button'}
              onClick={() => setMood(item.value)}
            >
              <strong>{item.label}</strong>
              <span>{item.cue}</span>
            </button>
          ))}
        </div>

        <button className="button primary recommendation-submit" type="button" onClick={requestRecommendations} disabled={loading}>
          {loading ? 'Asking Mistral…' : 'Find films for this mood'}
        </button>
      </section>

      {loading && <LoadingState message="Mistral is shaping suggestions, then Film-like is verifying them in TMDB…" />}

      {!loading && error && (
        <div className="state-panel error-panel" role="alert">
          <span className="state-symbol" aria-hidden="true">!</span>
          <h2>Recommendations are not available</h2>
          <p>{error}</p>
          <p className="state-footnote">Live recommendations require a configured Mistral API key and reachable Mistral/TMDB services.</p>
          <button className="button secondary" type="button" onClick={requestRecommendations}>Try again</button>
        </div>
      )}

      {!loading && !error && hasRequested && recommendations.length === 0 && (
        <EmptyState
          title="No verified matches this time"
          message="Try another mood. Film-like only shows suggestions it can verify through TMDB."
        />
      )}

      {!loading && !error && active && (
        <section className="recommendation-deck" aria-live="polite" aria-label={`Recommendation ${activeIndex + 1} of ${recommendations.length}`}>
          <div className="deck-progress">
            <span>{activeIndex + 1} / {recommendations.length}</span>
            <div className="progress-track"><span style={{ width: `${((activeIndex + 1) / recommendations.length) * 100}%` }} /></div>
          </div>

          <article className="recommendation-card">
            <Poster film={active.film} className="recommendation-poster" />
            <div className="recommendation-copy">
              <p className="eyebrow">Verified recommendation</p>
              <h2>{active.film.title}</h2>
              <p className="genre-line">
                {[active.film.year, ...(active.film.genres || [])].filter(Boolean).join(' · ') || 'TMDB verified'}
              </p>
              <blockquote>“{active.reason}”</blockquote>
              {active.film.synopsis && <p className="muted">{active.film.synopsis}</p>}

              {historyTags.length > 0 && (
                <div className="context-note">
                  <span>Diary signals used</span>
                  <ul className="tag-list">
                    {historyTags.map((tag) => <li key={tag}>{tag}</li>)}
                  </ul>
                </div>
              )}

              <div className="deck-actions">
                <button className="button ghost" type="button" onClick={() => setActiveIndex((index) => index + 1)}>
                  Skip
                </button>
                <Link className="button primary" to={`/films/${active.film.tmdb_id}`}>View film details</Link>
              </div>
            </div>
          </article>
        </section>
      )}

      {!loading && !error && exhausted && (
        <EmptyState
          title="You reached the end of this reel"
          message="Replay these matches or choose a different mood for a fresh set."
          action={(
            <div className="button-row">
              <button className="button secondary" type="button" onClick={() => setActiveIndex(0)}>Replay matches</button>
              <button className="button primary" type="button" onClick={requestRecommendations}>Refresh this mood</button>
            </div>
          )}
        />
      )}
    </div>
  )
}

export default RecommendationPage
