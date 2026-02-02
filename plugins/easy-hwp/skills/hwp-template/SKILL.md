---
name: hwp-template
description: 한글 서식을 템플릿으로 저장/관리합니다. "템플릿 저장", "서식 등록", "템플릿 목록" 요청시 사용합니다.
---

# 한글 템플릿 관리

## 입력
$ARGUMENTS

## 명령어

- `save <이름> <파일>`: 템플릿으로 저장
- `list`: 저장된 템플릿 목록
- `info <이름>`: 템플릿 상세 정보
- `delete <이름>`: 템플릿 삭제

## 해야 할 일

### save
1. 파일을 `templates/` 디렉토리에 복사
2. `templates/index.json`에 메타데이터 저장 (이름, 경로, 필드 목록)
3. 저장 완료 안내

### list
1. `templates/index.json` 읽어서 목록 표시

### info
1. 해당 템플릿의 필드 목록 등 상세 정보 표시

### delete
1. 파일 삭제, 인덱스에서 제거

## 저장 위치

```
프로젝트/templates/
├── index.json
└── {이름}.hwpx
```

## 활용

저장된 템플릿은 `/hwp-fill`에서 파일 경로 대신 이름으로 사용:
```
/hwp-fill IRB 내용.md
```
