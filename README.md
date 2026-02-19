# YouTube Subtitle API

YouTube動画の日本語字幕を取得するREST API。

## 機能

- YouTube URLから字幕テキスト(VTT形式)を取得
- 手動字幕を優先、なければ自動生成字幕にフォールバック
- 対象言語: 日本語(`ja`)

## エンドポイント

### `GET /subtitle?url={youtube_url}`

| パラメータ | 型 | 必須 | 説明 |
|---|---|---|---|
| `url` | string | Yes | YouTube動画のURL |

**レスポンス例**

```json
{"success": true, "subtitle": "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nこんにちは..."}
```

| ステータス | 条件 |
|---|---|
| 200 | 字幕取得成功 |
| 404 | 字幕が見つからない |
| 422 | `url`パラメータ未指定 |
| 500 | 内部エラー(yt-dlp失敗等) |

## セットアップ

```bash
make install   # 依存インストール
make dev       # 開発サーバ起動 (localhost:10000, auto-reload)
make test      # テスト実行
```

## Docker

```bash
make build     # docker build
make run       # docker run (port 10000)
```

## ファイル構成

```
├── app/
│   ├── main.py                  # FastAPIアプリ本体（エンドポイント + 字幕取得ロジック）
│   └── requirements.txt         # 本番用依存パッケージ
├── tests/
│   ├── conftest.py              # pytest共通フィクスチャ（TestClient）
│   ├── test_subtitle_api.py     # エンドポイントのテスト（200/404/422/500）
│   └── test_extract_subtitle.py # extract_subtitle関数の単体テスト
├── Dockerfile                   # Docker構成（python:3.11-slim + ffmpeg）
├── Makefile                     # 開発用コマンド集（dev/test/build等）
├── api.http                     # APIリクエスト例（VSCode REST Client用）
├── pytest.ini                   # pytest設定（pythonpath, testpaths）
├── requirements-dev.txt         # 開発用依存（pytest, httpx含む）
├── 基礎設計.md                   # 設計仕様書
└── README.md                    # このファイル
```

## 技術スタック

Python 3.11 / FastAPI / yt-dlp / ffmpeg
