"""
간단한 의상 이미지 크롤러
- 무신사, Unsplash 등에서 이미지 수집
- 카테고리별 자동 분류
"""

import requests
from pathlib import Path
import time
from PIL import Image
import io


class SimpleCrawler:
    def __init__(self, output_dir='test_images'):
        self.output_dir = Path(output_dir)
        self.setup_dirs()

    def setup_dirs(self):
        """폴더 구조 생성"""
        dirs = ['models', 'tops', 'bottoms', 'outers', 'dresses']
        for d in dirs:
            (self.output_dir / d).mkdir(parents=True, exist_ok=True)

    def download_from_url(self, url, save_path):
        """URL에서 이미지 다운로드"""
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            img = Image.open(io.BytesIO(response.content))
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # 크기 조정 (너무 크면)
            if max(img.size) > 1024:
                ratio = 1024 / max(img.size)
                new_size = tuple(int(d * ratio) for d in img.size)
                img = img.resize(new_size, Image.LANCZOS)

            img.save(save_path, 'JPEG', quality=90)
            print(f"✅ 저장: {save_path.name}")
            return True
        except Exception as e:
            print(f"❌ 실패: {e}")
            return False

    def collect_unsplash_images(self, query, category, count=10):
        """
        Unsplash에서 무료 이미지 수집
        API 키 필요: https://unsplash.com/developers
        """
        api_key = input(f"Unsplash API 키를 입력하세요 (없으면 Enter): ").strip()

        if not api_key:
            print("⚠️ API 키 없이는 수집할 수 없습니다")
            print("   https://unsplash.com/developers 에서 무료로 발급 가능")
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
                filename = f"{category}_{idx + 1}.jpg"
                save_path = self.output_dir / category / filename

                if self.download_from_url(img_url, save_path):
                    downloaded.append(str(save_path))
                    time.sleep(0.5)

            return downloaded
        except Exception as e:
            print(f"❌ Unsplash 오류: {e}")
            return []

    def manual_download(self, urls_file, category):
        """
        텍스트 파일에서 URL 목록을 읽어서 다운로드
        urls_file 형식:
        https://image1.jpg
        https://image2.jpg
        """
        if not Path(urls_file).exists():
            print(f"❌ 파일 없음: {urls_file}")
            return

        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        print(f"\n📥 {len(urls)}개 이미지 다운로드 시작...")

        for idx, url in enumerate(urls, 1):
            filename = f"{category}_{idx}.jpg"
            save_path = self.output_dir / category / filename
            print(f"[{idx}/{len(urls)}] ", end='')
            self.download_from_url(url, save_path)
            time.sleep(0.5)

    def quick_collect(self):
        """빠른 샘플 수집 (수동 URL 입력)"""
        print("=" * 60)
        print("🎨 간단한 이미지 수집")
        print("=" * 60)

        categories = {
            '1': ('models', '모델 (전신)'),
            '2': ('tops', '상의'),
            '3': ('bottoms', '하의'),
            '4': ('outers', '아우터'),
            '5': ('dresses', '원피스')
        }

        print("\n카테고리:")
        for key, (cat, name) in categories.items():
            print(f"  {key}. {name}")

        choice = input("\n선택: ").strip()
        category, name = categories.get(choice, (None, None))

        if not category:
            print("❌ 잘못된 선택")
            return

        print(f"\n📸 {name} 이미지 URL을 입력하세요 (완료하려면 빈 줄)")
        print("예: https://example.com/image.jpg")

        urls = []
        while True:
            url = input(f"URL {len(urls) + 1}: ").strip()
            if not url:
                break
            urls.append(url)

        if not urls:
            print("⚠️ URL 없음")
            return

        print(f"\n다운로드 시작...")
        for idx, url in enumerate(urls, 1):
            filename = f"{category}_{int(time.time())}_{idx}.jpg"
            save_path = self.output_dir / category / filename
            print(f"[{idx}/{len(urls)}] ", end='')
            self.download_from_url(url, save_path)
            time.sleep(0.5)

        print(f"\n✅ 완료! 저장 위치: {self.output_dir / category}")


def main():
    crawler = SimpleCrawler()

    print("=" * 60)
    print("🕷️  이미지 크롤러")
    print("=" * 60)
    print("\n방법 선택:")
    print("1. 수동 URL 입력 (권장)")
    print("2. Unsplash API 사용")
    print("3. URL 목록 파일에서 읽기")

    choice = input("\n선택: ").strip()

    if choice == '1':
        crawler.quick_collect()

    elif choice == '2':
        print("\nUnsplash 카테고리별 수집")
        queries = {
            'models': 'fashion model full body',
            'tops': 'white tshirt clothing',
            'bottoms': 'blue jeans pants',
            'outers': 'jacket coat outerwear',
            'dresses': 'dress fashion clothing'
        }

        for category, query in queries.items():
            print(f"\n📥 {category} 수집 중...")
            crawler.collect_unsplash_images(query, category, count=5)
            time.sleep(1)

    elif choice == '3':
        category = input("카테고리 (models/tops/bottoms/outers/dresses): ").strip()
        urls_file = input("URL 목록 파일 경로: ").strip()
        crawler.manual_download(urls_file, category)

    print("\n✅ 수집 완료!")
    print(f"📁 저장 위치: {crawler.output_dir}")


if __name__ == '__main__':
    main()