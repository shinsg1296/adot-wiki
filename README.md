# 에이닷 영어학원 — AI 업무 위키

템플릿 `AI-Agent-Wiki-Template` 기반으로 만든 **운영용** Obsidian 업무 위키입니다.

여러 AI 에이전트(Claude Code·Codex 등)와 사람이 **같은 업무 맥락을 공유**하는 비즈니스 프로세스를 목표로 합니다. 개인 메모 정리가 아닙니다.

## 빠른 시작

1. Obsidian에서 이 폴더를 vault로 엽니다.
2. Claude Code 또는 Codex를 이 폴더에서 실행합니다.
3. [[START_HERE]]의 일상 운영 명령어로 시작합니다. ("옵시디언 참조" → 작업 → "저장해줘")

## 핵심 파일

- [[CLAUDE]] / [[AGENTS]] — 에이전트 업무 규약
- [[index]] — vault 지도
- [[log]] — 작업 로그
- [[START_HERE]] — 일상 운영·첫 세팅
- [[가이드라인 개요]] — 사람이 읽는 판단·품질 기준
- `prompts/` — 상황별 명령 프롬프트

## 폴더 구조

```text
├── CLAUDE.md / AGENTS.md      에이전트 규약
├── START_HERE.md / README.md / index.md / log.md
├── prompts/ / templates/ / scripts/
└── AI-Sessions/
    ├── raw/            (불변 1차 자료 — 수정 금지)
    ├── conversations/  (세션 인수인계)
    └── wiki/
        ├── guidelines/  (한국어 판단·품질 기준)
        ├── departments/ · sops/ · students/   (학원 운영)
        ├── sources/ · concepts/ · decisions/ · errors/
        └── projects/ · design/ · dev-tasks/
```

## 운영 원칙

- `raw/`는 불변, `wiki/`는 가공 지식.
- 모든 저장은 5가지 저장 필터를 통과해야 합니다(맥락 오염 방지). → [[CLAUDE]] §5
- 사람이 읽는 규칙은 한국어, 실행 키워드(save/ingest/query/lint)는 영어로 고정합니다.

## 템플릿 재배포

이 폴더는 실제 데이터가 채워진 **운영 인스턴스**입니다. 다른 곳에 새 vault를 만들 때 쓰는 **재배포용 빈 스켈레톤**의 정의(필수 파일/폴더, 배포 규칙)는 [[TEMPLATE_MANIFEST]]와 `scripts/validate-template.sh`에 있습니다. 재배포할 때는 이 운영 폴더가 아니라 빈 스켈레톤에서 시작하고, 실제 학생·고객 정보는 넣지 않습니다.
