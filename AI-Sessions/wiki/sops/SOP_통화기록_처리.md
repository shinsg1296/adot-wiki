---
type: sop
date: 2026-06-07
status: active
---

# SOP: 통화 기록 자동 처리

담당: [[3_상담소통부]] (유지보수: [[5_시스템개발부]])

## 파이프라인

```
휴대폰 통화 → Tasker(RAW 녹음) → Google Drive 업로드
→ Gemini 전사 (B11 수식) → AppsScript → 스프레드시트 DB 기록
```

- Drive 폴더 / 스프레드시트 / API 키 위치: 메모리 call_automation_pipeline 참조
- DB 컬럼 매핑 준수

## 수업 녹음 → 수업일지 워크플로우

1. 수업 중 녹음 (학생 이름 호명으로 구분)
2. 수업 전용 Drive 폴더에 업로드 → 전사 (통화녹음 폴더와 분리)
3. 에이전트가 전사본 읽고 학생별 4필드 작성 → [[SOP_수업일지_작성]]
