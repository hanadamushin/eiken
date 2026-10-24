"""eiken-pre1-desk.html (claude.ai 版) から GitHub Pages 用のファイル一式を docs/ に作る。

使い方:  python build_pages.py
アプリを直したら、このスクリプトをもう一度実行して docs/ ごと GitHub に push し直す。
"""
import json
import time
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "eiken-pre1-desk.html"
OUT = ROOT / "docs"
NAME = "準1級 合格デスク"
SHORT = "合格デスク"
RED = "#C42F3B"

# claude.ai が公開時に自動で付けている部分（文字コード・画面幅・最小のリセット）を自前で付ける
RESET = (":root{color-scheme:light;padding-top:env(safe-area-inset-top,0px);"
         "padding-bottom:env(safe-area-inset-bottom,0px)}"
         "body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}"
         "[hidden]{display:none!important}")


def build_html(src: str) -> str:
    head_part, sep, body_part = src.partition("<header")
    if not sep:
        raise SystemExit("eiken-pre1-desk.html に <header が見つかりません")
    return f"""<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="{RED}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="{SHORT}">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="icon-180.png">
<style>{RESET}</style>
{head_part.strip()}
</head>
<body>
<header{body_part.rstrip()}
<script>
if ('serviceWorker' in navigator) navigator.serviceWorker.register('sw.js').catch(() => {{}});
</script>
</body>
</html>
"""


ICON_SVG = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
<rect width="512" height="512" rx="112" fill="{RED}"/>
<text x="256" y="318" text-anchor="middle" font-family="Hiragino Sans,Yu Gothic,Noto Sans JP,sans-serif" font-weight="900" font-size="200" fill="#fff">準1</text>
</svg>
"""


def png_icon(size: int, path: Path, maskable: bool = False) -> None:
    from PIL import Image, ImageDraw, ImageFont

    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if maskable:
        d.rectangle([0, 0, size, size], fill=RED)
    else:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=int(size * 0.22), fill=RED)
    font = None
    for f in ["C:/Windows/Fonts/YuGothB.ttc", "C:/Windows/Fonts/meiryob.ttc", "C:/Windows/Fonts/msgothic.ttc",
              "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]:
        try:
            font = ImageFont.truetype(f, int(size * (0.30 if maskable else 0.38)))
            break
        except OSError:
            continue
    if font is None:
        font = ImageFont.load_default()
    text = "準1"
    box = d.textbbox((0, 0), text, font=font)
    w, h = box[2] - box[0], box[3] - box[1]
    d.text(((size - w) / 2 - box[0], (size - h) / 2 - box[1]), text, font=font, fill="white")
    img.save(path)


def main() -> None:
    OUT.mkdir(exist_ok=True)
    (OUT / "index.html").write_text(build_html(SRC.read_text(encoding="utf-8")), encoding="utf-8")
    (OUT / "icon.svg").write_text(ICON_SVG, encoding="utf-8")
    try:
        png_icon(180, OUT / "icon-180.png")
        png_icon(192, OUT / "icon-192.png")
        png_icon(512, OUT / "icon-512.png")
        png_icon(512, OUT / "icon-maskable.png", maskable=True)
        icons = [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png"},
                 {"src": "icon-512.png", "sizes": "512x512", "type": "image/png"},
                 {"src": "icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]
    except ImportError:
        print("Pillow がないため PNG アイコンは作りませんでした（pip install pillow で作れます）")
        icons = []
    icons.append({"src": "icon.svg", "sizes": "any", "type": "image/svg+xml"})
    manifest = {
        "name": NAME, "short_name": SHORT, "lang": "ja",
        "description": "英検準1級の対策アプリ。苦手語クイズ・TODO・学習記録・過去問スコア・英作文練習。",
        "start_url": "./", "scope": "./", "display": "standalone",
        "background_color": "#EDF0F3", "theme_color": RED, "icons": icons,
    }
    (OUT / "manifest.webmanifest").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    cached = ["./", "./index.html", "./manifest.webmanifest", "./icon.svg"] + [f"./{i['src']}" for i in icons if i["src"].endswith(".png")]
    version = time.strftime("%Y%m%d%H%M%S")
    (OUT / "sw.js").write_text(SW.replace("__VERSION__", version).replace("__FILES__", json.dumps(cached)), encoding="utf-8")
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print(f"docs/ を作りました（版 {version}）")


# オフラインでも開けるようにする。アプリ本体はネット優先（更新がすぐ届く）、フォントは一度読んだら手元から。
SW = """const CACHE = 'goukaku-desk-__VERSION__';
const FILES = __FILES__;
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin === location.origin) {
    e.respondWith(fetch(req).then(res => {
      const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res;
    }).catch(() => caches.match(req).then(r => r || caches.match('./index.html'))));
  } else if (url.hostname.endsWith('fonts.googleapis.com') || url.hostname.endsWith('fonts.gstatic.com')) {
    e.respondWith(caches.match(req).then(r => r || fetch(req).then(res => {
      const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res;
    })));
  }
});
"""

if __name__ == "__main__":
    main()
