---
name: hwp-analyze
description: 한글 파일(.hwpx)의 구조를 분석하여 표, 필드, 텍스트 내용을 추출합니다. "hwpx 분석", "서식 분석", "한글 파일 구조" 요청시 사용합니다.
---

# 한글 파일 분석 스킬

## 사용법

```
/hwp-analyze <파일경로>
```

## 분석 대상

$ARGUMENTS

## 실행 절차

1. **파일 확인**: 입력된 파일이 .hwpx인지 확인
2. **Python 스크립트 준비**: 플러그인의 lib 디렉토리에서 hwp_core.py 사용
3. **분석 실행**: 다음 Python 코드 실행

```python
import sys
import zipfile
from xml.etree import ElementTree as ET

NAMESPACES = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
}

def analyze_hwpx(file_path):
    """HWPX 파일 분석"""
    result = {'tables': [], 'fields': [], 'texts': []}

    with zipfile.ZipFile(file_path, 'r') as zf:
        for name in zf.namelist():
            if name.startswith('Contents/section') and name.endswith('.xml'):
                with zf.open(name) as f:
                    root = ET.fromstring(f.read())

                    # 표 분석
                    for tbl in root.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}tbl'):
                        table = {'rows': [], 'row_count': 0, 'col_count': 0}
                        for tr in tbl.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}tr'):
                            row = []
                            for tc in tr.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}tc'):
                                texts = []
                                for t in tc.iter():
                                    if t.tag.endswith('}t') and t.text:
                                        texts.append(t.text)
                                row.append(' '.join(texts).strip())
                            table['rows'].append(row)
                        if table['rows']:
                            table['row_count'] = len(table['rows'])
                            table['col_count'] = len(table['rows'][0]) if table['rows'] else 0
                            result['tables'].append(table)

                    # 필드 추출 (표의 첫 열을 필드명으로)
                    for table in result['tables']:
                        if table['col_count'] >= 2:
                            for row in table['rows']:
                                if row[0]:
                                    is_empty = len(row[1].strip()) == 0 if len(row) > 1 else True
                                    result['fields'].append({
                                        'name': row[0],
                                        'value': row[1] if len(row) > 1 else '',
                                        'is_empty': is_empty
                                    })

    return result

# 실행
result = analyze_hwpx("<파일경로>")
```

4. **결과 저장**: `{파일명}_structure.md` 파일로 저장
5. **요약 제공**: 사용자에게 분석 결과 요약

## 분석 항목

- **표(table) 구조**: 행/열 수, 각 셀의 내용
- **필드 목록**: 빈 필드(채워야 할 항목)와 기존 내용이 있는 필드 구분
- **텍스트 내용**: 문단별 텍스트

## 출력 형식

```markdown
# 문서 구조 분석: {파일명}

## 빈 필드 (채워야 할 항목)
- **연구과제명**: _(빈 칸)_
- **연구책임자**: _(빈 칸)_

## 표 1 (5행 x 2열)
| 연구과제명 |  |
|---|---|
| 연구책임자 |  |
...
```

## 다음 단계 안내

분석이 완료되면 사용자에게 안내:
- `/hwp-fill` 명령으로 내용 채우기 가능
- `/hwp-template save <이름>` 으로 템플릿으로 저장 가능
