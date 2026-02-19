"""GET /subtitle エンドポイントのテスト"""

from unittest.mock import patch


# --- 正常系 ---

def test_subtitle_success_default_text(client):
    """デフォルト(format=text)ではクリーニング済みテキストを返す"""
    fake_vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nこんにちは"

    with patch("main.extract_subtitle", return_value=fake_vtt):
        resp = client.get("/subtitle", params={"url": "https://www.youtube.com/watch?v=test123"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["subtitle"] == "こんにちは"


def test_subtitle_success_vtt_format(client):
    """format=vtt では生VTTをそのまま返す"""
    fake_vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nこんにちは"

    with patch("main.extract_subtitle", return_value=fake_vtt):
        resp = client.get("/subtitle", params={"url": "https://www.youtube.com/watch?v=test123", "format": "vtt"})

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["subtitle"] == fake_vtt


# --- 異常系 ---

def test_missing_url_returns_422(client):
    """url パラメータ未指定は 422"""
    resp = client.get("/subtitle")
    assert resp.status_code == 422


def test_subtitle_not_found_returns_404(client):
    """字幕が見つからない場合は 404"""
    with patch("main.extract_subtitle", return_value=None):
        resp = client.get("/subtitle", params={"url": "https://www.youtube.com/watch?v=nosub"})

    assert resp.status_code == 404
    assert "not found" in resp.json()["detail"].lower()


def test_ytdlp_error_returns_500(client):
    """yt-dlp 内部エラー時は 500"""
    with patch("main.extract_subtitle", side_effect=RuntimeError("yt-dlp failed")):
        resp = client.get("/subtitle", params={"url": "https://www.youtube.com/watch?v=broken"})

    assert resp.status_code == 500
