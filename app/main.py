from fastapi import FastAPI, HTTPException
import yt_dlp
import tempfile
import os
import glob
import re

app = FastAPI(title="YouTube Subtitle API")


def extract_subtitle(url: str, lang: str = "ja"):
    with tempfile.TemporaryDirectory() as tmpdir:
        ydl_opts = {
            "writesubtitles": True,
            "writeautomaticsub": True,
            "subtitleslangs": [lang],
            "skip_download": True,
            "outtmpl": os.path.join(tmpdir, "%(id)s"),
            "quiet": True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.extract_info(url, download=True)
            except Exception as e:
                raise RuntimeError(str(e))

        subtitle_files = glob.glob(os.path.join(tmpdir, "*.vtt"))

        if not subtitle_files:
            return None

        with open(subtitle_files[0], "r", encoding="utf-8") as f:
            return f.read()


_SENTENCE_ENDINGS = re.compile(r"[。？！?!]$")


def clean_vtt_to_text(vtt: str) -> str:
    """VTT字幕を読みやすいプレーンテキストに変換する。

    - WEBVTT ヘッダ・メタデータ除去
    - タイムスタンプ行除去
    - インラインタグ (<00:00:01.240><c>text</c>) 除去
    - 重複行の除去
    - 句点(。？！)で改行、それ以外は連結して改行を削減
    """
    if not vtt:
        return ""

    # インラインタイミングタグ除去: <00:00:01.240> や <c> </c>
    text = re.sub(r"<[^>]+>", "", vtt)

    lines = text.splitlines()
    deduped = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("WEBVTT"):
            continue
        if re.match(r"^(Kind|Language|Style|Region)\s*:", stripped):
            continue
        if "-->" in stripped:
            continue
        if not stripped:
            continue
        if deduped and stripped == deduped[-1]:
            continue
        deduped.append(stripped)

    # 句点で改行、それ以外は連結
    result = []
    buf = ""
    for line in deduped:
        buf += line
        if _SENTENCE_ENDINGS.search(buf):
            result.append(buf)
            buf = ""
    if buf:
        result.append(buf)

    return "\n".join(result)


@app.get("/subtitle")
def get_subtitle(url: str, format: str = "text"):
    try:
        subtitle_text = extract_subtitle(url)

        if not subtitle_text:
            raise HTTPException(status_code=404, detail="Subtitle not found")

        if format == "vtt":
            return {
                "success": True,
                "subtitle": subtitle_text,
            }

        return {
            "success": True,
            "subtitle": clean_vtt_to_text(subtitle_text),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
