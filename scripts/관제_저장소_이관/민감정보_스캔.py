#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
관제 저장소 이관 — 첫 커밋 전 민감정보 스캔

git add 까지 끝낸 상태에서 실행한다. **스테이징된 파일만** 검사한다.
(.gitignore 가 제대로 걸렸는지를 확인하는 게 목적이므로,
 폴더 전체가 아니라 '실제로 올라갈 것'만 봐야 의미가 있다.)

  cd <관제 폴더>
  git add -A
  python3 민감정보_스캔.py     # ← 여기서 걸리면 커밋하지 않는다
  git commit -m "..."

한 건이라도 잡히면 종료코드 1. 잡힌 파일을 .gitignore 에 추가하고 다시 돌린다.
  git rm --cached <파일>
"""
import re, subprocess, sys

# 관제 문서에서 확인된 실제 값 기준 패턴
PATTERNS = [
    ("휴대폰 번호",      re.compile(r"01[016789][-\s]?\d{3,4}[-\s]?\d{4}")),
    ("주민번호 형태",     re.compile(r"\b\d{6}[-\s]?[1-4]\d{6}\b")),
    ("비밀번호 대입",     re.compile(r"(?i)(passwd|password|pwd)\s*[=:]\s*['\"][^'\"]{3,}")),
    ("API 키 · 토큰",    re.compile(r"(?i)(api[_-]?key|secret|token|bearer)\s*[=:]\s*['\"][A-Za-z0-9_\-]{16,}")),
    ("구글 시트 ID",     re.compile(r"\b[A-Za-z0-9_-]{40,}\b")),
    ("개인 키",          re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("절대경로(윈도우)",  re.compile(r"[Cc]:\\\\?학생관리")),
    ("절대경로(리눅스)",  re.compile(r"/opt/adot-[a-z]+/")),
]

# 학생 이름이 줄줄이 있는지.
# 산문(주석·문서)에도 한글 2~4자는 널려 있으므로 **따옴표로 감싼 것만** 센다.
#   "김민성", \'김지우\'  → 명단·프로필 데이터
#   # 이름이 설정 같아도  → 주석. 안 걸린다.
HANGUL_NAME = re.compile(r"[\"\']([가-힣]{2,4})[\"\']")
NAME_THRESHOLD = 30
# 문서는 이 검사에서 제외 (코드/데이터가 아니다)
PROSE_EXT = (".md", ".gitignore", ".txt")

# 코드에 정상적으로 등장해 오탐이 나는 줄
ALLOW = re.compile(r"(?i)(example|샘플|테스트용|placeholder|000-0000|xxx|\byour_)")


def staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only"],
                         capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit("git 저장소가 아니거나 git add 를 하지 않았습니다.")
    return [f for f in out.stdout.splitlines() if f.strip()]


def main():
    files = staged_files()
    if not files:
        sys.exit("스테이징된 파일이 없습니다. 먼저 `git add -A` 를 실행하세요.")

    hits = []
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                text = fh.read()
        except (OSError, IsADirectoryError):
            continue

        for lineno, line in enumerate(text.splitlines(), 1):
            if ALLOW.search(line):
                continue
            for label, pat in PATTERNS:
                if pat.search(line):
                    hits.append((path, lineno, label, line.strip()[:80]))
                    break

        names = set() if path.endswith(PROSE_EXT) else set(HANGUL_NAME.findall(text))
        if len(names) >= NAME_THRESHOLD:
            hits.append((path, 0, f"한글 이름 {len(names)}개 — 명단/프로필 의심",
                         ", ".join(sorted(names)[:5]) + " ..."))

    print(f"스테이징된 파일 {len(files)}개 검사\n")
    if not hits:
        print("통과 — 민감정보 패턴 없음. 커밋해도 됩니다.")
        return 0

    print(f"{len(hits)}건 발견 — 커밋하지 마세요.\n")
    by_file = {}
    for hit in hits:
        by_file.setdefault(hit[0], []).append(hit)

    for path, found in by_file.items():
        print(f"  {path}  —  {len(found)}건")
        for _, lineno, label, snippet in found[:3]:
            where = f"  {lineno}행" if lineno else ""
            print(f"      [{label}]{where}  {snippet}")
        if len(found) > 3:
            print(f"      ... 외 {len(found) - 3}건")
        print()
    print("\n조치: .gitignore 에 해당 파일을 추가하고")
    print("      git rm --cached <파일>  후 다시 실행하세요.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
