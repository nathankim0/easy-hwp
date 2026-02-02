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

## 핵심 동작

1. HWPX 파일(ZIP) 압축 해제
2. section*.xml에서 표와 텍스트 추출
3. 필드명과 현재 값 파악
4. 사용자에게 쉽게 설명

## 분석 코드

```python
import zipfile
from xml.etree import ElementTree as ET

def analyze_hwpx(file_path):
    result = {'tables': [], 'fields': []}

    with zipfile.ZipFile(file_path, 'r') as zf:
        for name in zf.namelist():
            if 'section' in name and name.endswith('.xml'):
                root = ET.fromstring(zf.read(name))
                ns = 'http://www.hancom.co.kr/hwpml/2011/paragraph'

                for tbl in root.findall(f'.//{{{ns}}}tbl'):
                    table = {'rows': []}
                    for tr in tbl.findall(f'.//{{{ns}}}tr'):
                        row = []
                        for tc in tr.findall(f'.//{{{ns}}}tc'):
                            texts = [t.text for t in tc.iter() if t.tag.endswith('}t') and t.text]
                            row.append(' '.join(texts).strip())
                        table['rows'].append(row)
                    result['tables'].append(table)

                    # 2열 표면 필드로 인식
                    if table['rows'] and len(table['rows'][0]) >= 2:
                        for row in table['rows']:
                            if row[0]:
                                result['fields'].append({
                                    'name': row[0],
                                    'value': row[1] if len(row) > 1 else '',
                                    'is_empty': not (row[1].strip() if len(row) > 1 else False)
                                })
    return result
```

## 출력 형식

분석 결과를 **사용자가 이해하기 쉽게** 설명하세요:

```
📄 IRB서식.hwpx 분석 완료!

📊 표 2개 발견

✏️ 채워야 할 필드 (빈 칸):
  • 연구과제명
  • 연구책임자
  • 연구기간
  • 연구목적
  • 연구방법

📝 이미 채워진 필드:
  • 신청일자: 2024.01.15
  • 서식번호: IRB-001

💡 다음 단계:
  /hwp-fill IRB서식.hwpx 내용.md
  또는 채워넣을 내용을 직접 알려주세요.
```

## 주의사항

- .hwp 파일은 .hwpx로 변환 필요 (한글 → 다른 이름으로 저장 → HWPX)
- 복잡한 표(병합 셀)는 구조가 다르게 보일 수 있음
- 분석 결과 저장 필요시 `{파일명}_structure.md`로 저장
