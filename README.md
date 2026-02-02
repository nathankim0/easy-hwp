# easy-hwp

> Claude Code에서 한글 파일(.hwpx)을 자동으로 분석하고 작성하는 스킬

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://github.com/anthropics/claude-code)

## 설치

```bash
claude skill add nathankim0/easy-hwp
```

## 스킬 명령어

| 명령어 | 설명 |
|--------|------|
| `/hwp-analyze` | 한글 파일 구조 분석 (표, 필드, 텍스트) |
| `/hwp-fill` | 서식에 내용 채우기 |
| `/hwp-template` | 템플릿 저장/관리 |

## 사용 예시

### 서식 분석

```
/hwp-analyze IRB서식.hwpx
```

**출력:**
```
분석 완료!
- 표: 2개
- 빈 필드: 연구과제명, 연구책임자, 연구기간...
```

### 내용 채우기

```
/hwp-fill IRB서식.hwpx 연구계획.md
```

**입력 MD 형식:**
```markdown
# 연구과제명
AI 기반 의료 영상 진단 시스템 개발

## 연구책임자
홍길동

## 연구기간
2024.03.01 ~ 2025.02.28
```

### 템플릿 관리

```bash
# 템플릿 저장
/hwp-template save IRB ./IRB서식.hwpx

# 템플릿 목록
/hwp-template list

# 템플릿으로 채우기
/hwp-fill IRB 새연구계획.md
```

## 작동 방식

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  .hwpx 파일  │ ──▶ │  XML 파싱   │ ──▶ │  구조 분석   │
│  (ZIP+XML)  │     │  표/필드 추출│     │  MD로 저장   │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                           ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  MD 내용    │ ──▶ │  필드 매칭   │ ──▶ │  새 hwpx    │
│  (입력)     │     │  XML 수정   │     │  파일 생성   │
└─────────────┘     └─────────────┘     └─────────────┘
```

## 문제 해결

| 문제 | 해결 방법 |
|------|----------|
| .hwp 파일 지원 안됨 | 한글에서 .hwpx로 다시 저장 |
| 내용이 잘못된 위치에 채워짐 | `/hwp-analyze`로 구조 확인 후 조정 |
| 표가 인식 안됨 | 최신 한글에서 다시 저장 |

## 라이선스

MIT License
