"""
자동 테스트 및 정확도 측정
- 모든 조합 테스트
- 분류 정확도 계산
- 성능 리포트 생성
- ✨ 결과 이미지 저장 (개선됨!)
"""

import requests
import base64
import json
import time
from pathlib import Path
from datetime import datetime
import numpy as np
import os


class AccuracyTester:
    def __init__(self, test_dir='test_images', server_url='http://localhost:5000'):
        self.test_dir = Path(test_dir)
        self.server_url = server_url
        self.results = []
        self.results_dir = Path('test_results')
        self.results_dir.mkdir(exist_ok=True)

        # ✨ 결과 이미지 저장 디렉토리
        self.images_dir = self.results_dir / 'images'
        self.images_dir.mkdir(exist_ok=True)

        print(f"📁 결과 저장 경로: {self.results_dir.absolute()}")
        print(f"🖼️  이미지 저장 경로: {self.images_dir.absolute()}")

    def image_to_base64(self, image_path):
        """이미지를 Base64로 인코딩"""
        with open(image_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')

    def save_result_image(self, base64_data, filename):
        """
        ✨ 결과 이미지 저장 (개선됨!)
        - 에러 처리 강화
        - 저장 경로 반환
        - 성공/실패 로그
        """
        try:
            # data:image/png;base64, 접두사 제거
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]

            # Base64 디코딩
            img_bytes = base64.b64decode(base64_data)

            # 파일 저장
            save_path = self.images_dir / filename
            with open(save_path, 'wb') as f:
                f.write(img_bytes)

            # 파일 크기 확인
            file_size = os.path.getsize(save_path)
            print(f"   💾 이미지 저장: {filename} ({file_size/1024:.1f}KB)")

            return str(save_path)

        except Exception as e:
            print(f"   ❌ 이미지 저장 실패: {e}")
            return None

    def test_single_combination(self, model_path, garment_path, expected_type):
        """하나의 조합 테스트"""
        print(f"\n🧪 테스트:")
        print(f"   모델: {model_path.name}")
        print(f"   의상: {garment_path.name}")
        print(f"   예상: {expected_type}")

        try:
            start_time = time.time()

            response = requests.post(
                f'{self.server_url}/api/single-tryon',
                json={
                    'person': self.image_to_base64(model_path),
                    'cloth': self.image_to_base64(garment_path),
                    'cloth_filename': garment_path.name
                },
                timeout=120
            )

            elapsed = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    classification = data.get('classification', {})
                    predicted = classification.get('class', 'unknown')
                    confidence = classification.get('confidence', 0.0)

                    is_correct = (predicted == expected_type)

                    # ✨ 결과 이미지 저장 (개선됨!)
                    saved_image_path = None
                    result_img_data = data.get('result', '')

                    if result_img_data:
                        # 파일명 생성 (타임스탬프 추가)
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')[:-3]
                        result_filename = f"{timestamp}_{model_path.stem}_{garment_path.stem}_{predicted}.png"

                        saved_image_path = self.save_result_image(result_img_data, result_filename)
                    else:
                        print(f"   ⚠️  응답에 결과 이미지 없음")

                    print(f"   예측: {predicted} (신뢰도: {confidence:.0%})")
                    print(f"   {'✅ 정답' if is_correct else '❌ 오답'} ({elapsed:.1f}초)")

                    return {
                        'model': model_path.name,
                        'garment': garment_path.name,
                        'expected': expected_type,
                        'predicted': predicted,
                        'confidence': confidence,
                        'correct': is_correct,
                        'time': elapsed,
                        'success': True,
                        'saved_image': saved_image_path  # ✨ 저장된 이미지 경로 추가
                    }

            print(f"   ❌ 실패: HTTP {response.status_code}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"   ❌ 오류: {e}")
            return {'success': False, 'error': str(e)}

    def run_full_test(self, sample_ratio=1.0):
        """
        전체 테스트 실행
        sample_ratio: 샘플링 비율 (0.1 = 10%, 1.0 = 100%)
        """
        print("=" * 70)
        print("🚀 전체 테스트 시작")
        print("=" * 70)

        # 테스트 케이스 준비
        models = list((self.test_dir / 'models').glob('*.jpg'))

        garments = {
            'top': list((self.test_dir / 'tops').glob('*.jpg')),
            'bottom': list((self.test_dir / 'bottoms').glob('*.jpg')),
            'dress': list((self.test_dir / 'dresses').glob('*.jpg'))
        }

        if not models:
            print("❌ 모델 이미지가 없습니다!")
            print(f"   {self.test_dir / 'models'} 폴더에 이미지를 추가하세요")
            return

        # 총 테스트 수 계산
        total_tests = sum(len(models) * len(g) for g in garments.values())

        # 샘플링 적용
        if sample_ratio < 1.0:
            import random
            sample_size = int(total_tests * sample_ratio)
            print(f"\n⚠️ 샘플링 모드: {sample_ratio*100:.0f}% ({sample_size}/{total_tests})")
        else:
            sample_size = total_tests

        print(f"\n📊 테스트 개요:")
        print(f"   모델: {len(models)}개")
        for cat, items in garments.items():
            print(f"   {cat}: {len(items)}개")
        print(f"   총 조합: {total_tests}개")

        if total_tests == 0:
            print("\n❌ 테스트할 의상이 없습니다!")
            return

        input("\nEnter를 눌러 시작...")

        # 테스트 실행
        test_count = 0
        self.results = []

        for expected_type, garment_list in garments.items():
            for garment_path in garment_list:
                for model_path in models:
                    test_count += 1
                    print(f"\n{'='*70}")
                    print(f"[{test_count}/{total_tests}]")

                    result = self.test_single_combination(
                        model_path,
                        garment_path,
                        expected_type
                    )

                    if result.get('success'):
                        self.results.append(result)

                    time.sleep(1)  # 서버 부하 방지

        # 결과 분석
        self.analyze_results()

    def analyze_results(self):
        """결과 분석 및 리포트"""
        print("\n" + "=" * 70)
        print("📈 결과 분석")
        print("=" * 70)

        if not self.results:
            print("❌ 분석할 결과가 없습니다")
            return

        total = len(self.results)
        correct = sum(1 for r in self.results if r['correct'])
        accuracy = (correct / total) * 100

        print(f"\n✅ 전체 정확도: {accuracy:.1f}% ({correct}/{total})")

        # ✨ 저장된 이미지 개수
        saved_images = sum(1 for r in self.results if r.get('saved_image'))
        print(f"🖼️  저장된 이미지: {saved_images}개")

        # 카테고리별 정확도
        print(f"\n📊 카테고리별 정확도:")

        categories = {}
        for r in self.results:
            cat = r['expected']
            if cat not in categories:
                categories[cat] = {'total': 0, 'correct': 0}
            categories[cat]['total'] += 1
            if r['correct']:
                categories[cat]['correct'] += 1

        for cat, stats in sorted(categories.items()):
            cat_accuracy = (stats['correct'] / stats['total']) * 100
            print(f"   {cat:10s}: {cat_accuracy:5.1f}% ({stats['correct']}/{stats['total']})")

        # 평균 처리 시간
        avg_time = np.mean([r['time'] for r in self.results])
        print(f"\n⏱️  평균 처리 시간: {avg_time:.2f}초")

        # 신뢰도 분석
        avg_confidence = np.mean([r['confidence'] for r in self.results])
        print(f"📊 평균 신뢰도: {avg_confidence:.1%}")

        # 오분류 분석
        print(f"\n❌ 오분류 사례:")
        errors = [r for r in self.results if not r['correct']]

        if errors:
            for err in errors[:5]:  # 최대 5개만
                img_info = f" (이미지: {Path(err['saved_image']).name})" if err.get('saved_image') else ""
                print(f"   {err['expected']} → {err['predicted']} ({err['garment']}){img_info}")

            if len(errors) > 5:
                print(f"   ... 외 {len(errors)-5}개")
        else:
            print("   없음 (완벽!)")

        # Confusion Matrix
        self.print_confusion_matrix()

        # JSON 저장
        self.save_report()

    def print_confusion_matrix(self):
        """Confusion Matrix 출력"""
        print(f"\n📊 Confusion Matrix:")

        # 모든 카테고리
        all_cats = sorted(set(r['expected'] for r in self.results))

        # 매트릭스 생성
        matrix = {true_cat: {pred_cat: 0 for pred_cat in all_cats}
                  for true_cat in all_cats}

        for r in self.results:
            matrix[r['expected']][r['predicted']] += 1

        # 출력
        print(f"\n{'':12s}", end='')
        for cat in all_cats:
            print(f"{cat:10s}", end='')
        print()

        for true_cat in all_cats:
            print(f"{true_cat:12s}", end='')
            for pred_cat in all_cats:
                count = matrix[true_cat][pred_cat]
                print(f"{count:10d}", end='')
            print()

    def save_report(self):
        """리포트 JSON 저장"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = self.results_dir / f'accuracy_report_{timestamp}.json'

        total = len(self.results)
        correct = sum(1 for r in self.results if r['correct'])
        saved_images = sum(1 for r in self.results if r.get('saved_image'))

        report = {
            'timestamp': timestamp,
            'summary': {
                'total_tests': total,
                'correct': correct,
                'accuracy': (correct / total * 100) if total > 0 else 0,
                'avg_time': np.mean([r['time'] for r in self.results]),
                'avg_confidence': np.mean([r['confidence'] for r in self.results]),
                'saved_images': saved_images  # ✨ 저장된 이미지 개수 추가
            },
            'results': self.results,
            'images_directory': str(self.images_dir)  # ✨ 이미지 디렉토리 경로 추가
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 리포트 저장: {report_path}")
        print(f"📂 이미지 폴더: {self.images_dir}")

    def compare_reports(self, report1_path, report2_path):
        """두 리포트 비교"""
        with open(report1_path) as f:
            r1 = json.load(f)
        with open(report2_path) as f:
            r2 = json.load(f)

        print("=" * 70)
        print("📊 리포트 비교")
        print("=" * 70)

        print(f"\n리포트 1: {report1_path}")
        print(f"리포트 2: {report2_path}")

        s1 = r1['summary']
        s2 = r2['summary']

        print(f"\n정확도:")
        print(f"  리포트 1: {s1['accuracy']:.1f}%")
        print(f"  리포트 2: {s2['accuracy']:.1f}%")
        print(f"  개선:     {s2['accuracy'] - s1['accuracy']:+.1f}%p")

        print(f"\n평균 시간:")
        print(f"  리포트 1: {s1['avg_time']:.2f}초")
        print(f"  리포트 2: {s2['avg_time']:.2f}초")
        print(f"  개선:     {s2['avg_time'] - s1['avg_time']:+.2f}초")


def main():
    tester = AccuracyTester()

    # 서버 확인
    try:
        response = requests.get(f'{tester.server_url}/health', timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 응답하지 않습니다!")
            return
    except:
        print("❌ 서버에 연결할 수 없습니다!")
        print(f"   {tester.server_url}에서 서버를 실행하세요")
        return

    print("✅ 서버 연결 확인\n")

    print("=" * 70)
    print("🎯 정확도 테스트")
    print("=" * 70)
    print("\n옵션:")
    print("1. 전체 테스트 실행 (100%)")
    print("2. 빠른 테스트 (10% 샘플링)")
    print("3. 중간 테스트 (50% 샘플링)")
    print("4. 리포트 비교")

    choice = input("\n선택: ").strip()

    if choice == '1':
        tester.run_full_test(sample_ratio=1.0)
    elif choice == '2':
        tester.run_full_test(sample_ratio=0.1)
    elif choice == '3':
        tester.run_full_test(sample_ratio=0.5)
    elif choice == '4':
        r1 = input("리포트 1 경로: ").strip()
        r2 = input("리포트 2 경로: ").strip()
        tester.compare_reports(r1, r2)


if __name__ == '__main__':
    main()