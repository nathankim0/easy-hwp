"""
HWPX 파일 파싱 모듈

HWPX 파일은 ZIP 형식으로 압축된 XML 기반 문서입니다.
주요 구조:
- Contents/section0.xml: 본문 내용
- Contents/header.xml: 머리말
- settings.xml: 문서 설정
"""

import zipfile
import os
import shutil
from xml.etree import ElementTree as ET
from typing import Optional
from dataclasses import dataclass, field


# HWPX XML 네임스페이스
NAMESPACES = {
    'hp': 'http://www.hancom.co.kr/hwpml/2011/paragraph',
    'hs': 'http://www.hancom.co.kr/hwpml/2011/section',
    'hc': 'http://www.hancom.co.kr/hwpml/2011/core',
    'hp10': 'http://www.hancom.co.kr/hwpml/2016/paragraph',
}


@dataclass
class TableCell:
    """표 셀 정보"""
    row: int
    col: int
    content: str
    row_span: int = 1
    col_span: int = 1


@dataclass
class Table:
    """표 정보"""
    index: int
    rows: int
    cols: int
    cells: list[TableCell] = field(default_factory=list)

    def to_markdown(self) -> str:
        """표를 마크다운 형식으로 변환"""
        if not self.cells:
            return ""

        # 2차원 배열로 셀 배치
        grid = [["" for _ in range(self.cols)] for _ in range(self.rows)]
        for cell in self.cells:
            if 0 <= cell.row < self.rows and 0 <= cell.col < self.cols:
                grid[cell.row][cell.col] = cell.content.strip()

        lines = []
        for i, row in enumerate(grid):
            escaped_row = [c.replace("|", "\\|") for c in row]
            lines.append("| " + " | ".join(escaped_row) + " |")
            if i == 0:
                lines.append("|" + "|".join(["---"] * self.cols) + "|")

        return "\n".join(lines)


@dataclass
class TextField:
    """텍스트 필드 정보"""
    name: str
    content: str
    position: int  # 문서 내 위치 (순서)
    is_empty: bool = False


@dataclass
class DocumentSection:
    """문서 섹션 정보"""
    index: int
    paragraphs: list[str] = field(default_factory=list)
    tables: list[Table] = field(default_factory=list)


@dataclass
class HwpxDocument:
    """HWPX 문서 구조"""
    file_path: str
    sections: list[DocumentSection] = field(default_factory=list)
    fields: list[TextField] = field(default_factory=list)

    def to_structure_markdown(self) -> str:
        """문서 구조를 마크다운으로 변환"""
        lines = [
            f"# 문서 구조 분석: {os.path.basename(self.file_path)}",
            "",
            f"**원본 파일**: `{self.file_path}`",
            f"**섹션 수**: {len(self.sections)}",
            "",
        ]

        # 필드 정보
        if self.fields:
            lines.append("## 필드 목록")
            lines.append("")
            empty_fields = [f for f in self.fields if f.is_empty]
            filled_fields = [f for f in self.fields if not f.is_empty]

            if empty_fields:
                lines.append("### 빈 필드 (채워야 할 항목)")
                for f in empty_fields:
                    lines.append(f"- **{f.name}**: _(빈 칸)_")
                lines.append("")

            if filled_fields:
                lines.append("### 기존 내용이 있는 필드")
                for f in filled_fields:
                    preview = f.content[:50] + "..." if len(f.content) > 50 else f.content
                    lines.append(f"- **{f.name}**: {preview}")
                lines.append("")

        # 섹션별 내용
        for section in self.sections:
            lines.append(f"## 섹션 {section.index + 1}")
            lines.append("")

            # 표 정보
            if section.tables:
                lines.append(f"### 표 ({len(section.tables)}개)")
                lines.append("")
                for table in section.tables:
                    lines.append(f"#### 표 {table.index + 1} ({table.rows}행 x {table.cols}열)")
                    lines.append("")
                    lines.append(table.to_markdown())
                    lines.append("")

            # 단락 텍스트
            if section.paragraphs:
                lines.append("### 텍스트 내용")
                lines.append("")
                for para in section.paragraphs:
                    if para.strip():
                        lines.append(para.strip())
                        lines.append("")

        return "\n".join(lines)


