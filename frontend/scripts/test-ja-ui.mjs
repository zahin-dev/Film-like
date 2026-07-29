import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), 'utf8')

const html = await read('index.html')
const states = await read('src/components/PageState.jsx')
const catalog = await read('src/pages/CatalogPage/index.jsx')
const dashboard = await read('src/pages/DashboardPage/index.jsx')
const detail = await read('src/pages/FilmDetailPage/index.jsx')
const recommendation = await read('src/pages/RecommendationPage/index.jsx')

assert.match(html, /<html lang="ja">/)
assert.match(states, /読み込み中です/)
assert.match(states, /読み込みに失敗しました/)
assert.match(states, /もう一度試す/)
assert.match(catalog, /placeholder="例：羅生門"/)
assert.match(catalog, /aria-label="映画タイトルを検索"/)
assert.match(catalog, /api\.get\('\/films\/search'/)
assert.match(dashboard, /Intl\.DateTimeFormat\('ja-JP'/)
assert.match(dashboard, /timeZone: 'Asia\/Tokyo'/)
assert.match(detail, /film_id: Number\(filmId\)/)
assert.match(detail, /出演者情報はありません/)
assert.match(recommendation, /ローカル推薦エンジン/)
assert.match(recommendation, /aria-label="現在の気分"/)
assert.doesNotMatch(recommendation, /Mistral|TMDB|API key/i)

console.log('日本語UI契約テストに合格しました。')
