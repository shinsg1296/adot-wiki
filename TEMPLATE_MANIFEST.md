# Template Manifest

## Name

AI-Agent-Wiki-Template

## Version

1.0.0

## Purpose

이 매니페스트는 **재배포용 빈 스켈레톤**(더미 데이터 없는 상태)의 정의입니다. 필수 파일·폴더 목록과 배포 규칙을 정합니다.

> 참고: 현재 이 폴더는 에이닷 영어학원 **운영용 인스턴스**로, 실제 학생·운영 데이터가 채워져 있습니다. 아래 "Required" 목록은 새 vault를 처음부터 만들거나 빈 템플릿으로 재배포할 때의 기준입니다.

Claude Code, Codex, 기타 AI 에이전트가 동일한 업무 맥락을 공유하고, 저장과 참조를 반복 가능한 프로세스로 운영하도록 돕습니다.

## Required Files

- `README.md`
- `START_HERE.md`
- `CLAUDE.md`
- `AGENTS.md`
- `index.md`
- `log.md`
- `VERSION`
- `LICENSE.md`

## Required Directories

- `AI-Sessions/raw/`
- `AI-Sessions/conversations/`
- `AI-Sessions/wiki/sources/`
- `AI-Sessions/wiki/concepts/`
- `AI-Sessions/wiki/decisions/`
- `AI-Sessions/wiki/errors/`
- `AI-Sessions/wiki/projects/`
- `AI-Sessions/wiki/design/`
- `AI-Sessions/wiki/dev-tasks/`
- `AI-Sessions/wiki/guidelines/`
- `prompts/`
- `scripts/`

## Distribution Rule

배포 ZIP에는 실제 고객 정보, 실제 프로젝트 자료, API 키, 토큰, 개인 메모, 예시 회의록을 넣지 않습니다.

## First Prompt

첫 실행 프롬프트는 `START_HERE.md`와 `prompts/first-setup.md`에 있습니다.