class HwpxParser:
    """HWPX 파일 파서"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.temp_dir: Optional[str] = None

    def analyze(self) -> HwpxDocument:
        """HWPX 파일을 분석하여 문서 구조 반환"""
        doc = HwpxDocument(file_path=self.file_path)

        try:
            with zipfile.ZipFile(self.file_path, 'r') as zf:
                # 섹션 파일 목록 찾기
                section_files = sorted([
                    name for name in zf.namelist()
                    if name.startswith('Contents/section') and name.endswith('.xml')
                ])

                for idx, section_file in enumerate(section_files):
                    section = self._parse_section(zf, section_file, idx)
                    doc.sections.append(section)

                # 필드 정보 추출
                doc.fields = self._extract_fields(doc)

        except zipfile.BadZipFile:
            raise ValueError(f"유효하지 않은 HWPX 파일입니다: {self.file_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {self.file_path}")

        return doc

    def _parse_section(self, zf: zipfile.ZipFile, section_file: str, index: int) -> DocumentSection:
        """섹션 XML 파싱"""
        section = DocumentSection(index=index)

        try:
            with zf.open(section_file) as f:
                content = f.read()
                root = ET.fromstring(content)

                # 모든 네임스페이스 등록
                for prefix, uri in NAMESPACES.items():
                    ET.register_namespace(prefix, uri)

                # 표 파싱
                section.tables = self._parse_tables(root)

                # 단락 텍스트 파싱
                section.paragraphs = self._parse_paragraphs(root)

        except ET.ParseError as e:
            print(f"XML 파싱 오류 ({section_file}): {e}")

        return section

    def _parse_tables(self, root: ET.Element) -> list[Table]:
        """표 요소 파싱"""
        tables = []

        # 다양한 네임스페이스에서 표 찾기
        table_elements = []
        for ns_prefix in ['hp', 'hp10']:
            ns = NAMESPACES.get(ns_prefix, '')
            if ns:
                table_elements.extend(root.findall(f'.//{{{ns}}}tbl'))

        # 네임스페이스 없이도 시도
        table_elements.extend(root.findall('.//tbl'))

        for idx, tbl in enumerate(table_elements):
            table = self._parse_single_table(tbl, idx)
            if table:
                tables.append(table)

        return tables

    def _parse_single_table(self, tbl: ET.Element, index: int) -> Optional[Table]:
        """단일 표 파싱"""
        # 행/열 수 추출
        rows = int(tbl.get('rowCnt', 0))
        cols = int(tbl.get('colCnt', 0))

        if rows == 0 or cols == 0:
            # 속성이 없으면 실제 요소 수로 계산
            row_elements = list(tbl.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}tr'))
            if not row_elements:
                row_elements = list(tbl.findall('.//tr'))
            rows = len(row_elements) if row_elements else 0

        table = Table(index=index, rows=rows, cols=cols)

        # 셀 내용 추출
        cells = self._extract_table_cells(tbl)
        table.cells = cells

        # 실제 행/열 수 업데이트
        if cells:
            table.rows = max(c.row for c in cells) + 1
            table.cols = max(c.col for c in cells) + 1

        return table if table.rows > 0 and table.cols > 0 else None

    def _extract_table_cells(self, tbl: ET.Element) -> list[TableCell]:
        """표 셀 내용 추출"""
        cells = []

        # 행 요소 찾기
        row_elements = list(tbl.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}tr'))
        if not row_elements:
            row_elements = list(tbl.findall('.//tr'))

        for row_idx, tr in enumerate(row_elements):
            # 셀 요소 찾기
            cell_elements = list(tr.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}tc'))
            if not cell_elements:
                cell_elements = list(tr.findall('.//tc'))

            for col_idx, tc in enumerate(cell_elements):
                content = self._extract_cell_text(tc)
                cell = TableCell(
                    row=row_idx,
                    col=col_idx,
                    content=content
                )
                cells.append(cell)

        return cells

    def _extract_cell_text(self, tc: ET.Element) -> str:
        """셀 내에서 텍스트 추출"""
        texts = []

        # 모든 텍스트 요소 찾기 (여러 네임스페이스)
        for elem in tc.iter():
            if elem.tag.endswith('}t') or elem.tag == 't':
                if elem.text:
                    texts.append(elem.text)

        return " ".join(texts)

    def _parse_paragraphs(self, root: ET.Element) -> list[str]:
        """단락 텍스트 파싱"""
        paragraphs = []

        # 단락 요소 찾기
        para_elements = root.findall('.//{http://www.hancom.co.kr/hwpml/2011/paragraph}p')
        if not para_elements:
            para_elements = root.findall('.//p')

        for para in para_elements:
            text = self._extract_paragraph_text(para)
            if text:
                paragraphs.append(text)

        return paragraphs

    def _extract_paragraph_text(self, para: ET.Element) -> str:
        """단락에서 텍스트 추출"""
        texts = []

        for elem in para.iter():
            if elem.tag.endswith('}t') or elem.tag == 't':
                if elem.text:
                    texts.append(elem.text)

        return " ".join(texts)

    def _extract_fields(self, doc: HwpxDocument) -> list[TextField]:
        """문서에서 필드 정보 추출 (빈 칸, 입력 필드 등)"""
        fields = []
        position = 0

        for section in doc.sections:
            for table in section.tables:
                # 표의 첫 번째 열을 필드명으로, 두 번째 열을 값으로 간주
                if table.cols >= 2:
                    for row in range(table.rows):
                        name_cell = next((c for c in table.cells if c.row == row and c.col == 0), None)
                        value_cell = next((c for c in table.cells if c.row == row and c.col == 1), None)

                        if name_cell and name_cell.content.strip():
                            content = value_cell.content.strip() if value_cell else ""
                            field = TextField(
                                name=name_cell.content.strip(),
                                content=content,
                                position=position,
                                is_empty=len(content) == 0
                            )
                            fields.append(field)
                            position += 1

        return fields


def analyze_hwpx(file_path: str) -> HwpxDocument:
    """HWPX 파일 분석 (편의 함수)"""
    parser = HwpxParser(file_path)
    return parser.analyze()


def save_structure_markdown(doc: HwpxDocument, output_path: Optional[str] = None) -> str:
    """문서 구조를 마크다운 파일로 저장"""
    if output_path is None:
        base_name = os.path.splitext(doc.file_path)[0]
        output_path = f"{base_name}_structure.md"

    content = doc.to_structure_markdown()

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return output_path


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("사용법: python hwpx_parser.py <hwpx파일경로>")
        sys.exit(1)

    file_path = sys.argv[1]

    try:
        doc = analyze_hwpx(file_path)
        output_path = save_structure_markdown(doc)
        print(f"분석 완료! 결과 저장: {output_path}")
        print("\n" + doc.to_structure_markdown())
    except Exception as e:
        print(f"오류: {e}")
        sys.exit(1)
