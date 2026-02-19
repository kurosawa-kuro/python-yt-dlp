# Render デプロイ手順

## 前提

- GitHubリポジトリ `python-yt-dlp` にコードがpush済み
- Renderアカウント作成済み

## 手順

### 1. New Web Service 作成

Render Dashboard → **New** → **Web Service**

### 2. 設定値

| 項目 | 値 |
|---|---|
| Source Code | `kurosawa-kuro/python-yt-dlp` |
| Name | `python-yt-dlp` |
| Language | **Docker** |
| Branch | `master` |
| Region | Singapore (Southeast Asia) |
| Instance Type | Free ($0/month) |

- Root Directory: 空欄（リポジトリ直下にDockerfileがあるためそのまま）
- Environment Variables: 設定不要

### 3. デプロイ

**Deploy web service** ボタンを押す。

Renderが自動でDockerfileを検出し、ビルド→デプロイを実行する。
ポート10000はDockerfile内の `CMD` で指定済み。

### 4. 動作確認

デプロイ完了後、RenderのURLにアクセス:

```
https://python-yt-dlp.onrender.com/subtitle?url=https://www.youtube.com/watch?v=VIDEO_ID
```

Swagger UIで確認する場合:

```
https://python-yt-dlp.onrender.com/docs
```

## 注意点（Free プラン）

| 制限 | 内容 |
|---|---|
| コールドスタート | 15分間アクセスがないとスリープ。次回アクセスで起動に数十秒かかる |
| リクエストタイムアウト | 最大15分 |
| IP制限 | YouTubeがデータセンターIPをブロックする可能性あり |

### IP制限への対策

字幕取得が失敗する場合:

1. **cookies.txt** — ブラウザのYouTubeクッキーをエクスポートし、コンテナに配置
2. **VPS運用** — 住宅用IPのVPSに移行
3. **Residential Proxy** — プロキシ経由でアクセス
