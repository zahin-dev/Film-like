import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Poster } from '../../components/FilmCard'
import { EmptyState, ErrorState, LoadingState } from '../../components/PageState'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'
import usePageTitle from '../../utils/usePageTitle'

function formatDate(value) {
  return new Intl.DateTimeFormat('ja-JP', {
    dateStyle: 'long',
    timeZone: 'Asia/Tokyo',
  }).format(new Date(value))
}

function DashboardPage() {
  const [entries, setEntries] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [insights, setInsights] = useState(null)
  const [insightsLoading, setInsightsLoading] = useState(true)
  const [insightsError, setInsightsError] = useState('')
  usePageTitle('映画日記')

  const loadHistory = useCallback(async () => {
    try {
      const response = await api.get('/films/history')
      setEntries(response.data)
    } catch (requestError) {
      setError(getApiError(requestError, '視聴記録を読み込めませんでした。'))
    } finally {
      setLoading(false)
    }
  }, [])

  const loadInsights = useCallback(async () => {
    try {
      const response = await api.get('/insights')
      setInsights(response.data)
    } catch (requestError) {
      setInsightsError(getApiError(requestError, '視聴傾向を読み込めませんでした。'))
    } finally {
      setInsightsLoading(false)
    }
  }, [])

  useEffect(() => {
    const task = window.setTimeout(loadHistory, 0)
    return () => window.clearTimeout(task)
  }, [loadHistory])

  useEffect(() => {
    const task = window.setTimeout(loadInsights, 0)
    return () => window.clearTimeout(task)
  }, [loadInsights])

  function retryHistory() {
    setLoading(true)
    setError('')
    loadHistory()
  }

  function retryInsights() {
    setInsightsLoading(true)
    setInsightsError('')
    loadInsights()
  }

  const ratedCount = entries.filter((entry) => entry.prestige_tier).length
  const tagCount = new Set(entries.flatMap((entry) => entry.tags.map((tag) => tag.key))).size

  return (
    <div className="page-stack">
      <section className="page-hero compact-hero">
        <div>
          <p className="eyebrow light">あなたの映画日記</p>
          <h1>観た一本を、記憶に残す。</h1>
          <p>心に残ったこと、合わなかったこと、繰り返し選ぶ気分を振り返れます。</p>
        </div>
        <Link className="button light" to="/catalog">映画を探す</Link>
      </section>

      {!loading && !error && entries.length > 0 && (
        <section className="stat-row" aria-label="視聴記録の概要">
          <div><strong>{entries.length}</strong><span>記録した映画</span></div>
          <div><strong>{ratedCount}</strong><span>評価した映画</span></div>
          <div><strong>{tagCount}</strong><span>選んだ感想タグ</span></div>
        </section>
      )}

      <section className="insights-section" aria-labelledby="insights-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">視聴傾向</p>
            <h2 id="insights-heading">映画日記の分析</h2>
            <p className="section-description">
              映画を記録するときに自分で選んだタグだけを集計しています。外部AIによる推測は行いません。
            </p>
          </div>
          {!insightsLoading && insights && (
            <button className="button ghost compact" type="button" onClick={retryInsights}>分析を更新</button>
          )}
        </div>

        {insightsLoading && <LoadingState message="選んだ感想タグを集計しています…" />}
        {!insightsLoading && insightsError && <ErrorState message={insightsError} onRetry={retryInsights} />}
        {!insightsLoading && !insightsError && insights?.total_films === 0 && (
          <EmptyState
            title="分析できる視聴記録がまだありません"
            message="映画を観た記録と感想タグを追加すると、ここに傾向が表示されます。"
            action={<Link className="button primary" to="/catalog">映画を探す</Link>}
          />
        )}
        {!insightsLoading && !insightsError && insights?.total_films > 0 && insights.tagged_films === 0 && (
          <EmptyState
            title="感想タグを追加してみましょう"
            message="映画は記録されていますが、集計できる感想タグがまだありません。"
            action={<Link className="button primary" to="/catalog">タグを付ける映画を探す</Link>}
          />
        )}

        {!insightsLoading && !insightsError && insights?.tagged_films > 0 && (
          <div className="insights-content">
            <dl className="insights-summary" aria-label="映画日記の集計">
              <div><dt>記録した映画</dt><dd>{insights.total_films}</dd></div>
              <div><dt>タグ付きの映画</dt><dd>{insights.tagged_films}</dd></div>
              <div><dt>異なる感想タグ</dt><dd>{insights.unique_reaction_signals}</dd></div>
            </dl>

            <div className="insights-grid">
              <article className="insights-panel">
                <h3>よく選ぶ感想</h3>
                <p className="insights-note">タグ付き映画のうち、その感想を選んだ割合です。</p>
                <ol className="signal-list">
                  {insights.top_reaction_signals.map((signal) => (
                    <li key={signal.tag}>
                      <div className="signal-label">
                        <span>{signal.tag}</span>
                        <strong>{signal.count}本 · {signal.percentage}%</strong>
                      </div>
                      <div className="signal-bar" aria-label={`${signal.tag}は${signal.percentage}パーセント`}>
                        <span style={{ width: `${signal.percentage}%` }} />
                      </div>
                    </li>
                  ))}
                </ol>
              </article>

              <article className="insights-panel">
                <h3>最近の感想</h3>
                <p className="insights-note">直近5件の視聴記録から集計しています。</p>
                {insights.recent_reaction_signals.length === 0 ? (
                  <p className="recent-signals-empty">直近5件には感想タグがありません。</p>
                ) : (
                  <ul className="recent-signal-list">
                    {insights.recent_reaction_signals.map((signal) => (
                      <li key={signal.tag}>
                        <span>{signal.tag}</span>
                        <strong>{signal.count}本 · {signal.percentage}%</strong>
                      </li>
                    ))}
                  </ul>
                )}
              </article>
            </div>
          </div>
        )}
      </section>

      <section aria-labelledby="history-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">これまでの記録</p>
            <h2 id="history-heading">視聴履歴</h2>
          </div>
          {!loading && entries.length > 0 && (
            <button className="button ghost compact" type="button" onClick={retryHistory}>履歴を更新</button>
          )}
        </div>

        {loading && <LoadingState message="映画日記を読み込んでいます…" />}
        {!loading && error && <ErrorState message={error} onRetry={retryHistory} />}
        {!loading && !error && entries.length === 0 && (
          <EmptyState
            title="最初の一本を記録しましょう"
            message="カタログから映画を探し、感想を残すと日記とおすすめに反映されます。"
            action={<Link className="button primary" to="/catalog">映画を探す</Link>}
          />
        )}

        {!loading && !error && entries.length > 0 && (
          <div className="diary-grid">
            {entries.map((entry) => {
              const displayFilm = { id: entry.film_id, title: entry.title || '映画情報はありません', poster_url: entry.poster_url }
              return (
                <article className="diary-card" key={entry.id}>
                  <Link to={`/films/${entry.film_id}`} aria-label={`${displayFilm.title}の詳細を見る`}>
                    <Poster film={displayFilm} />
                  </Link>
                  <div className="diary-card-body">
                    <div className="diary-meta">
                      <span>{formatDate(entry.created_at)}</span>
                      {entry.prestige_tier_label && <span className="tier-badge">{entry.prestige_tier_label}</span>}
                    </div>
                    <h3><Link to={`/films/${entry.film_id}`}>{displayFilm.title}</Link></h3>
                    {entry.tags.length > 0 && (
                      <ul className="tag-list" aria-label="選んだ感想タグ">
                        {entry.tags.map((tag) => <li key={tag.id}>{tag.name}</li>)}
                      </ul>
                    )}
                    {entry.personal_note && <blockquote>「{entry.personal_note}」</blockquote>}
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
