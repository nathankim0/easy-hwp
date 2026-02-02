---
name: hwp-analyze
description: 한글 파일(.hwp, .hwpx)의 구조를 분석합니다. "hwp 분석", "서식 분석", "한글 파일 구조" 요청시 사용합니다.
---

# 한글 파일 분석

## 입력
$ARGUMENTS

## OS별 처리 방법

### Windows: pyhwpx 사용 (권장)

Windows + 한글 프로그램이 설치된 환경에서는 pyhwpx를 사용합니다.

```python
from pyhwpx import Hwp

hwp = Hwp()
hwp.open("서식.hwp")  # .hwp, .hwpx 모두 지원

# 필드 목록 조회
fields = hwp.get_field_list()
print(fields)

# 필드값 조회
for field in fields:
    value = hwp.get_field_text(field)
    print(f"{field}: {value}")

hwp.quit()
```

**pyhwpx 설치**: `pip install pyhwpx`

### macOS/Linux: XML 직접 파싱 (.hwpx만 지원)

HWPX는 ZIP 형식의 압축 파일입니다.

```
hwpx파일/
├── Contents/
│   ├── section0.xml    # 본문 내용 (첫 번째 섹션)
│   ├── section1.xml    # 추가 섹션 (있는 경우)
│   └── header.xml      # 헤더 정보
├── settings.xml        # 문서 설정
└── mimetype            # 파일 타입 정보
```

#### 처리 절차

1. **압축 해제**
```bash
unzip -o {파일}.hwpx -d {임시디렉토리}/
```

2. **XML 읽기**: `Contents/section0.xml` 파일을 Read 도구로 읽습니다.

3. **XML 구조 분석**

**네임스페이스**: `hp` = `http://www.hancom.co.kr/hwpml/2011/paragraph`

| 태그 | 의미 |
|------|------|
| `<hp:tbl>` | 표 (table) |
| `<hp:tr>` | 행 (table row) |
| `<hp:tc>` | 셀 (table cell) |
| `<hp:t>` | 텍스트 내용 |
| `<hp:p>` | 문단 (paragraph) |

**표 구조 예시**:
```xml
<hp:tbl>
  <hp:tr>
    <hp:tc><hp:p><hp:t>필드명</hp:t></hp:p></hp:tc>
    <hp:tc><hp:p><hp:t>값</hp:t></hp:p></hp:tc>
  </hp:tr>
</hp:tbl>
```

4. **필드 추출**: 2열 표에서 첫 번째 열은 필드명, 두 번째 열은 값

5. **임시 파일 정리**
```bash
rm -rf {임시디렉토리}
```

## 사용자에게 알려줄 것

- 발견된 표 개수
- 채워야 할 필드 목록 (빈 칸)
- 이미 채워진 필드 (있다면)
- 다음 단계 안내 (`/hwp-fill`로 채우기)

## 주의

- macOS/Linux에서 `.hwp`는 지원 안 됨 → 한글에서 `.hwpx`로 다시 저장하라고 안내
- Windows에서는 pyhwpx로 `.hwp`, `.hwpx` 모두 지원
- 복잡한 표(병합 셀 등)는 구조가 다르게 보일 수 있음
