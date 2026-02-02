---
name: hwp-fill
description: 한글 서식 파일(.hwpx)에 내용을 채워 새 문서를 생성합니다. "서식 채우기", "hwpx 작성", "한글 파일 채우기" 요청시 사용합니다.
---

# 한글 파일 채우기 스킬

## 사용법

```
/hwp-fill [템플릿경로|템플릿이름] [내용파일.md]
```

## 입력

$ARGUMENTS

## 입력 형식

### 1. 템플릿 + MD 파일
```
/hwp-fill IRB서식.hwpx 연구계획.md
```

### 2. 대화로 내용 입력
```
/hwp-fill IRB서식.hwpx
(이후 대화로 내용 입력)
```

## 실행 절차

1. **템플릿 확인**: 파일 존재 여부 확인

2. **내용 소스 확인**:
   - MD 파일 제공시: 파일 내용 파싱
   - 없으면: 사용자에게 내용 입력 요청

3. **MD 파일 파싱**: 헤더를 필드명으로, 내용을 값으로 추출
```python
import re

def parse_markdown(md_content):
    content_dict = {}
    pattern = r'^#{1,2}\s+(.+?)$\s*((?:(?!^#{1,2}\s).+\n?)*)'
    matches = re.findall(pattern, md_content, re.MULTILINE)
    for field_name, field_value in matches:
        content_dict[field_name.strip()] = field_value.strip()
    return content_dict
```

4. **필드 매칭 확인**: 매칭 결과를 사용자에게 보여주고 확인

5. **문서 채우기**:
```python
import zipfile
import shutil
import os
from xml.etree import ElementTree as ET

def fill_hwpx(template_path, content_dict, output_path):
    shutil.copy2(template_path, output_path)
    temp_dir = output_path + "_temp"
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(output_path, 'r') as zf:
            zf.extractall(temp_dir)

        # section XML 수정
        contents_dir = os.path.join(temp_dir, 'Contents')
        for f in os.listdir(contents_dir):
            if f.startswith('section') and f.endswith('.xml'):
                section_path = os.path.join(contents_dir, f)
                tree = ET.parse(section_path)
                root = tree.getroot()

                # 표 내 셀 채우기
                ns = 'http://www.hancom.co.kr/hwpml/2011/paragraph'
                for tbl in root.findall(f'.//{{{ns}}}tbl'):
                    for tr in tbl.findall(f'.//{{{ns}}}tr'):
                        cells = list(tr.findall(f'.//{{{ns}}}tc'))
                        if len(cells) >= 2:
                            # 첫 셀: 필드명, 둘째 셀: 값
                            field_name = get_cell_text(cells[0])
                            if field_name in content_dict:
                                set_cell_text(cells[1], content_dict[field_name])

                tree.write(section_path, encoding='utf-8', xml_declaration=True)

        # 다시 압축
        os.remove(output_path)
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root_dir, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root_dir, file)
                    arc_name = os.path.relpath(file_path, temp_dir)
                    zf.write(file_path, arc_name)
    finally:
        shutil.rmtree(temp_dir)

    return output_path
```

6. **결과 안내**: 생성된 파일 경로 안내

## MD 파일 형식

```markdown
# 연구과제명
스마트 헬스케어 시스템 개발

## 연구책임자
홍길동

## 연구기간
2024.01.01 ~ 2024.12.31
```

## 출력 파일

기본: `{원본파일명}_filled.hwpx`

## 필드 매칭 예시

```
템플릿 필드          ←  MD 섹션
──────────────────────────────────
연구과제명           ←  # 연구과제명
연구책임자           ←  ## 연구책임자
연구기간             ←  ## 연구기간
```

매칭 결과를 사용자에게 보여주고 확인 후 진행합니다.
