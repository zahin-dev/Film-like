import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Poster } from '../../components/FilmCard'
import { ErrorState, LoadingState } from '../../components/PageState'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'

const prestigeTiers = ['Platinum', 'Gold', 'Silver', 'Bronze', 'Coal', 'Trash']

function FilmDetailPage() {
  const { tmdbId } = useParams()
  const [film, setFilm] = useState(null)
  const [inHistory, setInHistory] = useState(false)
  const [tags, setTags] = useState([])
  const [selectedTags, setSelectedTags] = useState([])
  const [prestigeTier, setPrestigeTier] = useState('')
  const [note, setNote] = useState('')
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [actionMessage, setActionMessage] = useState('')

  const loadFilm = useCallback(async () => {
    try {
      const [filmResponse, tagResponse] = await Promise.all([
        api.get(`/films/${tmdbId}`),
        api.get('/tags'),
      ])
      setFilm(filmResponse.data.film)
      setInHistory(filmResponse.data.in_history)
      setTags(tagResponse.data)
    } catch (requestError) {
      setError(getApiError(requestError, 'Film details could not be loaded.'))
    } finally {
      setLoading(false)
    }
  }, [tmdbId])

  useEffect(() => {
    const task = window.setTimeout(loadFilm, 0)
    return () => window.clearTimeout(task)
  }, [loadFilm])

  function retryFilm() {
    setLoading(true)
    setError('')
    loadFilm()
  }

  function toggleTag(tagId) {
    setSelectedTags((current) => current.includes(tagId)
      ? current.filter((id) => id !== tagId)
      : [...current, tagId])
  }

  async function logFilm(event) {
    event.preventDefault()
    setSaving(true)
    setError('')
    setActionMessage('')
    try {
      await api.post('/films/log', {
        tmdb_id: Number(tmdbId),
        tag_ids: selectedTags,
        prestige_tier: prestigeTier || null,
        personal_note: note.trim() || null,
      })
      setInHistory(true)
      setActionMessage('Added to your film diary.')
    } catch (requestError) {
      setError(getApiError(requestError, 'This film could not be added.'))
    } finally {
      setSaving(false)
    }
  }

  async function removeFilm() {
    setSaving(true)
    setError('')
    setActionMessage('')
    try {
      await api.delete(`/films/log/${tmdbId}`)
      setInHistory(false)
      setSelectedTags([])
      setPrestigeTier('')
      setNote('')
      setActionMessage('Removed from your film diary.')
    } catch (requestError) {
      setError(getApiError(requestError, 'This film could not be removed.'))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <LoadingState message="Fetching the complete TMDB record…" />
  if (error && !film) return <ErrorState message={error} onRetry={retryFilm} />
  if (!film) return null

  return (
    <div className="detail-page">
      <Link className="back-link" to="/catalog">← Back to catalog</Link>

      <section className="detail-hero">
        <div className="detail-poster-wrap">
          <Poster film={film} className="detail-poster" />
        </div>
        <div className="detail-copy">
          <div className="detail-kicker">
            <span>{film.year || 'Year unavailable'}</span>
            {film.runtime && <span>{film.runtime} min</span>}
            {inHistory && <span className="status-pill">In your diary</span>}
          </div>
          <h1>{film.title}</h1>
          {film.genres?.length > 0 && <p className="genre-line">{film.genres.join(' · ')}</p>}
          <p className="detail-synopsis">{film.synopsis || 'TMDB does not currently provide a synopsis for this film.'}</p>

          <dl className="film-facts">
            <div><dt>Director</dt><dd>{film.director || 'Not available'}</dd></div>
            <div><dt>Cast</dt><dd>{film.cast?.join(', ') || 'Not available'}</dd></div>
            <div><dt>Streaming in France</dt><dd>{film.streaming_platforms?.join(', ') || 'No subscription provider listed'}</dd></div>
          </dl>
        </div>
      </section>

      <section className="reaction-section" aria-labelledby="reaction-heading">
        <div className="reaction-intro">
          <p className="eyebrow">Your reaction</p>
          <h2 id="reaction-heading">{inHistory ? 'This one is in the diary.' : 'How did this film land?'}</h2>
          <p className="muted">
            {inHistory
              ? 'Remove it if you want to clear this reaction and log it again later.'
              : 'Your tags and tier help shape future mood recommendations.'}
          </p>
        </div>

        {inHistory ? (
          <div className="logged-actions">
            <span className="state-symbol success" aria-hidden="true">✓</span>
            <div>
              <strong>Logged in your viewing history</strong>
              <p>Film metadata stays in TMDB; Film-like keeps your reaction and the TMDB ID.</p>
            </div>
            <button className="button danger" type="button" onClick={removeFilm} disabled={saving}>
              {saving ? 'Removing…' : 'Remove from diary'}
            </button>
          </div>
        ) : (
          <form className="reaction-form" onSubmit={logFilm}>
            <fieldset>
              <legend>Choose any tags that fit</legend>
              {tags.length === 0 ? (
                <p className="muted">No tags are available yet. You can still log the film.</p>
              ) : (
                <div className="tag-picker">
                  {tags.map((tag) => (
                    <label key={tag.id} className={selectedTags.includes(tag.id) ? 'tag-option selected' : 'tag-option'} title={tag.description}>
                      <input
                        type="checkbox"
                        checked={selectedTags.includes(tag.id)}
                        onChange={() => toggleTag(tag.id)}
                      />
                      <span>{tag.name}</span>
                    </label>
                  ))}
                </div>
              )}
            </fieldset>

            <div className="form-grid two-column reaction-fields">
              <label>
                Prestige tier <span className="optional">Optional</span>
                <select value={prestigeTier} onChange={(event) => setPrestigeTier(event.target.value)}>
                  <option value="">No tier</option>
                  {prestigeTiers.map((tier) => <option key={tier} value={tier}>{tier}</option>)}
                </select>
              </label>
              <label>
                Personal note <span className="optional">Optional</span>
                <textarea
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                  maxLength="2000"
                  rows="4"
                  placeholder="What stayed with you?"
                />
                <span className="field-hint">{note.length}/2000 characters</span>
              </label>
            </div>

            <button className="button primary" type="submit" disabled={saving}>
              {saving ? 'Adding to diary…' : 'Log this film'}
            </button>
          </form>
        )}

        {actionMessage && <p className="inline-success" role="status">{actionMessage}</p>}
        {error && film && <p className="inline-alert" role="alert">{error}</p>}
      </section>
    </div>
  )
}

export default FilmDetailPage
