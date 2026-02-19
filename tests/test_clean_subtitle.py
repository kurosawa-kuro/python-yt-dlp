"""clean_vtt_to_text 関数のテスト"""

from main import clean_vtt_to_text


class TestCleanVttToText:

    def test_removes_vtt_header(self):
        """WEBVTT ヘッダとメタデータ行を除去"""
        vtt = "WEBVTT\nKind: captions\nLanguage: ja\n\n00:00:01.000 --> 00:00:02.000\nこんにちは"
        result = clean_vtt_to_text(vtt)
        assert "WEBVTT" not in result
        assert "Kind:" not in result
        assert "Language:" not in result
        assert "こんにちは" in result

    def test_removes_timestamp_lines(self):
        """タイムスタンプ行を除去"""
        vtt = "WEBVTT\n\n00:00:01.000 --> 00:00:02.000 align:start position:0%\nテスト"
        result = clean_vtt_to_text(vtt)
        assert "-->" not in result
        assert "align:start" not in result
        assert "テスト" in result

    def test_removes_inline_timing_tags(self):
        """<00:00:01.240><c>text</c> 形式のタグを除去しテキストだけ残す"""
        vtt = (
            "WEBVTT\n\n"
            "00:00:00.919 --> 00:00:02.830\n"
            "こんにちは<00:00:01.240><c>。</c><00:00:01.319><c>経済</c>"
        )
        result = clean_vtt_to_text(vtt)
        assert "<" not in result
        assert ">" not in result
        assert "こんにちは。経済" in result

    def test_deduplicates_consecutive_lines(self):
        """連続する重複行を1行にまとめる"""
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:02.000\nあいう\n\n"
            "00:00:02.000 --> 00:00:03.000\nあいう\n\n"
            "00:00:03.000 --> 00:00:04.000\nえおか\n"
        )
        result = clean_vtt_to_text(vtt)
        assert result.count("あいう") == 1
        assert "えおか" in result

    def test_real_world_vtt_fragment(self):
        """実際のYouTube自動字幕VTTフラグメントを整形"""
        vtt = (
            "WEBVTT\n"
            "Kind: captions\n"
            "Language: ja\n\n"
            "00:00:00.919 --> 00:00:02.830 align:start position:0%\n"
            " \n"
            "こんにちは<00:00:01.240><c>。</c><00:00:01.319><c>経済</c><00:00:01.560><c>カブ</c><00:00:01.760><c>の</c><00:00:01.880><c>小崎</c><00:00:02.280><c>です</c><00:00:02.440><c>。</c>\n\n"
            "00:00:02.830 --> 00:00:02.840 align:start position:0%\n"
            "こんにちは。経済カブの小崎です。\n"
            " \n\n"
            "00:00:02.840 --> 00:00:05.710 align:start position:0%\n"
            "こんにちは。経済カブの小崎です。\n"
            "ロスチャイルド<00:00:03.639><c>怪我</c><00:00:03.760><c>が</c><00:00:03.919><c>世界</c><00:00:04.279><c>を</c><00:00:04.480><c>支配</c><00:00:04.799><c>し</c><00:00:04.920><c>て</c><00:00:05.000><c>いる</c>\n\n"
            "00:00:05.710 --> 00:00:05.720 align:start position:0%\n"
            "ロスチャイルド怪我が世界を支配している\n"
            " \n"
        )
        result = clean_vtt_to_text(vtt)
        assert "<" not in result
        assert "-->" not in result
        assert "こんにちは。経済カブの小崎です。" in result
        assert "ロスチャイルド怪我が世界を支配している" in result
        assert result.count("こんにちは。経済カブの小崎です。") == 1

    def test_empty_input(self):
        """空文字列は空文字列を返す"""
        assert clean_vtt_to_text("") == ""

    def test_sentence_end_causes_newline(self):
        """句点(。?！)で改行し、それ以外は連結して改行を減らす"""
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:02.000\n最初の文。\n\n"
            "00:00:02.000 --> 00:00:03.000\n次の文。\n\n"
            "00:00:03.000 --> 00:00:04.000\n続きの\n\n"
            "00:00:04.000 --> 00:00:05.000\nテキスト。\n"
        )
        result = clean_vtt_to_text(vtt)
        # 句点で改行される
        assert "最初の文。\n" in result
        assert "次の文。\n" in result
        # 句点がない行は次の行と連結される
        assert "続きのテキスト。" in result

    def test_no_excessive_newlines(self):
        """連続する改行が2つ以上にならない"""
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:02.000\nあ。\n\n"
            "00:00:05.000 --> 00:00:06.000\nい。\n"
        )
        result = clean_vtt_to_text(vtt)
        assert "\n\n" not in result
