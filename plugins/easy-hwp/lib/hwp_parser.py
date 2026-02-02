"""
HWP 파일 파싱 모듈 (Windows + 한글 프로그램 전용)

pyhwpx 라이브러리를 사용하여 .hwp 파일을 처리합니다.
이 모듈은 Windows 환경에서 한글 프로그램이 설치되어 있어야 동작합니다.
"""

import os
import sys
import platform
from dataclasses import dataclass, field
from typing import Optional

# hwpx_parser의 데이터 클래스 재사용
from hwpx_parser import (
    TableCell, Table, TextField, DocumentSection,
    HwpxDocument as HwpDocument  # 동일한 구조 사용
)


# pyhwpx 사용 가능 여부 확인
PYHWPX_AVAILABLE = False
IS_WINDOWS = platform.system() == 'Windows'

if IS_WINDOWS:
    try:
        import pyhwpx
        PYHWPX_AVAILABLE = True
    except ImportError:
        PYHWPX_AVAILABLE = False


class HwpParserError(Exception):
    """HWP 파서 관련 오류"""
    pass


class HwpParser:
    """HWP 파일 파서 (Windows + 한글 프로그램 필요)"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self._validate_environment()

    def _validate_environment(self):
        """실행 환경 검증"""
        if not IS_WINDOWS:
            raise HwpParserError(
                "HWP 파일 처리는 Windows 환경에서만 가능합니다.\n"
                "Mac/Linux에서는 .hwpx 형식을 사용해주세요."
            )

        if not PYHWPX_AVAILABLE:
            raise HwpParserError(
                "pyhwpx 라이브러리가 설치되어 있지 않습니다.\n"
                "설치: pip install pyhwpx\n"
                "참고: 한글 프로그램도 설치되어 있어야 합니다."
            )

    def analyze(self) -> HwpDocument:
        """HWP 파일을 분석하여 문서 구조 반환"""
        if not PYHWPX_AVAILABLE:
            raise HwpParserError("pyhwpx를 사용할 수 없습니다.")

        doc = HwpDocument(file_path=self.file_path)

        try:
            hwp = pyhwpx.Hwp()
            hwp.open(self.file_path)

            # 문서 내용 분석
            section = self._parse_document(hwp)
            doc.sections.append(section)

            # 필드 정보 추출
            doc.fields = self._extract_fields(hwp)

            hwp.quit()

        except Exception as e:
            raise HwpParserError(f"HWP 파일 분석 중 오류: {e}")

        return doc

    def _parse_document(self, hwp) -> DocumentSection:
        """문서 내용 파싱"""
        section = DocumentSection(index=0)

        try:
            # 전체 텍스트 추출
            hwp.move_to_field("", 0, False, False)
            text = hwp.get_text()
            if text:
                section.paragraphs = [p for p in text.split('\n') if p.strip()]

            # 표 정보 추출
            section.tables = self._extract_tables(hwp)

        except Exception as e:
            print(f"문서 파싱 중 경고: {e}")

        return section

    def _extract_tables(self, hwp) -> list[Table]:
        """문서 내 표 추출"""
        tables = []

        try:
            # pyhwpx API를 사용하여 표 추출
            # 참고: 실제 API는 pyhwpx 버전에 따라 다를 수 있음
            table_count = hwp.get_table_count() if hasattr(hwp, 'get_table_count') else 0

            for i in range(table_count):
                table_data = hwp.get_table(i) if hasattr(hwp, 'get_table') else None
                if table_data:
                    table = self._parse_table_data(table_data, i)
                    tables.append(table)

        except Exception as e:
            print(f"표 추출 중 경고: {e}")

        return tables

    def _parse_table_data(self, table_data, index: int) -> Table:
        """표 데이터 파싱"""
        # pyhwpx 반환 형식에 맞게 파싱
        rows = len(table_data) if table_data else 0
        cols = len(table_data[0]) if rows > 0 else 0

        table = Table(index=index, rows=rows, cols=cols)

        for row_idx, row in enumerate(table_data):
            for col_idx, cell_content in enumerate(row):
                cell = TableCell(
                    row=row_idx,
                    col=col_idx,
                    content=str(cell_content) if cell_content else ""
                )
                table.cells.append(cell)

        return table

    def _extract_fields(self, hwp) -> list[TextField]:
        """문서 내 필드 정보 추출"""
        fields = []

        try:
            # pyhwpx의 필드 API 사용
            field_list = hwp.get_field_list() if hasattr(hwp, 'get_field_list') else []

            for idx, field_name in enumerate(field_list):
                field_value = hwp.get_field_text(field_name) if hasattr(hwp, 'get_field_text') else ""
                field = TextField(
                    name=field_name,
                    content=field_value,
                    position=idx,
                    is_empty=len(field_value.strip()) == 0 if field_value else True
                )
                fields.append(field)

        except Exception as e:
            print(f"필드 추출 중 경고: {e}")

        return fields


class HwpFiller:
    """HWP 파일에 내용 채우기 (Windows + 한글 프로그램 필요)"""

    def __init__(self, template_path: str):
        self.template_path = template_path
        self._validate_environment()

    def _validate_environment(self):
        """실행 환경 검증"""
        if not IS_WINDOWS:
            raise HwpParserError(
                "HWP 파일 처리는 Windows 환경에서만 가능합니다."
            )

        if not PYHWPX_AVAILABLE:
            raise HwpParserError(
                "pyhwpx 라이브러리가 설치되어 있지 않습니다."
            )

    def fill(self, content_dict: dict, output_path: str) -> str:
        """템플릿에 내용 채워서 저장"""
        if not PYHWPX_AVAILABLE:
            raise HwpParserError("pyhwpx를 사용할 수 없습니다.")

        try:
            hwp = pyhwpx.Hwp()
            hwp.open(self.template_path)

            # 필드별로 내용 채우기
            for field_name, value in content_dict.items():
                try:
                    hwp.put_field_text(field_name, value)
                except Exception as e:
                    print(f"필드 '{field_name}' 채우기 실패: {e}")

            # 저장
            hwp.save_as(output_path)
            hwp.quit()

            return output_path

        except Exception as e:
            raise HwpParserError(f"HWP 파일 채우기 중 오류: {e}")


def check_hwp_support() -> dict:
    """HWP 파일 지원 여부 확인"""
    return {
        'platform': platform.system(),
        'is_windows': IS_WINDOWS,
        'pyhwpx_available': PYHWPX_AVAILABLE,
        'hwp_supported': IS_WINDOWS and PYHWPX_AVAILABLE,
        'message': (
            "HWP 파일 지원 가능" if IS_WINDOWS and PYHWPX_AVAILABLE
            else "HWPX 형식만 지원됩니다 (Windows + 한글 프로그램 필요)"
        )
    }


def analyze_hwp(file_path: str) -> HwpDocument:
    """HWP 파일 분석 (편의 함수)"""
    parser = HwpParser(file_path)
    return parser.analyze()


def fill_hwp(template_path: str, content_dict: dict, output_path: str) -> str:
    """HWP 파일에 내용 채우기 (편의 함수)"""
    filler = HwpFiller(template_path)
    return filler.fill(content_dict, output_path)


if __name__ == "__main__":
    # 환경 확인
    support = check_hwp_support()
    print("=== HWP 파일 지원 상태 ===")
    print(f"플랫폼: {support['platform']}")
    print(f"Windows 여부: {support['is_windows']}")
    print(f"pyhwpx 사용 가능: {support['pyhwpx_available']}")
    print(f"HWP 지원: {support['hwp_supported']}")
    print(f"상태: {support['message']}")

    if len(sys.argv) >= 2 and support['hwp_supported']:
        file_path = sys.argv[1]
        try:
            doc = analyze_hwp(file_path)
            print(f"\n분석 완료: {file_path}")
            print(doc.to_structure_markdown())
        except HwpParserError as e:
            print(f"오류: {e}")
