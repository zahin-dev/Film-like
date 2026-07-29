import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Poster } from '../../components/FilmCard'
import { EmptyState, LoadingState } from '../../components/PageState'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'
import usePageTitle from '../../utils/usePageTitle'

const moods = [
  { value: 'relaxed', label: 'リラックスしたい', cue: '穏やかに楽しむ' },
  { value: 'uplifting', label: '前向きになりたい', cue: '観終わったあと軽やかに' },
  { value: 'excited', label: '刺激がほしい', cue: '勢いと高揚感' },
  { value: 'thoughtful', label: 'じっくり考えたい', cue: '余韻の残るテーマ' },
  { value: 'emotional', label: '思いきり感動したい', cue: '感情を動かす物語' },
  { value: 'romantic', label: '恋愛気分を味わいたい', cue: '二人の関係を見つめる' },
  { value: 'adventurous', label: '冒険したい', cue: '知らない世界へ' },
  { value: 'scared', label: '怖い映画を観たい', cue: '緊張と恐怖を楽しむ' },
]

function RecommendationPage() {
  const [mood, setMood] = useState('thoughtful')
  const [recommendations, setRecommendations] = useState([])
  const [historyTags, setHistoryTags] = useState([])
  const [resultMessage, setResultMessage] = useState('')
  const [activeIndex, setActiveIndex] = useState(0)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [hasRequested, setHasRequested] = useState(false)
  usePageTitle('おすすめ')

  async function requestRecommendations() {
    setLoading(true)
    setError('')
    setResultMessage('')
    setHasRequested(true)
    setActiveIndex(0)
    try {
      const response = await api.post('/recommendations', { mood, limit: 5 })
      setRecommendations(response.data.recommendations)
      setHistoryTags(response.data.history_tags_used)
      setResultMessage(response.data.message || '')
    } catch (requestError) {
      setRecommendations([])
      setHistoryTags([])
      setError(getApiError(requestError, 'おすすめを取得できませんでした。'))
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
          <p className="eyebrow light">ローカル推薦エンジン</p>
          <h1>今夜は、どんな気分で映画を観たいですか？</h1>
          <p>
            選んだ気分、映画日記の感想タグ、最近観たジャンルをこのサーバー内で点数化します。
            外部AIやクラウドAPIは使わず、視聴済みの映画は候補から除外します。
          </p>
        </div>
        <span className="ai-orbit" aria-hidden="true">JP</span>
      </section>

      <section className="mood-panel" aria-labelledby="mood-heading">
        <div className="section-heading">
          <div>
            <p className="eyebrow">今の気分</p>
            <h2 id="mood-heading">気分を一つ選んでください</h2>
          </div>
          <span className="result-count">1つ選択</span>
        </div>

        <div className="mood-grid" role="radiogroup" aria-label="現在の気分">
          {moods.map((item) => (
            <button
              key={item.value}
              type="button"
              role="radio"
              aria-checked={mood === item.value}
              aria-label={`${item.label}：${item.cue}`}
              className={mood === item.value ? 'mood-button selected' : 'mood-button'}
              onClick={() => setMood(item.value)}
            >
              <strong>{item.label}</strong>
              <span>{item.cue}</span>
            </button>
          ))}
        </div>

        <button className="button primary recommendation-submit" type="button" onClick={requestRecommendations} disabled={loading}>
          {loading ? '候補を計算しています…' : 'この気分に合う映画を探す'}
        </button>
      </section>

      {loading && <LoadingState message="気分、感想タグ、最近の視聴傾向から候補を計算しています…" />}

      {!loading && error && (
        <div className="state-panel error-panel" role="alert">
          <span className="state-symbol" aria-hidden="true">!</span>
          <h2>おすすめを取得できませんでした</h2>
          <p>{error}</p>
          <p className="state-footnote">推薦処理はローカルで動作します。バックエンドとデータベースの状態を確認してください。</p>
          <button className="button secondary" type="button" onClick={requestRecommendations}>もう一度試す</button>
        </div>
      )}

      {!loading && !error && hasRequested && recommendations.length === 0 && (
        <EmptyState
          title="おすすめできる未視聴作品がありません"
          message={resultMessage || 'ローカルカタログへ映画を追加するか、視聴記録を見直してください。'}
        />
      )}

      {!loading && !error && active && (
        <section className="recommendation-deck" aria-live="polite" aria-label={`${recommendations.length}件中${activeIndex + 1}件目のおすすめ`}>
          <div className="deck-progress">
            <span>{activeIndex + 1} / {recommendations.length}</span>
            <div className="progress-track" aria-hidden="true"><span style={{ width: `${((activeIndex + 1) / recommendations.length) * 100}%` }} /></div>
          </div>

          {resultMessage && <p className="inline-alert recommendation-notice">{resultMessage}</p>}

          <article className="recommendation-card">
            <Poster film={active.film} className="recommendation-poster" />
            <div className="recommendation-copy">
              <p className="eyebrow">おすすめの理由付き</p>
              <h2>{active.film.title}</h2>
              <p className="genre-line">
                {[active.film.year ? `${active.film.year}年` : null, ...active.film.genres].filter(Boolean).join('・') || 'ジャンル情報はありません'}
              </p>
              <blockquote>「{active.reason}」</blockquote>
              <p className="muted">{active.film.synopsis || '日本語のあらすじ情報はありません'}</p>

              {historyTags.length > 0 && (
                <div className="context-note">
                  <span>反映した映画日記の傾向</span>
                  <ul className="tag-list" aria-label="推薦に反映した感想タグ">
                    {historyTags.map((tag) => <li key={tag}>{tag}</li>)}
                  </ul>
                </div>
              )}

              <div className="deck-actions">
                <button className="button ghost" type="button" onClick={() => setActiveIndex((index) => index + 1)}>
                  次の候補へ
                </button>
                <Link className="button primary" to={`/films/${active.film.id}`}>映画の詳細を見る</Link>
              </div>
            </div>
          </article>
        </section>
      )}

      {!loading && !error && exhausted && (
        <EmptyState
          title="今回のおすすめをすべて確認しました"
          message="同じ候補を見直すか、別の気分を選んで再計算できます。"
          action={(
            <div className="button-row">
              <button className="button secondary" type="button" onClick={() => setActiveIndex(0)}>最初から見る</button>
              <button className="button primary" type="button" onClick={requestRecommendations}>もう一度計算する</button>
            </div>
          )}
        />
      )}
    </div>
  )
}

export default RecommendationPage
