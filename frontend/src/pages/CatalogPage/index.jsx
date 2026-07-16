import { useState } from 'react'
import FilmCard from '../../components/FilmCard'
import { EmptyState, ErrorState, LoadingState } from '../../components/PageState'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'

function CatalogPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchedFor, setSearchedFor] = useState('')

  async function search(event) {
    event?.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) {
      setError('Enter a film title before searching.')
      return
    }
    setLoading(true)
    setError('')
    setSearchedFor(trimmed)
    try {
      const response = await api.get('/films/search', { params: { query: trimmed } })
      setResults(response.data)
    } catch (requestError) {
      setResults([])
      setError(getApiError(requestError, 'Film search is unavailable right now.'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <section className="catalog-intro">
        <p className="eyebrow">TMDB catalog</p>
        <h1>Search beyond the algorithm.</h1>
        <p className="muted">Look up a title, inspect the details, then add your own reaction.</p>
        <form className="search-bar" onSubmit={search} role="search">
          <label className="sr-only" htmlFor="film-search">Film title</label>
          <input
            id="film-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="Try ‘In the Mood for Love’"
            autoComplete="off"
          />
          <button className="button primary" type="submit" disabled={loading}>
            {loading ? 'Searching…' : 'Search films'}
          </button>
        </form>
        {error && !searchedFor && <p className="inline-alert" role="alert">{error}</p>}
      </section>

      {loading && <LoadingState message={`Searching TMDB for “${searchedFor}”…`} />}
      {!loading && error && searchedFor && <ErrorState message={error} onRetry={search} />}
      {!loading && !error && searchedFor && results.length === 0 && (
        <EmptyState
          title="No matching films"
          message={`TMDB returned no results for “${searchedFor}”. Try another title or spelling.`}
        />
      )}
      {!loading && !error && results.length > 0 && (
        <section aria-labelledby="results-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Search results</p>
              <h2 id="results-heading">Films matching “{searchedFor}”</h2>
            </div>
            <span className="result-count">{results.length} found</span>
          </div>
          <div className="film-grid">
            {results.map((result) => <FilmCard key={result.tmdb_id} film={result} />)}
          </div>
        </section>
      )}
    </div>
  )
}

export default CatalogPage
