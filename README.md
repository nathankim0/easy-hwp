# easy-hwp

> Claude Code에서 한글 파일(.hwpx)을 자동으로 분석하고 작성하는 스킬

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-blue)](https://github.com/anthropics/claude-code)

## 설치

Claude Code에서:

```
/plugin marketplace add nathankim0/easy-hwp
/plugin install easy-hwp@nathankim0-easy-hwp
```

## 사용법

설치 후 **자연어로 요청**하면 됩니다:

```
연구계획.md 내용을 IRB서식.hwpx에 채워줘
```

```
신청서.hwpx 구조 분석해줘
```

```
보고서.md를 출장신청서.hwpx에 입력해서 결과.hwpx로 저장해줘
```

## 슬래시 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `/hwp-analyze` | 한글 파일 구조 분석 | `/hwp-analyze 서식.hwpx` |
| `/hwp-fill` | 서식에 내용 채우기 | `/hwp-fill 서식.hwpx 내용.md` |
| `/hwp-template` | 템플릿 저장/관리 | `/hwp-template list` |

## 입력 파일 형식

**MD 파일 (채울 내용):**
```markdown
# 연구과제명
AI 기반 의료 영상 진단 시스템 개발

## 연구책임자
홍길동

## 연구기간
2024.03.01 ~ 2025.02.28
```

**HWPX 파일 (서식):**
- 한글에서 저장한 .hwpx 파일
- 표 안의 빈 칸을 자동으로 인식해서 채움

## 작동 방식

```
HWPX 서식 ──▶ 구조 분석 ──▶ MD 내용 매칭 ──▶ 새 HWPX 생성
```

## 문제 해결

| 문제 | 해결 |
|------|------|
| .hwp 지원 안됨 | 한글에서 .hwpx로 다시 저장 |
| 잘못된 위치에 채워짐 | `/hwp-analyze`로 구조 확인 |

## 라이선스

MIT License
