import { useState } from 'react'
import FilmCard from '../../components/FilmCard'
import { EmptyState, ErrorState, LoadingState } from '../../components/PageState'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'
import usePageTitle from '../../utils/usePageTitle'

function CatalogPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [searchedFor, setSearchedFor] = useState('')
  usePageTitle('映画を探す')

  async function search(event) {
    event?.preventDefault()
    const trimmed = query.trim()
    if (!trimmed) {
      setError('映画のタイトルを入力してください。')
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
      setError(getApiError(requestError, '映画を検索できませんでした。'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page-stack">
      <section className="catalog-intro">
        <p className="eyebrow">ローカル映画カタログ</p>
        <h1>次に観たい映画を探す。</h1>
        <p className="muted">日本語タイトルを優先して検索し、作品情報を確認して日記へ追加できます。</p>
        <form className="search-bar" onSubmit={search} role="search">
          <label className="sr-only" htmlFor="film-search">映画タイトル</label>
          <input
            id="film-search"
            type="search"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="例：羅生門"
            autoComplete="off"
            aria-label="映画タイトルを検索"
          />
          <button className="button primary" type="submit" disabled={loading}>
            {loading ? '検索中です…' : '映画を検索'}
          </button>
        </form>
        {error && !searchedFor && <p className="inline-alert" role="alert">{error}</p>}
      </section>

      {loading && <LoadingState message={`「${searchedFor}」をローカルカタログから検索しています…`} />}
      {!loading && error && searchedFor && <ErrorState message={error} onRetry={search} />}
      {!loading && !error && searchedFor && results.length === 0 && (
        <EmptyState
          title="該当する映画が見つかりませんでした"
          message={`「${searchedFor}」に一致する映画はローカルカタログにありません。表記を変えるか、データを取り込んでください。`}
        />
      )}
      {!loading && !error && results.length > 0 && (
        <section aria-labelledby="results-heading">
          <div className="section-heading">
            <div>
              <p className="eyebrow">検索結果</p>
              <h2 id="results-heading">「{searchedFor}」に一致する映画</h2>
            </div>
            <span className="result-count">{results.length}件</span>
          </div>
          <div className="film-grid">
            {results.map((result) => <FilmCard key={result.id} film={result} />)}
          </div>
        </section>
      )}
    </div>
  )
}

export default CatalogPage
