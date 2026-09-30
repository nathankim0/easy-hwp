# easy-hwp

HWP와 HWPX 문서의 읽기·수정·서식 채우기·템플릿·PDF 미리보기를 하나의 `hwp` 스킬로 제공합니다. Codex, Claude Code, OpenClaw 등 `SKILL.md`를 읽는 에이전트에서 사용할 수 있습니다. 개인 계정이나 특정 문서가 필요하지 않습니다.

## 설치

```sh
git clone https://github.com/nathankim0/easy-hwp.git
cd easy-hwp
python3 scripts/install.py
```

기본 위치는 `~/.codex/skills/hwp`입니다. 다른 런타임은 설치 위치를 선택합니다.

```sh
python3 scripts/install.py --dest ~/.claude/skills/hwp
python3 scripts/install.py --dest ~/.openclaw/skills/hwp
```

기존 설치를 교체하려면 `--replace`를 붙입니다. 이전 파일은 스킬 탐색 경로 밖에 백업됩니다. 설치 후 새 에이전트 세션을 시작하세요.

Claude Code 플러그인 설치도 가능합니다.

```text
/plugin marketplace add nathankim0/easy-hwp
/plugin install easy-hwp@easy-hwp
```

## 요구 사항

- Node.js 18 이상, Python 3.9 이상. 핵심 편집 의존성은 포함되어 있습니다.
- PDF 미리보기 내보내기: Node.js 22 이상과 Chrome/Chromium. 자동 탐색되지 않으면 `HWP_BROWSER`에 실행 파일 경로를 지정합니다.
- Windows 한컴 자동화와 kordoc 등 대체 도구는 필요한 경우만 별도로 사용합니다.

## 사용

```text
현재 계획안.hwp의 날짜만 바꾸고 표와 서식은 유지해줘.
신청서.hwpx 구조를 분석하고 내용.md를 대응하는 칸에 채워줘.
보고서.hwp의 제목이 페이지 끝에 혼자 남지 않도록 수정하고 PDF로 확인해줘.
```

수정은 최신 승인 파일을 기준으로 합니다. 스크립트는 설치된 스킬 폴더에서 실행합니다.

```sh
node scripts/extract_text.js --inspect --with-cell-text /absolute/input.hwp
node scripts/edit.mjs /absolute/input.hwp /absolute/output.hwp operations.json
node scripts/render-pdf.mjs /absolute/output.hwp /absolute/output.pdf
```

작업 지침과 연산 예시는 [SKILL.md](plugins/easy-hwp/skills/hwp/SKILL.md)에 있습니다. 연산은 순서대로 임시 복사본에 적용하고, 실패하면 기존 출력 파일을 보존합니다.

## 서식 검증

셀 줄바꿈 캐시, 셀 분할 시 스타일 상속, 제목 페이지 넘김과 간격, 실제 문단 분리, HWPUNIT/pt 구분을 보완했습니다. 수정 후 텍스트와 표를 다시 읽고 변경한 페이지를 눈으로 확인합니다. 표 병합이나 글꼴 통일은 요청 범위 안에서 수행합니다.

가능하면 한컴의 원본 PDF 내보내기를 사용하세요. 포함된 미리보기 PDF는 이미지 기반이며 검색 가능한 텍스트가 없습니다. 한컴과 글꼴·페이지 배치가 다를 수 있어 원본과 동일하다고 보장하지 않습니다.

## 개발 검증

```sh
node tests/regression.mjs
```

테스트는 합성 문서를 임시 폴더에 생성합니다. 개인정보, 사용자 문서, 봇 토큰, 수신자 설정은 포함하지 않습니다.

## 라이선스

MIT. 통합한 엔진과 외부 구성 요소의 출처는 [NOTICE](NOTICE), 각 구성 요소의 라이선스는 `scripts/vendor`에 보존되어 있습니다.
