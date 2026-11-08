# 映画データの取り込み

## 方針

Film-likeは映画情報を無断でスクレイピングしません。インポートする人が、データと画像の利用条件を確認してください。無料で入手できることと、再配布や商用利用が許可されることは同じではありません。

## 1. 出典マニフェスト

```json
{
  "key": "owned-catalog",
  "display_name": "権利確認済みの社内カタログ",
  "license_name": "契約またはライセンス名",
  "license_url": null,
  "commercial_use": "許可",
  "redistribution": "禁止",
  "obtained_on": "2026-07-26",
  "has_japanese_metadata": true,
  "update_method": "管理者が四半期ごとにローカルファイルを更新",
  "notes": "確認担当と証跡の保管場所"
}
```

`key`は英小文字、数字、ハイフンで構成する安定した内部値です。次を曖昧にしないでください。

- データ提供元
- ライセンスまたは契約
- 商用利用の可否
- 再配布の可否
- 取得日
- 日本語情報の有無
- 更新方法

## 2. 映画JSON

トップレベルは配列です。

```json
[
  {
    "external_id": "catalog-001",
    "tmdb_id": null,
    "title_ja": "日本語タイトル",
    "original_title": "Original Title",
    "search_aliases": ["にほんごたいとる"],
    "synopsis_ja": "権利を確認した日本語説明です。",
    "release_date": "2026-01-01",
    "runtime_minutes": 100,
    "genres": ["ドラマ"],
    "directors": ["公式表記の氏名"],
    "cast_members": [],
    "poster_path": "/posters/catalog-001.webp",
    "streaming_platforms": ["ローカルで確認した日本向けサービス"],
    "streaming_region": "JP",
    "streaming_updated_at": "2026-07-26T12:00:00+09:00",
    "recommendation_moods": ["thoughtful"]
  }
]
```

### 対応する気分コード

- `relaxed`
- `uplifting`
- `excited`
- `thoughtful`
- `emotional`
- `romantic`
- `adventurous`
- `scared`

### 欠損情報

日本語タイトル、あらすじ、人名を推測で作らないでください。確認できない項目は`null`または空配列にします。画面は日本語の欠損文を表示します。公式な日本語表記を確認できない固有名詞は、原語表記のまま格納できます。

## 3. ポスター

権利を確認したファイルだけを`backend/data/posters`へ配置します。JSONには`/posters/ファイル名`を記述します。

インポーターは`http://`や`https://`の外部画像URL、親ディレクトリ参照を拒否します。画像の権利証跡はリポジトリ外の適切な場所にも保管してください。

## 4. 実行

```bash
cd backend
python scripts/import_films.py \
  --source path/to/source.json \
  --films path/to/films.json
```

同じ出典キーと`external_id`を再投入すると既存行を更新します。視聴記録が参照するローカル`id`は維持されます。

## 5. 取り込み前チェックリスト

- [ ] 提供元を記録した
- [ ] ライセンスまたは契約を読んだ
- [ ] 商用利用条件を確認した
- [ ] 再配布条件を確認した
- [ ] 長期保存やキャッシュが許可される
- [ ] 日本語説明と画像の権利を個別に確認した
- [ ] 取得日と更新方法を記録した
- [ ] 配信情報を「最新」や「リアルタイム」と誤表示しない

判断できないデータは取り込まないでください。
