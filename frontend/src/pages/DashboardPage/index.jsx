import { useEffect, useState } from 'react'
import { useAuth } from '../../context/authStore'
import api from '../../services/api'

function errorMessage(error) {
  const detail = error.response?.data?.detail
  return typeof detail === 'string' ? detail : 'The request failed. Please try again.'
}

export default function DashboardPage() {
  const { logout } = useAuth()
  const [query, setQuery] = useState('')
  const [films, setFilms] = useState([])
  const [history, setHistory] = useState([])
  const [tags, setTags] = useState([])
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    const options = { signal: controller.signal }
    Promise.all([api.get('/films/history', options), api.get('/tags', options)])
      .then(([records, availableTags]) => {
        setHistory(records.data)
        setTags(availableTags.data)
        setLoading(false)
      })
      .catch((failure) => {
        if (!controller.signal.aborted) setError(errorMessage(failure))
      })
    return () => controller.abort()
  }, [])

  async function run(action) {
    setError('')
    setBusy(true)
    try {
      await action()
    } catch (failure) {
      setError(errorMessage(failure))
    } finally {
      setBusy(false)
    }
  }

  function search(event) {
    event.preventDefault()
    run(async () => {
      const response = await api.get('/films/search', { params: { query: query.trim() } })
      setFilms(response.data)
    })
  }

  function log(event) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    run(async () => {
      const response = await api.post('/films/log', {
        tmdb_id: Number(form.get('film')),
        tag_ids: form.getAll('tags').map(Number),
        personal_note: form.get('note') || null,
      })
      setHistory((records) => [response.data, ...records])
    })
  }

  function remove(tmdbId) {
    run(async () => {
      await api.delete(`/films/log/${tmdbId}`)
      const response = await api.get('/films/history')
      setHistory(response.data)
    })
  }

  const unloggedFilms = films.filter((film) => !history.some((entry) => entry.tmdb_id === film.tmdb_id))
  return (
    <main>
      <h1>Film diary</h1>
      <p>Verification interface for the reconstructed scope</p>
      <button type="button" onClick={logout}>Sign out</button>
      {error && <p role="alert">{error}</p>}
      {loading && !error && <p role="status">Loading your diary…</p>}
      {!loading && (
        <>
          <h2>Search TMDB</h2>
          <form onSubmit={search}>
            <label>Film title <input value={query} onChange={(event) => setQuery(event.target.value)} required /></label>
            <button disabled={busy || !query.trim()}>Search</button>
          </form>
          {unloggedFilms.length > 0 && (
            <form onSubmit={log}>
              <label>Film <select name="film" required>
                {unloggedFilms.map((film) => <option key={film.tmdb_id} value={film.tmdb_id}>{film.title} ({film.year ?? 'year unknown'})</option>)}
              </select></label>
              <label>Reaction tags <select name="tags" multiple>
                {tags.map((tag) => <option key={tag.id} value={tag.id}>{tag.name}</option>)}
              </select></label>
              <label>Personal note <textarea name="note" /></label>
              <button disabled={busy}>Log film</button>
            </form>
          )}
          <h2>Viewing history</h2>
          {history.length === 0 && <p>No films logged.</p>}
          <ul>
            {history.map((entry) => (
              <li key={entry.id}>
                <strong>{entry.title || `TMDB ${entry.tmdb_id}`}</strong>
                <p>{entry.tags.map((tag) => tag.name).join(', ')}</p>
                {entry.personal_note && <p>{entry.personal_note}</p>}
                <button type="button" onClick={() => remove(entry.tmdb_id)} disabled={busy}>Remove</button>
              </li>
            ))}
          </ul>
        </>
      )}
    </main>
  )
}
