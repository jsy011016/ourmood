#!/bin/bash

# CatVTON 품질 개선 프로젝트 빠른 시작 스크립트

echo "=================================="
echo "🎨 CatVTON 품질 개선 시스템"
echo "=================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. 의존성 확인
check_dependencies() {
    echo -e "${BLUE}📦 의존성 확인 중...${NC}"

    python3 -c "import flask" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Flask가 설치되지 않았습니다. 설치 중...${NC}"
        pip install flask flask-cors
    fi

    python3 -c "import torch" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ PyTorch가 설치되지 않았습니다!${NC}"
        echo "   설치: pip install torch torchvision"
        exit 1
    fi

    python3 -c "import PIL" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Pillow가 설치되지 않았습니다. 설치 중...${NC}"
        pip install pillow
    fi

    python3 -c "import cv2" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  OpenCV가 설치되지 않았습니다. 설치 중...${NC}"
        pip install opencv-python
    fi

    echo -e "${GREEN}✅ 의존성 확인 완료${NC}"
    echo ""
}

# 2. 테스트 데이터 준비
prepare_test_data() {
    echo -e "${BLUE}📁 테스트 데이터 준비${NC}"

    if [ ! -d "test_data/garments" ]; then
        echo -e "${YELLOW}⚠️  테스트 데이터가 없습니다.${NC}"
        echo ""
        echo "다음 중 하나를 선택하세요:"
        echo "1. API로 자동 수집 (Pexels/Unsplash)"
        echo "2. 수동으로 이미지 추가"
        echo "3. 건너뛰기"
        read -p "선택 (1/2/3): " choice

        case $choice in
            1)
                python3 data_collector.py
                ;;
            2)
                echo ""
                echo "이미지를 다음 폴더에 추가하세요:"
                echo "  - test_data/garments/tops/"
                echo "  - test_data/garments/outers/"
                echo "  - test_data/garments/bottoms/"
                echo "  - test_data/garments/dresses/"
                echo "  - test_data/models/full_body/"
                mkdir -p test_data/garments/{tops,outers,bottoms,dresses}
                mkdir -p test_data/models/full_body
                echo ""
                read -p "이미지 추가 후 Enter를 누르세요..."
                ;;
            3)
                echo -e "${YELLOW}⚠️  테스트 데이터 없이 진행합니다.${NC}"
                ;;
        esac
    else
        echo -e "${GREEN}✅ 테스트 데이터 확인됨${NC}"
    fi
    echo ""
}

# 3. 서버 실행
start_server() {
    echo -e "${BLUE}🚀 서버 시작${NC}"
    echo ""
    echo "어떤 서버를 실행하시겠습니까?"
    echo "1. 기본 서버 (server.py)"
    echo "2. 개선된 서버 (server_enhanced.py) ⭐ 권장"
    read -p "선택 (1/2): " server_choice

    case $server_choice in
        1)
            echo -e "${GREEN}기본 서버 실행 중...${NC}"
            python3 server.py &
            SERVER_PID=$!
            ;;
        2)
            echo -e "${GREEN}개선된 서버 실행 중...${NC}"
            python3 server_enhanced.py &
            SERVER_PID=$!
            ;;
        *)
            echo -e "${RED}잘못된 선택입니다.${NC}"
            exit 1
            ;;
    esac

    # 서버 시작 대기
    echo "서버 시작 대기 중..."
    sleep 10

    # 서버 상태 확인
    curl -s http://localhost:5000/health > /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 서버 시작 완료!${NC}"
        echo "   주소: http://localhost:5000"
    else
        echo -e "${RED}❌ 서버 시작 실패${NC}"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
    echo ""
}

# 4. 성능 측정 실행
run_performance_test() {
    echo -e "${BLUE}📊 성능 측정 시작${NC}"
    echo ""
    read -p "성능 측정을 실행하시겠습니까? (y/n): " run_test

    if [ "$run_test" = "y" ] || [ "$run_test" = "Y" ]; then
        python3 performance_test.py

        echo ""
        echo -e "${GREEN}✅ 성능 측정 완료!${NC}"
        echo "   결과: test_data/results/"

        # 최신 리포트 파일 찾기
        LATEST_REPORT=$(ls -t test_data/results/report_*.json 2>/dev/null | head -1)
        if [ -n "$LATEST_REPORT" ]; then
            echo "   리포트: $LATEST_REPORT"

            # 간단한 요약 출력
            echo ""
            echo "📈 요약:"
            python3 -c "
import json
with open('$LATEST_REPORT') as f:
    data = json.load(f)
    summary = data['summary']
    print(f\"   총 테스트: {summary['total_tests']}\")
    print(f\"   성공률: {summary['success_rate']:.1f}%\")
    print(f\"   평균 시간: {summary['avg_time']:.2f}초\")
    print(f\"   평균 품질: {summary['avg_quality']:.1f}/100\")
"
        fi
    else
        echo -e "${YELLOW}성능 측정을 건너뜁니다.${NC}"
    fi
    echo ""
}

# 5. 정리
cleanup() {
    echo ""
    echo -e "${BLUE}🧹 정리 중...${NC}"

    if [ -n "$SERVER_PID" ]; then
        echo "서버 종료 중..."
        kill $SERVER_PID 2>/dev/null
        wait $SERVER_PID 2>/dev/null
        echo -e "${GREEN}✅ 서버 종료 완료${NC}"
    fi

    echo ""
    echo "=================================="
    echo "✅ 모든 작업 완료!"
    echo "=================================="
}

# 트랩 설정 (Ctrl+C 시 정리)
trap cleanup EXIT INT TERM

# 메인 실행
main() {
    check_dependencies
    prepare_test_data
    start_server
    run_performance_test
}

# 스크립트 시작
main