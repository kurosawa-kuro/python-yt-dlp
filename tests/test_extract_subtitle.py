"""extract_subtitle 関数の単体テスト（yt-dlp をモック）"""

import os
from unittest.mock import patch, MagicMock

from main import extract_subtitle


def _write_vtt(tmpdir_path: str, filename: str, content: str):
    """ヘルパー: tmpdir に VTT ファイルを作成"""
    path = os.path.join(tmpdir_path, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


class TestExtractSubtitle:

    def test_returns_vtt_content(self, tmp_path):
        """VTT ファイルが生成された場合、その内容を返す"""
        vtt_content = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nテスト字幕"

        def fake_extract(url, download=True):
            _write_vtt(str(tmp_path), "video123.ja.vtt", vtt_content)
            return {"id": "video123"}

        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info = fake_extract

        with patch("main.tempfile.TemporaryDirectory") as mock_tmpdir, \
             patch("main.yt_dlp.YoutubeDL", return_value=mock_ydl):
            mock_tmpdir.return_value.__enter__ = MagicMock(return_value=str(tmp_path))
            mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)

            result = extract_subtitle("https://www.youtube.com/watch?v=video123")

        assert result is not None
        assert "テスト字幕" in result

    def test_returns_none_when_no_subtitle(self, tmp_path):
        """VTT ファイルが無い場合は None を返す"""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info = MagicMock(return_value={"id": "video123"})

        with patch("main.tempfile.TemporaryDirectory") as mock_tmpdir, \
             patch("main.yt_dlp.YoutubeDL", return_value=mock_ydl):
            mock_tmpdir.return_value.__enter__ = MagicMock(return_value=str(tmp_path))
            mock_tmpdir.return_value.__exit__ = MagicMock(return_value=False)

            result = extract_subtitle("https://www.youtube.com/watch?v=nosub")

        assert result is None

    def test_raises_on_ytdlp_error(self):
        """yt-dlp がエラーを投げた場合 RuntimeError を送出"""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info = MagicMock(side_effect=Exception("network error"))

        with patch("main.yt_dlp.YoutubeDL", return_value=mock_ydl):
            try:
                extract_subtitle("https://www.youtube.com/watch?v=err")
                assert False, "RuntimeError should have been raised"
            except RuntimeError as e:
                assert "network error" in str(e)

    def test_default_lang_is_ja(self):
        """デフォルト言語は ja"""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.extract_info = MagicMock(return_value={"id": "v"})

        captured_opts = {}

        def capture_opts(opts):
            captured_opts.update(opts)
            return mock_ydl

        with patch("main.yt_dlp.YoutubeDL", side_effect=capture_opts):
            extract_subtitle("https://www.youtube.com/watch?v=test")

        assert captured_opts["subtitleslangs"] == ["ja"]
