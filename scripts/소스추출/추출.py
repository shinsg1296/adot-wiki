#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
배포된 웹앱에서 원본 소스 추출 (소스맵 기반)

Next.js·Vite 등으로 빌드된 사이트가 소스맵(.js.map)을 함께 올려두면,
그 안에 **원본 .tsx/.ts/.css 전문**이 들어 있다. 이 스크립트는 그걸 파일로 복원한다.
v0·Lovable·Bolt로 만든 사이트는 소스맵이 켜져 있는 경우가 많다.

사용:
    python3 추출.py https://example.vercel.app/dashboard
    python3 추출.py https://example.vercel.app/dashboard -o 내폴더

필요: 파이썬 3.8+ (표준 라이브러리만 사용 — 설치할 것 없음)

소스맵이 없으면 아무것도 못 가져온다. 그 경우 화면을 보고 다시 만드는 수밖에 없다.
"""
import argparse
import gzip
import json
import os
import re
import sys
import urllib.error
import urllib.request
from urllib.parse import urljoin, urlparse

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " \
     "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"

SCRIPT_SRC = re.compile(r'<script[^>]+src=["\']([^"\']+)["\']', re.I)
LINK_HREF = re.compile(r'<link[^>]+href=["\']([^"\']+\.css)["\']', re.I)
# 번들 끝의 //# sourceMappingURL=... 주석
MAP_COMMENT = re.compile(r'//[#@]\s*sourceMappingURL=(\S+)')


def fetch(url, timeout=30):
    """URL을 가져와 bytes 로 돌려준다. 실패하면 None."""
    req = urllib.request.Request(url, headers={"User-Agent": UA,
                                               "Accept-Encoding": "gzip"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return raw
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"    ! HTTP {e.code}  {url}")
        return None
    except Exception as e:
        print(f"    ! {type(e).__name__}  {url}")
        return None


def safe_path(out_dir, source_name):
    """소스맵의 경로를 안전한 로컬 경로로 바꾼다 (../ 탈출 차단)."""
    name = source_name
    for prefix in ("webpack://", "webpack-internal:///", "file://"):
        if name.startswith(prefix):
            name = name[len(prefix):]
    name = name.split("?")[0].lstrip("/")
    # _N_E 같은 Next.js 네임스페이스 접두어 제거
    name = re.sub(r"^_N_E/", "", name)
    parts = [p for p in name.split("/") if p not in ("", ".", "..")]
    if not parts:
        return None
    path = os.path.join(out_dir, *parts)
    # out_dir 밖으로 나가지 않는지 최종 확인
    if not os.path.abspath(path).startswith(os.path.abspath(out_dir) + os.sep):
        return None
    return path


def extract_map(map_bytes, out_dir):
    """소스맵 하나에서 sourcesContent 를 파일로 쓴다. (쓴 수, 내용없음 수)"""
    try:
        data = json.loads(map_bytes.decode("utf-8", "replace"))
    except json.JSONDecodeError:
        return 0, 0

    sources = data.get("sources") or []
    contents = data.get("sourcesContent") or []
    written = empty = 0

    for i, src in enumerate(sources):
        body = contents[i] if i < len(contents) else None
        if not body:
            empty += 1
            continue
        # node_modules 는 남의 라이브러리라 건너뛴다
        if "node_modules" in src:
            continue
        path = safe_path(out_dir, src)
        if not path:
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        written += 1
    return written, empty


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="추출할 페이지 주소")
    ap.add_argument("-o", "--out", default="추출된_소스", help="저장 폴더")
    args = ap.parse_args()

    print(f"페이지: {args.url}")
    html_bytes = fetch(args.url)
    if not html_bytes:
        sys.exit("페이지를 가져오지 못했습니다. 주소를 확인하세요.")
    html = html_bytes.decode("utf-8", "replace")

    # 페이지에 걸린 번들 목록
    assets = set()
    for m in SCRIPT_SRC.finditer(html):
        assets.add(urljoin(args.url, m.group(1)))
    for m in LINK_HREF.finditer(html):
        assets.add(urljoin(args.url, m.group(1)))
    assets = {a for a in assets if urlparse(a).netloc == urlparse(args.url).netloc}
    print(f"번들 {len(assets)}개 발견\n")

    total_written = total_empty = maps_found = 0

    for asset in sorted(assets):
        short = urlparse(asset).path
        body = fetch(asset)
        if not body:
            continue

        # 번들 안의 sourceMappingURL 주석을 우선 따르고, 없으면 .map 을 찍어본다
        candidates = []
        tail = body[-2048:].decode("utf-8", "replace")
        m = MAP_COMMENT.search(tail)
        if m and not m.group(1).startswith("data:"):
            candidates.append(urljoin(asset, m.group(1)))
        candidates.append(asset + ".map")

        for map_url in candidates:
            map_bytes = fetch(map_url)
            if not map_bytes:
                continue
            written, empty = extract_map(map_bytes, args.out)
            maps_found += 1
            total_written += written
            total_empty += empty
            mark = f"{written}개 복원" if written else "내용 없음"
            print(f"  [맵] {short}  →  {mark}")
            break
        else:
            print(f"  [ - ] {short}")

    print()
    if total_written:
        print(f"완료 — 소스맵 {maps_found}개에서 파일 {total_written}개를 '{args.out}/' 에 복원했습니다.")
        if total_empty:
            print(f"      (본문이 비어 있던 항목 {total_empty}개는 건너뜀)")
        print("\n다음: 그 폴더를 통째로 압축해서 저에게 주시면 구조를 분석하겠습니다.")
    else:
        print("소스맵이 없습니다. 원본 코드는 못 가져옵니다.")
        print("→ 화면(HTML/CSS)만 가져와 다시 만드는 방향으로 가야 합니다.")
    return 0 if total_written else 2


if __name__ == "__main__":
    sys.exit(main())
