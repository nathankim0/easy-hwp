---
name: hwp-template
description: 자주 사용하는 한글 서식을 템플릿으로 저장하고 관리합니다. "템플릿 저장", "서식 등록", "템플릿 목록" 요청시 사용합니다.
---

# 한글 템플릿 관리 스킬

## 사용법

```
/hwp-template <명령> [인자...]
```

## 명령어

$ARGUMENTS

### save - 템플릿 저장
```
/hwp-template save <이름> <파일경로>
```
예: `/hwp-template save IRB ./IRB서식.hwpx`

### list - 템플릿 목록
```
/hwp-template list
```

### info - 템플릿 정보
```
/hwp-template info <이름>
```

### delete - 템플릿 삭제
```
/hwp-template delete <이름>
```

## 실행 절차

1. **명령어 파싱**: 인자에서 명령과 추가 인자 분리

2. **템플릿 디렉토리 확인**: 프로젝트 루트의 `templates/` 디렉토리
   - 없으면 생성
   - `templates/index.json`에 메타데이터 저장

3. **명령 실행**:

### save 명령
```python
import json
import shutil
import os

def save_template(name, file_path, templates_dir):
    index_file = os.path.join(templates_dir, 'index.json')

    # 인덱스 로드
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {}

    # 파일 복사
    _, ext = os.path.splitext(file_path)
    template_file = os.path.join(templates_dir, f"{name}{ext}")
    shutil.copy2(file_path, template_file)

    # 문서 분석하여 필드 정보 저장
    fields = analyze_hwpx_fields(file_path)

    # 인덱스 업데이트
    index[name] = {
        'file': template_file,
        'extension': ext,
        'fields': fields
    }

    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)

    return template_file
```

### list 명령
```python
def list_templates(templates_dir):
    index_file = os.path.join(templates_dir, 'index.json')
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}
```

### info 명령
```python
def get_template_info(name, templates_dir):
    index = list_templates(templates_dir)
    return index.get(name)
```

### delete 명령
```python
def delete_template(name, templates_dir):
    index = list_templates(templates_dir)
    if name in index:
        template_file = index[name]['file']
        if os.path.exists(template_file):
            os.remove(template_file)
        del index[name]
        # 인덱스 저장
        with open(os.path.join(templates_dir, 'index.json'), 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)
        return True
    return False
```

4. **결과 안내**: 작업 결과를 사용자에게 표시

## 저장 위치

템플릿은 현재 프로젝트의 `templates/` 디렉토리에 저장:
```
templates/
├── index.json      # 템플릿 메타데이터
├── IRB.hwpx        # 저장된 템플릿 파일
└── 연구계획.hwpx   # 저장된 템플릿 파일
```

## 출력 예시

### 템플릿 저장
```
✓ 'IRB' 템플릿으로 저장되었습니다.
  - 필드 10개 감지됨
  - /hwp-fill IRB <내용.md> 로 사용 가능
```

### 템플릿 목록
```
저장된 템플릿:
1. IRB (IRB_승인신청서.hwpx) - 필드 10개
2. 연구계획 (연구계획서.hwpx) - 필드 15개
```

### 템플릿 정보
```
템플릿: IRB
파일: templates/IRB.hwpx
필드:
  - 연구과제명
  - 연구책임자
  - 소속기관
  ...
```

## 템플릿 활용

저장된 템플릿은 `/hwp-fill`에서 이름으로 사용:
```
/hwp-fill IRB 연구계획.md
```
