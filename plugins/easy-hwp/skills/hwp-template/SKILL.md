---
name: hwp-template
description: 한글 서식을 템플릿으로 저장/관리합니다. "템플릿 저장", "서식 등록", "템플릿 목록" 요청시 사용합니다.
---

# 한글 템플릿 관리

## 입력
$ARGUMENTS

## 명령어

| 명령어 | 설명 | 예시 |
|--------|------|------|
| `save <이름> <파일>` | 템플릿으로 저장 | `/hwp-template save IRB IRB서식.hwpx` |
| `list` | 저장된 템플릿 목록 | `/hwp-template list` |
| `info <이름>` | 템플릿 상세 정보 | `/hwp-template info IRB` |
| `delete <이름>` | 템플릿 삭제 | `/hwp-template delete IRB` |

## 저장 위치

템플릿은 **현재 프로젝트 디렉토리** 기준으로 저장:

```
{프로젝트}/
└── templates/
    ├── index.json      # 템플릿 메타데이터
    └── {이름}.hwpx     # 템플릿 파일들
```

## 처리 절차

### save

1. `templates/` 디렉토리가 없으면 생성
2. 파일을 `templates/{이름}.hwpx`로 복사
3. 템플릿 분석하여 필드 목록 추출
4. `templates/index.json`에 메타데이터 저장:

```json
{
  "templates": [
    {
      "name": "IRB",
      "file": "IRB.hwpx",
      "fields": ["연구과제명", "연구책임자", "연구기간"],
      "created": "2024-01-15"
    }
  ]
}
```

### list

1. `templates/index.json` 읽기
2. 템플릿 목록을 표 형식으로 표시:

```
템플릿 목록:
| 이름 | 필드 수 | 등록일 |
|------|---------|--------|
| IRB  | 15개    | 2024-01-15 |
```

### info

1. `templates/index.json`에서 해당 템플릿 찾기
2. 상세 정보 표시:
   - 이름, 파일 경로
   - 필드 목록 (채워야 할 항목들)
   - 등록일

### delete

1. `templates/{이름}.hwpx` 파일 삭제
2. `templates/index.json`에서 항목 제거
3. 삭제 완료 안내

## 활용

저장된 템플릿은 `/hwp-fill`에서 파일 경로 대신 이름으로 사용:

```
/hwp-fill IRB 내용.md
```

→ `templates/IRB.hwpx`를 자동으로 찾아서 사용

## 주의사항

- 템플릿 이름은 영문/한글/숫자만 허용 (특수문자 불가)
- 동일한 이름으로 저장 시 기존 템플릿 덮어쓰기 확인
- `templates/` 디렉토리는 `.gitignore`에 추가 권장 (개인 서식이므로)
