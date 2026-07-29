import assert from 'node:assert/strict'
import { readFile } from 'node:fs/promises'

const read = (path) => readFile(new URL(`../${path}`, import.meta.url), 'utf8')

const html = await read('index.html')
const states = await read('src/components/PageState.jsx')
const catalog = await read('src/pages/CatalogPage/index.jsx')
const dashboard = await read('src/pages/DashboardPage/index.jsx')
const detail = await read('src/pages/FilmDetailPage/index.jsx')
const recommendation = await read('src/pages/RecommendationPage/index.jsx')
const styles = await read('src/index.css')

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

for (const [name, value] of [
  ['forest', '#04202c'],
  ['evergreen', '#304040'],
  ['pine', '#5b7065'],
  ['fog', '#c9d1c8'],
]) {
  assert.match(styles, new RegExp(`--${name}:\\s*${value}`, 'i'), `${name}トークンが基準色で定義されていること`)
}

assert.match(styles, /--primary:\s*var\(--forest\)/)
assert.match(styles, /--primary-hover:\s*var\(--evergreen\)/)
assert.match(styles, /\.button\.danger\s*\{[^}]*var\(--danger\)/s)
assert.match(styles, /\.tag-option\.selected span::before\s*\{[^}]*content:\s*"✓"/s)
assert.match(styles, /@media \(max-width: 480px\)/)
assert.match(styles, /min-width:\s*320px/)
assert.doesNotMatch(styles, /#e84f33|#b9311d|#173b4d|#287a96|#f1c96e/i)

console.log('日本語UI契約テストに合格しました。')
