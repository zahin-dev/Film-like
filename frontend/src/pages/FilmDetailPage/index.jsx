import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { Poster } from '../../components/FilmCard'
import { ErrorState, LoadingState } from '../../components/PageState'
import api from '../../services/api'
import { getApiError } from '../../utils/apiError'
import usePageTitle from '../../utils/usePageTitle'

const prestigeTiers = [
  { value: 'Platinum', label: '最高傑作' },
  { value: 'Gold', label: 'かなり良い' },
  { value: 'Silver', label: '良い' },
  { value: 'Bronze', label: 'まずまず' },
  { value: 'Coal', label: 'いまひとつ' },
  { value: 'Trash', label: '合わなかった' },
]

function formatLocalDate(value) {
  if (!value) return null
  return new Intl.DateTimeFormat('ja-JP', {
    dateStyle: 'long',
    timeZone: 'Asia/Tokyo',
  }).format(new Date(value))
}

function FilmDetailPage() {
  const { filmId } = useParams()
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
  usePageTitle(film?.title || '映画詳細')

  const loadFilm = useCallback(async () => {
    try {
      const [filmResponse, tagResponse] = await Promise.all([
        api.get(`/films/${filmId}`),
        api.get('/tags'),
      ])
      setFilm(filmResponse.data.film)
      setInHistory(filmResponse.data.in_history)
      setTags(tagResponse.data)
    } catch (requestError) {
      setError(getApiError(requestError, '映画の詳細を読み込めませんでした。'))
    } finally {
      setLoading(false)
    }
  }, [filmId])

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
        film_id: Number(filmId),
        tag_ids: selectedTags,
        prestige_tier: prestigeTier || null,
        personal_note: note.trim() || null,
      })
      setInHistory(true)
      setActionMessage('映画日記に追加しました。')
    } catch (requestError) {
      setError(getApiError(requestError, '映画日記に追加できませんでした。'))
    } finally {
      setSaving(false)
    }
  }

  async function removeFilm() {
    const confirmed = window.confirm('この映画と感想を視聴記録から削除しますか？')
    if (!confirmed) return
    setSaving(true)
    setError('')
    setActionMessage('')
    try {
      await api.delete(`/films/log/${filmId}`)
      setInHistory(false)
      setSelectedTags([])
      setPrestigeTier('')
      setNote('')
      setActionMessage('視聴記録から削除しました。')
    } catch (requestError) {
      setError(getApiError(requestError, '視聴記録から削除できませんでした。'))
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <LoadingState message="ローカルカタログから映画情報を読み込んでいます…" />
  if (error && !film) return <ErrorState message={error} onRetry={retryFilm} />
  if (!film) return null

  const streamingUpdated = formatLocalDate(film.streaming_updated_at)

  return (
    <div className="detail-page">
      <Link className="back-link" to="/catalog">← 映画検索へ戻る</Link>

      <section className="detail-hero">
        <div className="detail-poster-wrap">
          <Poster film={film} className="detail-poster" />
        </div>
        <div className="detail-copy">
          <div className="detail-kicker">
            <span>{film.year ? `${film.year}年` : '公開年情報なし'}</span>
            {film.runtime && <span>{film.runtime}分</span>}
            {inHistory && <span className="status-pill">視聴記録に追加済み</span>}
          </div>
          <h1>{film.title}</h1>
          {film.original_title && film.original_title !== film.title && (
            <p className="original-title">原題：{film.original_title}</p>
          )}
          {film.genres.length > 0
            ? <p className="genre-line">{film.genres.join('・')}</p>
            : <p className="genre-line">ジャンル情報はありません</p>}
          <p className="detail-synopsis">{film.synopsis || '日本語のあらすじ情報はありません'}</p>

          <dl className="film-facts">
            <div><dt>監督</dt><dd>{film.director || '監督情報はありません'}</dd></div>
            <div><dt>出演</dt><dd>{film.cast.length > 0 ? film.cast.join('、') : '出演者情報はありません'}</dd></div>
            <div>
              <dt>日本の配信情報</dt>
              <dd>
                {film.streaming_platforms.length > 0 ? film.streaming_platforms.join('、') : '配信情報はありません'}
                {streamingUpdated && <span className="field-hint">情報更新日：{streamingUpdated}</span>}
              </dd>
            </div>
            <div><dt>データ提供元</dt><dd>{film.data_source}</dd></div>
          </dl>
        </div>
      </section>

      <section className="reaction-section" aria-labelledby="reaction-heading">
        <div className="reaction-intro">
          <p className="eyebrow">あなたの感想</p>
          <h2 id="reaction-heading">{inHistory ? 'この映画は記録済みです' : 'この映画をどう感じましたか？'}</h2>
          <p className="muted">
            {inHistory
              ? '感想を付け直す場合は、一度削除してからもう一度記録してください。'
              : '評価やタグは、視聴傾向の分析と次のおすすめに反映されます。'}
          </p>
        </div>

        {inHistory ? (
          <div className="logged-actions">
            <span className="state-symbol success" aria-hidden="true">✓</span>
            <div>
              <strong>視聴記録に保存されています</strong>
              <p>映画情報と感想はローカルDBに保存され、外部APIへ送信されません。</p>
            </div>
            <button className="button danger" type="button" onClick={removeFilm} disabled={saving}>
              {saving ? '削除中です…' : '視聴記録から削除'}
            </button>
          </div>
        ) : (
          <form className="reaction-form" onSubmit={logFilm}>
            <fieldset>
              <legend>当てはまる感想タグを選択</legend>
              {tags.length === 0 ? (
                <p className="muted">利用できるタグがありません。タグなしでも記録できます。</p>
              ) : (
                <div className="tag-picker">
                  {tags.map((tag) => (
                    <label key={tag.id} className={selectedTags.includes(tag.id) ? 'tag-option selected' : 'tag-option'} title={tag.description}>
                      <input
                        type="checkbox"
                        checked={selectedTags.includes(tag.id)}
                        onChange={() => toggleTag(tag.id)}
                        aria-label={`${tag.name}：${tag.description}`}
                      />
                      <span>{tag.name}</span>
                    </label>
                  ))}
                </div>
              )}
            </fieldset>

            <div className="form-grid two-column reaction-fields">
              <label>
                評価 <span className="optional">任意</span>
                <select value={prestigeTier} onChange={(event) => setPrestigeTier(event.target.value)}>
                  <option value="">評価なし</option>
                  {prestigeTiers.map((tier) => <option key={tier.value} value={tier.value}>{tier.label}</option>)}
                </select>
              </label>
              <label>
                メモ <span className="optional">任意</span>
                <textarea
                  value={note}
                  onChange={(event) => setNote(event.target.value)}
                  maxLength="2000"
                  rows="4"
                  placeholder="心に残った場面や感想を書いてください"
                />
                <span className="field-hint">{note.length}/2000文字</span>
              </label>
            </div>

            <button className="button primary" type="submit" disabled={saving}>
              {saving ? '映画日記に追加中です…' : 'この映画を記録する'}
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
