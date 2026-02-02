"""
한글 파일 통합 처리 모듈

파일 확장자에 따라 적절한 파서를 자동 선택합니다:
- .hwpx: XML 직접 파싱 (크로스 플랫폼)
- .hwp: pyhwpx 사용 (Windows + 한글 프로그램 필요)
"""

import os
import json
import shutil
import zipfile
from pathlib import Path
from typing import Optional, Union
from dataclasses import asdict
from xml.etree import ElementTree as ET

from hwpx_parser import (
    HwpxParser, HwpxDocument, Table, TableCell, TextField, DocumentSection,
    analyze_hwpx, save_structure_markdown, NAMESPACES
)
from hwp_parser import (
    HwpParser, HwpParserError, check_hwp_support,
    analyze_hwp, IS_WINDOWS, PYHWPX_AVAILABLE
)


# 템플릿 저장 경로
TEMPLATE_DIR = Path(__file__).parent / "templates"
TEMPLATE_INDEX_FILE = TEMPLATE_DIR / "index.json"


class HwpCore:
    """한글 파일 통합 처리 클래스"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.extension = self._get_extension()

    def _get_extension(self) -> str:
        """파일 확장자 추출"""
        _, ext = os.path.splitext(self.file_path)
        return ext.lower()

    @property
    def is_hwpx(self) -> bool:
        return self.extension == '.hwpx'

    @property
    def is_hwp(self) -> bool:
        return self.extension == '.hwp'

    def analyze(self) -> Union[HwpxDocument, None]:
        """파일 분석 (확장자에 따라 자동 선택)"""
        if self.is_hwpx:
            return analyze_hwpx(self.file_path)
        elif self.is_hwp:
            if not IS_WINDOWS or not PYHWPX_AVAILABLE:
                raise HwpParserError(
                    f".hwp 파일은 Windows + 한글 프로그램 환경에서만 분석 가능합니다.\n"
                    f".hwpx 형식으로 변환 후 다시 시도해주세요."
                )
            return analyze_hwp(self.file_path)
        else:
            raise ValueError(f"지원하지 않는 파일 형식입니다: {self.extension}")

    def save_structure(self, output_path: Optional[str] = None) -> str:
        """문서 구조를 마크다운으로 저장"""
        doc = self.analyze()
        return save_structure_markdown(doc, output_path)


class HwpxFiller:
    """HWPX 파일에 내용 채우기"""

    def __init__(self, template_path: str):
        self.template_path = template_path

    def fill(self, content_dict: dict, output_path: str) -> str:
        """템플릿에 내용을 채워서 새 파일 생성"""
        # 1. 템플릿 복사
        shutil.copy2(self.template_path, output_path)

        # 2. ZIP 파일로 열어서 XML 수정
        temp_dir = output_path + "_temp"
        os.makedirs(temp_dir, exist_ok=True)

        try:
            # 압축 해제
            with zipfile.ZipFile(output_path, 'r') as zf:
                zf.extractall(temp_dir)

            # 섹션 파일 수정
            section_files = sorted([
                f for f in os.listdir(os.path.join(temp_dir, 'Contents'))
                if f.startswith('section') and f.endswith('.xml')
            ])

            for section_file in section_files:
                section_path = os.path.join(temp_dir, 'Contents', section_file)
                self._fill_section(section_path, content_dict)

            # 다시 압축
            os.remove(output_path)
            self._create_hwpx(temp_dir, output_path)

        finally:
            # 임시 디렉토리 정리
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

        return output_path

    def _fill_section(self, section_path: str, content_dict: dict):
        """섹션 XML 파일에 내용 채우기"""
        # 네임스페이스 등록
        for prefix, uri in NAMESPACES.items():
            ET.register_namespace(prefix, uri)

        tree = ET.parse(section_path)
        root = tree.getroot()

        # 표 내 셀 채우기
        self._fill_table_cells(root, content_dict)

        # 저장
        tree.write(section_path, encoding='utf-8', xml_declaration=True)

    def _fill_table_cells(self, root: ET.Element, content_dict: dict):
        """표 셀에 내용 채우기"""
        # 표 찾기
        for ns_prefix in ['hp', 'hp10']:
            ns = NAMESPACES.get(ns_prefix, '')
            if ns:
                for tbl in root.findall(f'.//{{{ns}}}tbl'):
                    self._process_table(tbl, content_dict, ns)

    def _process_table(self, tbl: ET.Element, content_dict: dict, ns: str):
        """단일 표 처리"""
        rows = list(tbl.findall(f'.//{{{ns}}}tr'))
        if not rows:
            rows = list(tbl.findall('.//tr'))

        for tr in rows:
            cells = list(tr.findall(f'.//{{{ns}}}tc'))
            if not cells:
                cells = list(tr.findall('.//tc'))

            if len(cells) >= 2:
                # 첫 번째 셀: 필드명, 두 번째 셀: 값
                field_name = self._get_cell_text(cells[0])
                if field_name and field_name in content_dict:
                    self._set_cell_text(cells[1], content_dict[field_name])

    def _get_cell_text(self, cell: ET.Element) -> str:
        """셀에서 텍스트 추출"""
        texts = []
        for elem in cell.iter():
            if elem.tag.endswith('}t') or elem.tag == 't':
                if elem.text:
                    texts.append(elem.text)
        return " ".join(texts).strip()

    def _set_cell_text(self, cell: ET.Element, new_text: str):
        """셀에 텍스트 설정"""
        # 기존 텍스트 요소 찾기
        for elem in cell.iter():
            if elem.tag.endswith('}t') or elem.tag == 't':
                elem.text = new_text
                return

        # 텍스트 요소가 없으면 첫 번째 run에 추가
        for elem in cell.iter():
            if elem.tag.endswith('}run') or elem.tag == 'run':
                # 네임스페이스 확인
                ns_match = elem.tag.split('}')[0] + '}' if '}' in elem.tag else ''
                t_elem = ET.SubElement(elem, f"{ns_match}t")
                t_elem.text = new_text
                return

    def _create_hwpx(self, source_dir: str, output_path: str):
        """디렉토리를 HWPX 파일로 압축"""
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_name = os.path.relpath(file_path, source_dir)
                    zf.write(file_path, arc_name)


class TemplateManager:
    """템플릿 관리"""

    def __init__(self):
        self._ensure_template_dir()

    def _ensure_template_dir(self):
        """템플릿 디렉토리 생성"""
        TEMPLATE_DIR.mkdir(parents=True, exist_ok=True)
        if not TEMPLATE_INDEX_FILE.exists():
            self._save_index({})

    def _load_index(self) -> dict:
        """템플릿 인덱스 로드"""
        if TEMPLATE_INDEX_FILE.exists():
            with open(TEMPLATE_INDEX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_index(self, index: dict):
        """템플릿 인덱스 저장"""
        with open(TEMPLATE_INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def save_template(self, name: str, file_path: str, field_mapping: Optional[dict] = None) -> str:
        """템플릿 저장"""
        index = self._load_index()

        # 파일 복사
        _, ext = os.path.splitext(file_path)
        template_file = TEMPLATE_DIR / f"{name}{ext}"
        shutil.copy2(file_path, template_file)

        # 문서 분석하여 필드 정보 저장
        core = HwpCore(file_path)
        try:
            doc = core.analyze()
            fields = [asdict(f) for f in doc.fields] if doc.fields else []
        except Exception:
            fields = []

        # 인덱스 업데이트
        index[name] = {
            'file': str(template_file),
            'original_path': file_path,
            'extension': ext,
            'fields': fields,
            'field_mapping': field_mapping or {}
        }

        self._save_index(index)
        return str(template_file)

    def get_template(self, name: str) -> Optional[dict]:
        """템플릿 정보 조회"""
        index = self._load_index()
        return index.get(name)

    def list_templates(self) -> list[str]:
        """템플릿 목록 조회"""
        index = self._load_index()
        return list(index.keys())

    def delete_template(self, name: str) -> bool:
        """템플릿 삭제"""
        index = self._load_index()

        if name not in index:
            return False

        template_info = index[name]
        template_file = Path(template_info['file'])

        if template_file.exists():
            template_file.unlink()

        del index[name]
        self._save_index(index)
        return True

    def update_field_mapping(self, name: str, mapping: dict) -> bool:
        """필드 매핑 업데이트"""
        index = self._load_index()

        if name not in index:
            return False

        index[name]['field_mapping'] = mapping
        self._save_index(index)
        return True


def get_support_info() -> dict:
    """파일 형식별 지원 정보"""
    hwp_support = check_hwp_support()

    return {
        'hwpx': {
            'supported': True,
            'message': 'HWPX 파일은 모든 환경에서 지원됩니다.'
        },
        'hwp': {
            'supported': hwp_support['hwp_supported'],
            'message': hwp_support['message']
        }
    }


# 편의 함수들

def parse_markdown_content(md_path: str) -> dict:
    """마크다운 파일에서 필드-값 딕셔너리 추출

    형식:
    # 필드명1
    값1

    ## 필드명2
    값2 (여러 줄 가능)
    """
    content_dict = {}

    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    import re
    # 헤더와 내용 추출 (# 또는 ## 로 시작하는 라인)
    pattern = r'^#{1,2}\s+(.+?)$\s*((?:(?!^#{1,2}\s).+\n?)*)'
    matches = re.findall(pattern, content, re.MULTILINE)

    for field_name, field_value in matches:
        field_name = field_name.strip()
        field_value = field_value.strip()
        if field_name and field_value:
            content_dict[field_name] = field_value

    return content_dict


def analyze_document(file_path: str) -> Union[HwpxDocument, None]:
    """문서 분석 (통합 인터페이스)"""
    core = HwpCore(file_path)
    return core.analyze()


def fill_document(template_path: str, content_dict: dict, output_path: str) -> str:
    """문서에 내용 채우기 (통합 인터페이스)"""
    _, ext = os.path.splitext(template_path)

    if ext.lower() == '.hwpx':
        filler = HwpxFiller(template_path)
        return filler.fill(content_dict, output_path)
    elif ext.lower() == '.hwp':
        if not IS_WINDOWS or not PYHWPX_AVAILABLE:
            raise HwpParserError(
                ".hwp 파일은 Windows + 한글 프로그램 환경에서만 처리 가능합니다."
            )
        from hwp_parser import fill_hwp
        return fill_hwp(template_path, content_dict, output_path)
    else:
        raise ValueError(f"지원하지 않는 파일 형식입니다: {ext}")


if __name__ == "__main__":
    import sys

    print("=== 한글 파일 지원 정보 ===")
    info = get_support_info()
    print(f"HWPX: {info['hwpx']['message']}")
    print(f"HWP: {info['hwp']['message']}")

    if len(sys.argv) >= 2:
        file_path = sys.argv[1]
        print(f"\n=== 파일 분석: {file_path} ===")
        try:
            doc = analyze_document(file_path)
            print(doc.to_structure_markdown())
        except Exception as e:
            print(f"오류: {e}")
