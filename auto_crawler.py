"""
자동 이미지 크롤러
- API 키 한 번만 입력
- 자동으로 원하는 개수만큼 수집
"""

import requests
from pathlib import Path
import time
from PIL import Image
import io
import os


class AutoCrawler:
    def __init__(self, output_dir='test_images'):
        self.output_dir = Path(output_dir)
        self.setup_dirs()

    def setup_dirs(self):
        dirs = ['models', 'tops', 'bottoms', 'dresses']
        for d in dirs:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)

    def download_image(self, url, save_path):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            img = Image.open(io.BytesIO(response.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')

            if max(img.size) > 1024:
                ratio = 1024 / max(img.size)
                new_size = tuple(int(d * ratio) for d in img.size)
                img = img.resize(new_size, Image.LANCZOS)

            img.save(save_path, 'JPEG', quality=90)
            return True
        except Exception as e:
            print(f"  ❌ 실패: {e}")
            return False

    def collect_unsplash(self, query, count, category):
        """Unsplash API로 자동 수집"""
        print(f"\n📥 Unsplash에서 '{query}' 검색 중...")

        api_key = os.getenv('UNSPLASH_ACCESS_KEY')
        if not api_key:
            print("\n⚠️ Unsplash API 키가 필요합니다")
            print("1. https://unsplash.com/developers 접속")
            print("2. 회원가입 (무료)")
            print("3. 'New Application' 클릭")
            print("4. Access Key 복사")
            print("")
            api_key = input("Access Key 입력: ").strip()

            if not api_key:
                print("❌ API 키 없이는 수집 불가")
                return 0

        url = "https://api.unsplash.com/search/photos"
        headers = {'Authorization': f'Client-ID {api_key}'}

        downloaded = 0
        page = 1

        while downloaded < count:
            per_page = min(30, count - downloaded)

            params = {
                'query': query,
                'per_page': per_page,
                'page': page,
                'orientation': 'portrait'
            }

            try:
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                results = data.get('results', [])
                if not results:
                    print(f"  ⚠️ 더 이상 이미지 없음 (페이지 {page})")
                    break

                for item in results:
                    if downloaded >= count:
                        break

                    img_url = item['urls']['regular']
                    filename = f"{category}_{downloaded + 1:03d}.jpg"
                    save_path = self.output_dir / category / filename

                    print(f"  [{downloaded + 1}/{count}] {filename}...", end=' ')

                    if self.download_image(img_url, save_path):
                        print("✅")
                        downloaded += 1
                    else:
                        print("❌")

                    time.sleep(0.5)

                page += 1

            except Exception as e:
                print(f"\n❌ API 오류: {e}")
                break

        return downloaded

    def collect_pexels(self, query, count, category):
        """Pexels API로 자동 수집"""
        print(f"\n📥 Pexels에서 '{query}' 검색 중...")

        api_key = os.getenv('PEXELS_API_KEY')
        if not api_key:
            print("\n⚠️ Pexels API 키가 필요합니다")
            print("1. https://www.pexels.com/api/ 접속")
            print("2. 회원가입 (무료)")
            print("3. API Key 복사")
            print("")
            api_key = input("API Key 입력: ").strip()

            if not api_key:
                print("❌ API 키 없이는 수집 불가")
                return 0

        url = "https://api.pexels.com/v1/search"
        headers = {'Authorization': api_key}

        downloaded = 0
        page = 1

        while downloaded < count:
            per_page = min(80, count - downloaded)

            params = {
                'query': query,
                'per_page': per_page,
                'page': page,
                'orientation': 'portrait'
            }

            try:
                response = requests.get(url, params=params, headers=headers)
                response.raise_for_status()
                data = response.json()

                photos = data.get('photos', [])
                if not photos:
                    print(f"  ⚠️ 더 이상 이미지 없음 (페이지 {page})")
                    break

                for photo in photos:
                    if downloaded >= count:
                        break

                    img_url = photo['src']['large']
                    filename = f"{category}_{downloaded + 1:03d}.jpg"
                    save_path = self.output_dir / category / filename

                    print(f"  [{downloaded + 1}/{count}] {filename}...", end=' ')

                    if self.download_image(img_url, save_path):
                        print("✅")
                        downloaded += 1
                    else:
                        print("❌")

                    time.sleep(0.5)

                page += 1

            except Exception as e:
                print(f"\n❌ API 오류: {e}")
                break

        return downloaded

    def quick_setup(self):
        """빠른 전체 수집"""
        print("=" * 70)
        print("🚀 자동 이미지 수집")
        print("=" * 70)

        print("\nAPI 선택:")
        print("1. Pexels (추천, 무료)")
        print("2. Unsplash (무료)")

        api_choice = input("\n선택: ").strip()

        if api_choice == '1':
            api_type = 'pexels'
            collect_func = self.collect_pexels
        elif api_choice == '2':
            api_type = 'unsplash'
            collect_func = self.collect_unsplash
        else:
            print("❌ 잘못된 선택")
            return

        print("\n" + "=" * 70)
        print("📋 수집 계획")
        print("=" * 70)

        # 설정
        collections = {
            'models': {
                'query': 'fashion model full body',
                'count': 30
            },
            'tops': {
                'query': 'white tshirt clothing product',
                'count': 5
            },
            'bottoms': {
                'query': 'blue jeans pants product',
                'count': 5
            },
            'dresses': {
                'query': 'dress fashion clothing product',
                'count': 5
            }
        }

        print("\n수집 목록:")
        for cat, info in collections.items():
            print(f"  {cat:10s}: {info['count']:2d}개 ('{info['query']}')")

        total = sum(c['count'] for c in collections.values())
        print(f"\n총 {total}개 이미지")

        confirm = input("\n시작하시겠습니까? (y/n): ").strip().lower()
        if confirm != 'y':
            print("취소됨")
            return

        # 수집 시작
        print("\n" + "=" * 70)
        print("수집 시작!")
        print("=" * 70)

        results = {}
        for category, info in collections.items():
            print(f"\n{'=' * 70}")
            print(f"📁 카테고리: {category}")
            print(f"{'=' * 70}")

            count = collect_func(
                query=info['query'],
                count=info['count'],
                category=category
            )

            results[category] = count
            print(f"\n✅ {category}: {count}/{info['count']}개 수집 완료")

            time.sleep(1)

        # 결과 요약
        print("\n" + "=" * 70)
        print("📊 수집 결과")
        print("=" * 70)

        total_downloaded = sum(results.values())
        print(f"\n총 {total_downloaded}/{total}개 수집 완료")
        print(f"\n카테고리별:")
        for cat, count in results.items():
            print(f"  {cat:10s}: {count:2d}개")

        print(f"\n📁 저장 위치: {self.output_dir}")


def main():
    crawler = AutoCrawler()

    print("\n환경 변수 설정 (선택):")
    print("  Pexels: export PEXELS_API_KEY='your_key'")
    print("  Unsplash: export UNSPLASH_ACCESS_KEY='your_key'")
    print("\n설정 안 했으면 실행 중 입력하면 됩니다.\n")

    crawler.quick_setup()


if __name__ == '__main__':
    main()