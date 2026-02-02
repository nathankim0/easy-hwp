# easyhwp - 한글 파일 자동 작성 도구

비개발자도 Claude Code에서 쉽게 사용할 수 있는 **범용 한글 파일(.hwp/.hwpx) 자동 작성 도구**입니다.

## 스킬 명령어

| 명령어 | 설명 | 사용 예시 |
|--------|------|-----------|
| `/hwp-analyze` | 한글 파일 구조 분석 | `/hwp-analyze IRB서식.hwpx` |
| `/hwp-fill` | 서식에 내용 채우기 | `/hwp-fill IRB서식.hwpx 연구계획.md` |
| `/hwp-template` | 템플릿 관리 | `/hwp-template save IRB ./서식.hwpx` |

## 지원 환경

| 형식 | Mac | Windows | Windows + 한글 |
|------|-----|---------|----------------|
| .hwpx | ✅ | ✅ | ✅ |
| .hwp | ❌ | ❌ | ✅ |

> .hwpx는 ZIP 기반 XML 형식으로 어디서든 처리 가능합니다.
> .hwp는 Windows에서 한글 프로그램이 설치되어 있어야 합니다.

## 빠른 시작

### 1. 서식 분석하기

```
/hwp-analyze ./연구계획서.hwpx
```

분석 결과:
- 표 구조 (행/열)
- 빈 필드 목록 (채워야 할 항목)
- 기존 내용

### 2. 내용 채우기

```
/hwp-fill ./연구계획서.hwpx ./내용.md
```

또는 대화로:

```
/hwp-fill ./연구계획서.hwpx
> 연구과제명: 스마트 헬스케어 시스템
> 연구책임자: 홍길동
```

### 3. 템플릿으로 저장

```
/hwp-template save IRB ./연구계획서.hwpx
```

다음부터는:

```
/hwp-fill IRB ./새로운내용.md
```

## 파일 구조

```
/Users/nathan/easyhwp/
├── hwpx_parser.py   # HWPX 파싱 (크로스 플랫폼)
├── hwp_parser.py    # HWP 파싱 (Windows 전용)
├── hwp_core.py      # 통합 인터페이스
├── templates/       # 저장된 템플릿
└── README.md

~/.claude/commands/
├── hwp-analyze.md   # 분석 스킬
├── hwp-fill.md      # 채우기 스킬
└── hwp-template.md  # 템플릿 스킬
```

## MD 파일 형식

내용 파일은 다음 형식을 사용하세요:

```markdown
# 연구과제명
스마트 헬스케어 시스템 개발

## 연구책임자
홍길동

## 연구기간
2024.01.01 ~ 2024.12.31
```

헤더(`#`, `##`)가 필드명으로 인식되고, 그 아래 내용이 값으로 사용됩니다.

## 문제 해결

### "지원하지 않는 파일 형식" 오류
- .hwp 파일을 Mac에서 사용하려는 경우
- 해결: 한글 프로그램에서 .hwpx로 다시 저장

### 내용이 잘못된 위치에 채워짐
- 표 구조가 복잡한 경우 발생
- 해결: `/hwp-analyze`로 구조 확인 후 수동 조정

### 표가 인식되지 않음
- 비표준 HWPX 형식일 수 있음
- 해결: 최신 버전 한글에서 다시 저장

## 기술 정보

### HWPX 파일 구조
```
hwpx 파일 (ZIP)
├── Contents/
│   ├── section0.xml  # 본문 (표, 텍스트)
│   ├── section1.xml
│   └── ...
├── settings.xml
└── META-INF/
```

### 주요 XML 요소
- `<hp:tbl>`: 표
- `<hp:tr>`: 행
- `<hp:tc>`: 셀
- `<hp:t>`: 텍스트
