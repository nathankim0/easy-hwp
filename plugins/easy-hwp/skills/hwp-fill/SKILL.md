---
name: hwp-fill
description: 한글 서식 파일(.hwpx)에 내용을 채워 새 문서를 생성합니다. "서식 채우기", "hwpx 작성", "한글 파일 채우기" 요청시 사용합니다.
---

# 한글 파일 채우기 스킬

## 사용법

```
/hwp-fill [서식파일.hwpx] [내용파일.md]
```

## 입력

$ARGUMENTS

## 핵심 동작 원리

1. **서식 파일 분석**: HWPX 파일의 표에서 필드명(첫 번째 열) 추출
2. **내용 파일 파싱**: MD 파일의 헤더(`#`, `##`)를 필드명으로, 아래 내용을 값으로 추출
3. **스마트 매칭**: 필드명을 유연하게 매칭 (아래 규칙 참조)
4. **내용 채우기**: 매칭된 필드에 값을 채워서 새 파일 생성

## 스마트 필드 매칭 규칙

**중요**: 필드명이 정확히 일치하지 않아도 다음 규칙으로 매칭하세요.

### 자동 매칭 (확신 높음)
- 정확히 일치: `연구과제명` = `연구과제명`
- 부분 포함: `과제명` → `연구과제명` 매칭 가능
- 동의어/유사어: `책임자` ≈ `연구책임자`, `기간` ≈ `연구기간`
- 띄어쓰기/특수문자 무시: `연구 과제명` = `연구과제명`

### 사용자 확인 필요 (애매한 경우)
다음 상황에서는 **반드시 사용자에게 확인**하세요:
- 여러 필드에 매칭될 수 있는 경우
- 유사하지만 의미가 다를 수 있는 경우
- 매칭할 필드를 찾지 못한 경우

**확인 예시**:
```
MD의 "목적"을 다음 중 어디에 채울까요?
1. 연구목적
2. 사업목적
3. 기타 (직접 입력)
```

### 매칭 불가
- 서식에 해당 필드가 없으면 사용자에게 알림
- 필요시 새 필드 추가 여부 확인

## 실행 절차

### 1단계: 서식 분석
```python
import zipfile
from xml.etree import ElementTree as ET

def get_hwpx_fields(file_path):
    """HWPX에서 필드명 목록 추출"""
    fields = []
    with zipfile.ZipFile(file_path, 'r') as zf:
        for name in zf.namelist():
            if 'section' in name and name.endswith('.xml'):
                root = ET.fromstring(zf.read(name))
                ns = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
                for tr in root.findall(f'.//{{{ns}}}tr'):
                    cells = list(tr.findall(f'.//{{{ns}}}tc'))
                    if len(cells) >= 2:
                        # 첫 번째 셀에서 텍스트 추출
                        texts = [t.text for t in cells[0].iter() if t.tag.endswith('}t') and t.text]
                        field_name = ' '.join(texts).strip()
                        if field_name:
                            fields.append(field_name)
    return fields
```

### 2단계: MD 파싱
```python
import re

def parse_md(content):
    """MD에서 필드-값 추출"""
    result = {}
    pattern = r'^#{1,2}\s+(.+?)$\s*((?:(?!^#{1,2}\s).+\n?)*)'
    for field, value in re.findall(pattern, content, re.MULTILINE):
        result[field.strip()] = value.strip()
    return result
```

### 3단계: 스마트 매칭
1. 서식 필드 목록과 MD 필드 목록 비교
2. 위 매칭 규칙에 따라 매칭
3. 애매한 것은 사용자에게 확인
4. 최종 매핑 테이블 생성

### 4단계: 내용 채우기
```python
def fill_hwpx(template_path, field_mapping, output_path):
    """매핑에 따라 내용 채우기"""
    # template 복사 → XML 수정 → 재압축
```

## 사용자 경험 최적화

### DO (해야 할 것)
- 매칭 결과를 먼저 보여주고 확인 받기
- 채울 수 없는 필드가 있으면 알려주기
- 완료 후 어떤 필드가 채워졌는지 요약

### DON'T (하지 말 것)
- 애매한 매칭을 사용자 확인 없이 진행하지 않기
- MD 형식이 이상해도 최대한 해석 시도하기
- 에러 발생 시 기술적 메시지 대신 쉬운 설명 제공

## 출력 예시

```
📋 매칭 결과:

✅ 자동 매칭됨:
  - "과제명" → 연구과제명
  - "책임자" → 연구책임자
  - "기간" → 연구기간

❓ 확인 필요:
  - "목적": 연구목적 / 사업목적 중 어디에 채울까요?

⚠️ 매칭 안됨:
  - "참고문헌": 서식에 해당 필드가 없습니다

진행할까요?
```

## 출력 파일

기본: `{원본파일명}_filled.hwpx`
