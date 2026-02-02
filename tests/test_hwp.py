"""
easy-hwp 테스트

테스트 항목:
1. HWPX 파일 분석 (analyze)
2. MD 파일 파싱 (parse)
3. 내용 채우기 (fill)
4. 결과 검증 (verify)
"""

import os
import sys
import zipfile
from xml.etree import ElementTree as ET

# lib 경로 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'plugins', 'easy-hwp', 'lib'))

from hwpx_parser import analyze_hwpx, HwpxDocument
from hwp_core import parse_markdown_content, fill_document, analyze_document

# 테스트 파일 경로
FIXTURES_DIR = os.path.join(os.path.dirname(__file__), 'fixtures')
SAMPLE_HWPX = os.path.join(FIXTURES_DIR, 'sample.hwpx')
SAMPLE_MD = os.path.join(FIXTURES_DIR, 'sample_content.md')
OUTPUT_HWPX = os.path.join(FIXTURES_DIR, 'output.hwpx')


def test_analyze_hwpx():
    """HWPX 파일 분석 테스트"""
    print("\n=== 1. HWPX 분석 테스트 ===")

    doc = analyze_hwpx(SAMPLE_HWPX)

    assert doc is not None, "문서 분석 실패"
    assert len(doc.sections) > 0, "섹션이 없음"
    assert len(doc.fields) > 0, "필드가 없음"

    print(f"✓ 섹션 수: {len(doc.sections)}")
    print(f"✓ 필드 수: {len(doc.fields)}")
    print(f"✓ 필드 목록:")
    for field in doc.fields:
        status = "빈칸" if field.is_empty else f"값: {field.content[:20]}..."
        print(f"    - {field.name}: {status}")

    return doc


def test_parse_markdown():
    """MD 파일 파싱 테스트"""
    print("\n=== 2. MD 파싱 테스트 ===")

    content = parse_markdown_content(SAMPLE_MD)

    assert len(content) > 0, "내용이 없음"
    assert "연구과제명" in content, "연구과제명 필드 없음"

    print(f"✓ 파싱된 필드 수: {len(content)}")
    for key, value in content.items():
        preview = value[:30] + "..." if len(value) > 30 else value
        print(f"    - {key}: {preview}")

    return content


def test_fill_document(content_dict):
    """문서 채우기 테스트"""
    print("\n=== 3. 문서 채우기 테스트 ===")

    # 기존 출력 파일 삭제
    if os.path.exists(OUTPUT_HWPX):
        os.remove(OUTPUT_HWPX)

    output_path = fill_document(SAMPLE_HWPX, content_dict, OUTPUT_HWPX)

    assert os.path.exists(output_path), "출력 파일 생성 실패"
    print(f"✓ 출력 파일: {output_path}")

    return output_path


def test_verify_filled_document(output_path):
    """채워진 문서 검증 테스트"""
    print("\n=== 4. 결과 검증 테스트 ===")

    doc = analyze_hwpx(output_path)

    filled_count = 0
    empty_count = 0

    print("✓ 채워진 결과:")
    for field in doc.fields:
        if field.is_empty:
            empty_count += 1
            print(f"    ✗ {field.name}: 빈칸")
        else:
            filled_count += 1
            preview = field.content[:30] + "..." if len(field.content) > 30 else field.content
            print(f"    ✓ {field.name}: {preview}")

    print(f"\n✓ 채워진 필드: {filled_count}개")
    print(f"✓ 빈 필드: {empty_count}개")

    return filled_count, empty_count


def test_xml_content(output_path):
    """XML 내용 직접 확인"""
    print("\n=== 5. XML 내용 확인 ===")

    with zipfile.ZipFile(output_path, 'r') as zf:
        for name in zf.namelist():
            if 'section' in name and name.endswith('.xml'):
                content = zf.read(name).decode('utf-8')
                # 채워진 내용 확인
                if '인공지능' in content:
                    print(f"✓ {name}: 내용이 정상적으로 채워짐")
                else:
                    print(f"✗ {name}: 내용 확인 필요")


def run_all_tests():
    """전체 테스트 실행"""
    print("=" * 50)
    print("easy-hwp 테스트 시작")
    print("=" * 50)

    try:
        # 1. 분석 테스트
        doc = test_analyze_hwpx()

        # 2. MD 파싱 테스트
        content = test_parse_markdown()

        # 3. 채우기 테스트
        output_path = test_fill_document(content)

        # 4. 검증 테스트
        filled, empty = test_verify_filled_document(output_path)

        # 5. XML 확인
        test_xml_content(output_path)

        print("\n" + "=" * 50)
        print("✅ 모든 테스트 통과!")
        print("=" * 50)

        return True

    except AssertionError as e:
        print(f"\n❌ 테스트 실패: {e}")
        return False
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
