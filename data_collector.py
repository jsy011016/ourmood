"""
테스트용 이미지 데이터 수집기
- 무신사, Unsplash 등에서 의상/모델 이미지 크롤링
- 카테고리별 분류 및 저장
"""

import requests
import os
import time
from pathlib import Path
from PIL import Image
import io
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json


class ImageCollector:
    def __init__(self, output_dir='test_data'):
        self.output_dir = Path(output_dir)
        self.setup_directories()

    def setup_directories(self):
        """디렉토리 구조 생성"""
        dirs = [
            'garments/tops',
            'garments/outers',
            'garments/bottoms',
            'garments/dresses',
            'models/full_body',
            'results'
        ]
        for dir_path in dirs:
            (self.output_dir / dir_path).mkdir(parents=True, exist_ok=True)

    def download_image(self, url, save_path, max_retries=3):
        """이미지 다운로드 및 저장"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                img = Image.open(io.BytesIO(response.content))

                # RGB 변환
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # 적절한 크기로 리사이즈 (너무 크면)
                max_size = 2048
                if max(img.size) > max_size:
                    ratio = max_size / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)

                img.save(save_path, 'JPEG', quality=95)
                print(f"✅ 저장: {save_path.name}")
                return True

            except Exception as e:
                print(f"⚠️ 다운로드 실패 (시도 {attempt + 1}/{max_retries}): {e}")
                time.sleep(1)

        return False

    def collect_unsplash_images(self, query, category, count=20):
        """Unsplash에서 이미지 수집 (API 키 필요)"""
        # Unsplash API: https://unsplash.com/developers
        # 무료 계정: 50 requests/hour

        print(f"\n🔍 Unsplash 검색: '{query}' ({count}개)")

        # API 키가 없으면 스킵
        api_key = os.getenv('UNSPLASH_ACCESS_KEY')
        if not api_key:
            print("⚠️ UNSPLASH_ACCESS_KEY 환경변수 설정 필요")
            print("   https://unsplash.com/developers 에서 발급")
            return []

        url = "https://api.unsplash.com/search/photos"
        params = {
            'query': query,
            'per_page': count,
            'orientation': 'portrait'
        }
        headers = {'Authorization': f'Client-ID {api_key}'}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            results = data.get('results', [])
            downloaded = []

            for idx, item in enumerate(results):
                img_url = item['urls']['regular']
                filename = f"{query.replace(' ', '_')}_{idx + 1}.jpg"
                save_path = self.output_dir / category / filename

                if self.download_image(img_url, save_path):
                    downloaded.append(str(save_path))
                    time.sleep(0.5)  # Rate limiting

            return downloaded

        except Exception as e:
            print(f"❌ Unsplash 오류: {e}")
            return []

    def collect_pexels_images(self, query, category, count=20):
        """Pexels에서 이미지 수집 (무료 API)"""
        print(f"\n🔍 Pexels 검색: '{query}' ({count}개)")

        api_key = os.getenv('PEXELS_API_KEY')
        if not api_key:
            print("⚠️ PEXELS_API_KEY 환경변수 설정 필요")
            print("   https://www.pexels.com/api/ 에서 발급")
            return []

        url = "https://api.pexels.com/v1/search"
        params = {
            'query': query,
            'per_page': count,
            'orientation': 'portrait'
        }
        headers = {'Authorization': api_key}

        try:
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()

            photos = data.get('photos', [])
            downloaded = []

            for idx, photo in enumerate(photos):
                img_url = photo['src']['large']
                filename = f"{query.replace(' ', '_')}_{idx + 1}.jpg"
                save_path = self.output_dir / category / filename

                if self.download_image(img_url, save_path):
                    downloaded.append(str(save_path))
                    time.sleep(0.5)

            return downloaded

        except Exception as e:
            print(f"❌ Pexels 오류: {e}")
            return []

    def collect_sample_dataset(self):
        """샘플 데이터셋 자동 수집"""
        print("=" * 60)
        print("🎨 테스트 데이터셋 수집 시작")
        print("=" * 60)

        collections = {
            # 의상 이미지
            'garments/tops': [
                'white tshirt fashion',
                'black shirt clothing',
                'casual top wear'
            ],
            'garments/outers': [
                'denim jacket fashion',
                'blazer coat clothing',
                'cardigan outerwear'
            ],
            'garments/bottoms': [
                'blue jeans pants',
                'black skirt fashion',
                'casual trousers'
            ],
            'garments/dresses': [
                'summer dress fashion',
                'elegant dress clothing',
                'casual dress wear'
            ],
            # 모델 이미지
            'models/full_body': [
                'fashion model full body',
                'person standing white background',
                'model portrait full length'
            ]
        }

        results = {}

        for category, queries in collections.items():
            results[category] = []
            for query in queries:
                # Pexels 우선 시도 (무료)
                images = self.collect_pexels_images(query, category, count=5)
                if not images:
                    # Unsplash 시도
                    images = self.collect_unsplash_images(query, category, count=5)

                results[category].extend(images)
                time.sleep(1)

        # 결과 저장
        summary_path = self.output_dir / 'collection_summary.json'
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        print("\n" + "=" * 60)
        print("✅ 수집 완료!")
        print(f"📁 저장 위치: {self.output_dir}")
        print(f"📊 요약 파일: {summary_path}")
        print("=" * 60)

        # 통계 출력
        total = sum(len(imgs) for imgs in results.values())
        print(f"\n총 {total}개 이미지 수집:")
        for category, images in results.items():
            print(f"  - {category}: {len(images)}개")

        return results

    def manual_add_images(self, category, image_paths):
        """수동으로 이미지 추가"""
        category_path = self.output_dir / category
        added = []

        for img_path in image_paths:
            try:
                img = Image.open(img_path)
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                filename = Path(img_path).name
                save_path = category_path / filename
                img.save(save_path, 'JPEG', quality=95)

                added.append(str(save_path))
                print(f"✅ 추가: {filename}")

            except Exception as e:
                print(f"❌ 실패: {img_path} - {e}")

        return added


def main():
    """메인 실행 함수"""
    collector = ImageCollector('test_data')

    print("\n🎯 이미지 수집 방법 선택:")
    print("1. 자동 수집 (Pexels/Unsplash API 사용)")
    print("2. 수동 추가 (로컬 이미지 파일)")
    print("3. 둘 다")

    choice = input("\n선택 (1/2/3): ").strip()

    if choice in ['1', '3']:
        print("\n" + "=" * 60)
        print("📌 API 키 설정 안내")
        print("=" * 60)
        print("환경변수 설정이 필요합니다:")
        print("")
        print("# Pexels (권장, 무료)")
        print("export PEXELS_API_KEY='your_api_key'")
        print("발급: https://www.pexels.com/api/")
        print("")
        print("# Unsplash (선택)")
        print("export UNSPLASH_ACCESS_KEY='your_access_key'")
        print("발급: https://unsplash.com/developers")
        print("=" * 60)

        input("\nAPI 키 설정 후 Enter를 누르세요...")

        collector.collect_sample_dataset()

    if choice in ['2', '3']:
        print("\n📁 로컬 이미지 추가")
        print("이미지 파일들이 있는 폴더 경로를 입력하세요:")
        folder = input("폴더 경로: ").strip()

        if os.path.exists(folder):
            print("\n카테고리 선택:")
            print("1. garments/tops")
            print("2. garments/outers")
            print("3. garments/bottoms")
            print("4. garments/dresses")
            print("5. models/full_body")

            cat_choice = input("선택: ").strip()
            categories = {
                '1': 'garments/tops',
                '2': 'garments/outers',
                '3': 'garments/bottoms',
                '4': 'garments/dresses',
                '5': 'models/full_body'
            }

            category = categories.get(cat_choice)
            if category:
                image_files = list(Path(folder).glob('*.jpg')) + \
                              list(Path(folder).glob('*.png')) + \
                              list(Path(folder).glob('*.jpeg'))

                collector.manual_add_images(category, image_files)
        else:
            print("❌ 폴더를 찾을 수 없습니다.")


if __name__ == '__main__':
    main()