"""
CatVTON 성능 측정 시스템
- 자동으로 여러 조합 테스트
- 정확도/품질 평가 지표 계산
- 결과 시각화 및 리포트 생성
"""

import requests
import json
import time
import base64
from pathlib import Path
from PIL import Image
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix
import io


class PerformanceTester:
    def __init__(self, server_url='http://localhost:5000', test_data_dir='test_data'):
        self.server_url = server_url
        self.test_data_dir = Path(test_data_dir)
        self.results_dir = self.test_data_dir / 'results'
        self.results_dir.mkdir(exist_ok=True)

        # 테스트 결과 저장
        self.test_results = []

    def image_to_base64(self, image_path):
        """이미지를 Base64로 인코딩"""
        with open(image_path, 'rb') as f:
            img_data = f.read()
        return base64.b64encode(img_data).decode('utf-8')

    def base64_to_image(self, base64_str):
        """Base64를 PIL Image로 디코딩"""
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        img_data = base64.b64decode(base64_str)
        return Image.open(io.BytesIO(img_data))

    def test_single_tryon(self, person_path, cloth_path, expected_type=None):
        """단일 가상 피팅 테스트"""
        print(f"\n🧪 테스트 시작:")
        print(f"   모델: {person_path.name}")
        print(f"   의상: {cloth_path.name}")

        start_time = time.time()

        try:
            # API 호출
            response = requests.post(
                f'{self.server_url}/api/single-tryon',
                json={
                    'person': self.image_to_base64(person_path),
                    'cloth': self.image_to_base64(cloth_path),
                    'cloth_filename': cloth_path.name
                },
                timeout=120
            )

            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    # 결과 이미지 저장
                    result_img = self.base64_to_image(data['result'])
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    result_filename = f"result_{person_path.stem}_{cloth_path.stem}_{timestamp}.png"
                    result_path = self.results_dir / result_filename
                    result_img.save(result_path)

                    # 분류 정보
                    classification = data.get('classification', {})
                    predicted_type = classification.get('class', 'unknown')
                    confidence = classification.get('confidence', 0.0)

                    print(f"   ✅ 성공! ({elapsed_time:.2f}초)")
                    print(f"   분류: {predicted_type} (신뢰도: {confidence:.2%})")

                    # 정확도 계산
                    is_correct = (expected_type == predicted_type) if expected_type else None

                    # 이미지 품질 평가
                    quality_score = self.evaluate_image_quality(result_img)

                    result = {
                        'success': True,
                        'person': person_path.name,
                        'cloth': cloth_path.name,
                        'expected_type': expected_type,
                        'predicted_type': predicted_type,
                        'confidence': confidence,
                        'is_correct': is_correct,
                        'elapsed_time': elapsed_time,
                        'quality_score': quality_score,
                        'result_path': str(result_path),
                        'timestamp': timestamp
                    }

                    self.test_results.append(result)
                    return result

            print(f"   ❌ 실패: {response.status_code}")
            return {'success': False, 'error': f"HTTP {response.status_code}"}

        except Exception as e:
            print(f"   ❌ 오류: {e}")
            return {'success': False, 'error': str(e)}

    def evaluate_image_quality(self, image):
        """이미지 품질 평가 (간단한 휴리스틱)"""
        img_array = np.array(image)

        # 1. 선명도 (라플라시안 분산)
        gray = np.mean(img_array, axis=2).astype(np.uint8)
        laplacian = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])

        # 간단한 convolution
        sharpness = 0
        for i in range(1, gray.shape[0] - 1):
            for j in range(1, gray.shape[1] - 1):
                region = gray[i - 1:i + 2, j - 1:j + 2]
                sharpness += abs(np.sum(region * laplacian))

        sharpness = sharpness / (gray.shape[0] * gray.shape[1])

        # 2. 대비 (표준편차)
        contrast = np.std(img_array)

        # 3. 밝기 분포
        brightness = np.mean(img_array)
        brightness_score = 1.0 - abs(brightness - 128) / 128

        # 4. 색상 다양성
        color_variance = np.mean([np.std(img_array[:, :, i]) for i in range(3)])

        # 종합 점수 (0~100)
        quality = (
                min(sharpness / 50, 1.0) * 30 +  # 선명도 30%
                min(contrast / 100, 1.0) * 25 +  # 대비 25%
                brightness_score * 25 +  # 밝기 25%
                min(color_variance / 50, 1.0) * 20  # 색상 20%
        )

        return quality

    def test_layering(self, person_path, garments):
        """레이어링 테스트"""
        print(f"\n🧪 레이어링 테스트:")
        print(f"   모델: {person_path.name}")
        print(f"   의상 수: {len(garments)}개")

        start_time = time.time()

        try:
            garments_data = [
                {
                    'image': self.image_to_base64(g['path']),
                    'filename': g['path'].name
                }
                for g in garments
            ]

            response = requests.post(
                f'{self.server_url}/api/layering-tryon',
                json={
                    'person': self.image_to_base64(person_path),
                    'garments': garments_data
                },
                timeout=300
            )

            elapsed_time = time.time() - start_time

            if response.status_code == 200:
                data = response.json()

                if data.get('success'):
                    result_img = self.base64_to_image(data['result'])
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    result_filename = f"layering_{person_path.stem}_{timestamp}.png"
                    result_path = self.results_dir / result_filename
                    result_img.save(result_path)

                    layers = data.get('layers', [])
                    quality_score = self.evaluate_image_quality(result_img)

                    print(f"   ✅ 성공! ({elapsed_time:.2f}초)")
                    print(f"   품질 점수: {quality_score:.1f}/100")

                    for i, layer in enumerate(layers):
                        print(f"   Layer {i + 1}: {layer['class']}")

                    return {
                        'success': True,
                        'person': person_path.name,
                        'num_garments': len(garments),
                        'layers': layers,
                        'elapsed_time': elapsed_time,
                        'quality_score': quality_score,
                        'result_path': str(result_path)
                    }

            print(f"   ❌ 실패: {response.status_code}")
            return {'success': False}

        except Exception as e:
            print(f"   ❌ 오류: {e}")
            return {'success': False, 'error': str(e)}

    def run_full_test_suite(self):
        """전체 테스트 스위트 실행"""
        print("=" * 70)
        print("🚀 CatVTON 성능 측정 시작")
        print("=" * 70)

        # 테스트 데이터 로드
        test_cases = self.prepare_test_cases()

        if not test_cases:
            print("❌ 테스트 데이터가 없습니다!")
            print(f"   {self.test_data_dir} 폴더에 이미지를 추가하세요.")
            return

        print(f"\n📊 총 {len(test_cases)}개 테스트 케이스")
        print("-" * 70)

        # 단일 피팅 테스트
        for i, case in enumerate(test_cases, 1):
            print(f"\n[{i}/{len(test_cases)}]")
            self.test_single_tryon(
                case['person'],
                case['cloth'],
                case.get('expected_type')
            )
            time.sleep(1)  # 서버 부하 방지

        # 레이어링 테스트 (샘플)
        layering_cases = self.prepare_layering_cases()
        if layering_cases:
            print("\n" + "=" * 70)
            print("🎨 레이어링 테스트")
            print("=" * 70)

            for case in layering_cases[:3]:  # 최대 3개
                self.test_layering(case['person'], case['garments'])
                time.sleep(2)

        # 결과 분석
        self.analyze_results()

    def prepare_test_cases(self):
        """테스트 케이스 준비"""
        test_cases = []

        models = list((self.test_data_dir / 'models/full_body').glob('*.jpg'))
        models += list((self.test_data_dir / 'models/full_body').glob('*.png'))

        garment_categories = {
            'tops': 'top',
            'outers': 'outer',
            'bottoms': 'bottom',
            'dresses': 'dress'
        }

        for category, expected_type in garment_categories.items():
            garment_dir = self.test_data_dir / 'garments' / category
            if not garment_dir.exists():
                continue

            garments = list(garment_dir.glob('*.jpg')) + list(garment_dir.glob('*.png'))

            for model_path in models:
                for garment_path in garments:
                    test_cases.append({
                        'person': model_path,
                        'cloth': garment_path,
                        'expected_type': expected_type
                    })

        return test_cases

    def prepare_layering_cases(self):
        """레이어링 테스트 케이스 준비"""
        models = list((self.test_data_dir / 'models/full_body').glob('*.jpg'))

        if not models:
            return []

        cases = []

        # 예시: 하의 + 상의 + 아우터
        bottoms = list((self.test_data_dir / 'garments/bottoms').glob('*.jpg'))
        tops = list((self.test_data_dir / 'garments/tops').glob('*.jpg'))
        outers = list((self.test_data_dir / 'garments/outers').glob('*.jpg'))

        if bottoms and tops:
            cases.append({
                'person': models[0],
                'garments': [
                    {'path': bottoms[0], 'type': 'bottom'},
                    {'path': tops[0], 'type': 'top'}
                ]
            })

        if bottoms and tops and outers:
            cases.append({
                'person': models[0],
                'garments': [
                    {'path': bottoms[0], 'type': 'bottom'},
                    {'path': tops[0], 'type': 'top'},
                    {'path': outers[0], 'type': 'outer'}
                ]
            })

        return cases

    def analyze_results(self):
        """결과 분석 및 리포트 생성"""
        print("\n" + "=" * 70)
        print("📈 결과 분석")
        print("=" * 70)

        if not self.test_results:
            print("❌ 분석할 결과가 없습니다.")
            return

        successful = [r for r in self.test_results if r.get('success')]
        total = len(self.test_results)
        success_rate = len(successful) / total * 100 if total > 0 else 0

        print(f"\n✅ 성공률: {success_rate:.1f}% ({len(successful)}/{total})")

        if successful:
            # 처리 시간 통계
            times = [r['elapsed_time'] for r in successful]
            print(f"\n⏱️ 처리 시간:")
            print(f"   평균: {np.mean(times):.2f}초")
            print(f"   최소: {np.min(times):.2f}초")
            print(f"   최대: {np.max(times):.2f}초")

            # 분류 정확도
            with_expected = [r for r in successful if r.get('expected_type')]
            if with_expected:
                correct = sum(1 for r in with_expected if r.get('is_correct'))
                accuracy = correct / len(with_expected) * 100
                print(f"\n🎯 분류 정확도: {accuracy:.1f}% ({correct}/{len(with_expected)})")

                # Confusion Matrix
                y_true = [r['expected_type'] for r in with_expected]
                y_pred = [r['predicted_type'] for r in with_expected]
                self.plot_confusion_matrix(y_true, y_pred)

            # 품질 점수
            qualities = [r['quality_score'] for r in successful]
            print(f"\n⭐ 이미지 품질:")
            print(f"   평균: {np.mean(qualities):.1f}/100")
            print(f"   최소: {np.min(qualities):.1f}/100")
            print(f"   최대: {np.max(qualities):.1f}/100")

            # 카테고리별 통계
            self.category_statistics(successful)

        # JSON 리포트 저장
        report_path = self.results_dir / f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump({
                'summary': {
                    'total_tests': total,
                    'successful': len(successful),
                    'success_rate': success_rate,
                    'avg_time': np.mean(times) if times else 0,
                    'avg_quality': np.mean(qualities) if qualities else 0
                },
                'results': self.test_results
            }, f, indent=2, ensure_ascii=False)

        print(f"\n📄 상세 리포트 저장: {report_path}")

    def plot_confusion_matrix(self, y_true, y_pred):
        """Confusion Matrix 시각화"""
        try:
            labels = sorted(set(y_true + y_pred))
            cm = confusion_matrix(y_true, y_pred, labels=labels)

            plt.figure(figsize=(8, 6))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                        xticklabels=labels, yticklabels=labels)
            plt.title('Classification Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')

            cm_path = self.results_dir / f"confusion_matrix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            plt.savefig(cm_path, dpi=300, bbox_inches='tight')
            plt.close()

            print(f"   📊 Confusion Matrix 저장: {cm_path.name}")

        except Exception as e:
            print(f"   ⚠️ Confusion Matrix 생성 실패: {e}")

    def category_statistics(self, results):
        """카테고리별 통계"""
        print("\n📁 카테고리별 성능:")

        by_category = {}
        for r in results:
            cat = r.get('predicted_type', 'unknown')
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(r)

        for cat, items in sorted(by_category.items()):
            times = [i['elapsed_time'] for i in items]
            qualities = [i['quality_score'] for i in items]

            print(f"\n   {cat.upper()}:")
            print(f"      개수: {len(items)}")
            print(f"      평균 시간: {np.mean(times):.2f}초")
            print(f"      평균 품질: {np.mean(qualities):.1f}/100")


def main():
    """메인 실행"""
    tester = PerformanceTester()

    # 서버 상태 확인
    try:
        response = requests.get(f'{tester.server_url}/health', timeout=5)
        if response.status_code != 200:
            print("❌ 서버가 응답하지 않습니다!")
            print(f"   {tester.server_url} 에서 서버를 실행하세요.")
            return
    except:
        print("❌ 서버에 연결할 수 없습니다!")
        print(f"   {tester.server_url} 에서 서버를 실행하세요.")
        return

    print("✅ 서버 연결 확인\n")

    # 전체 테스트 실행
    tester.run_full_test_suite()


if __name__ == '__main__':
    main()