#!/bin/bash

# easy-hwp 테스트 실행 스크립트

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "프로젝트 경로: $PROJECT_DIR"
echo ""

# Python 경로 설정
export PYTHONPATH="$PROJECT_DIR/plugins/easy-hwp/lib:$PYTHONPATH"

# 테스트 실행
python3 "$SCRIPT_DIR/test_hwp.py"

exit $?
