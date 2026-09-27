# unsplash_crawler.py

import requests
import os
import time
from urllib.request import urlretrieve

# ⬇️ 여기에 본인 키 입력!
ACCESS_KEY = "YOUR_UNSPLASH_ACCESS_KEY"

API_URL = "https://api.unsplash.com/search/photos"

# 검색 키워드
KEYWORDS = {
    'balletcore': [
        'ballet dress pink', 'tutu skirt', 'ballet fashion',
        'pink ballet', 'ballerina outfit', 'pastel ballet'
    ],
    'angelcore': [
        'white dress angel', 'ethereal white', 'angel aesthetic',
        'white lace', 'heavenly fashion', 'cream dress'
    ],
    'y2k': [
        'y2k fashion', '2000s aesthetic', 'neon fashion',
        'butterfly top', 'y2k outfit', 'colorful 2000s'
    ],
    'darkacademia': [
        'dark academia', 'brown blazer', 'plaid skirt',
        'tweed jacket', 'academic fashion', 'vintage scholar'
    ]
}


def download_images(core, keywords, per_keyword=25):
    """이미지 다운로드"""
    save_dir = f'dataset/raw/{core}'
    os.makedirs(save_dir, exist_ok=True)

    print(f"\n{'=' * 50}")
    print(f"📸 {core.upper()} 수집 시작!")
    print(f"{'=' * 50}\n")

    total = 0

    for keyword in keywords:
        print(f"🔍 검색: '{keyword}'")

        try:
            params = {
                'query': keyword,
                'per_page': per_keyword,
                'orientation': 'portrait'
            }
            headers = {'Authorization': f'Client-ID {ACCESS_KEY}'}

            response = requests.get(API_URL, params=params, headers=headers)

            if response.status_code != 200:
                print(f"  ❌ API 에러: {response.status_code}")
                continue

            results = response.json().get('results', [])
            print(f"  📥 {len(results)}개 발견!")

            for i, photo in enumerate(results):
                try:
                    img_url = photo['urls']['regular']
                    filename = f"{core}_{keyword.replace(' ', '_')}_{i}.jpg"
                    filepath = os.path.join(save_dir, filename)

                    urlretrieve(img_url, filepath)
                    total += 1
                    print(f"    ✅ {filename}")

                    time.sleep(0.5)  # Rate limit

                except Exception as e:
                    print(f"    ❌ 실패: {str(e)}")

            time.sleep(1)

        except Exception as e:
            print(f"  ❌ 검색 실패: {str(e)}")

    print(f"\n✅ {core} 완료! {total}개\n")
    return total


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🕷️  Unsplash 학습 데이터 수집")
    print("=" * 60)

    total_images = 0
    for core, keywords in KEYWORDS.items():
        count = download_images(core, keywords, per_keyword=25)
        total_images += count

    print("\n" + "=" * 60)
    print(f"🎉 수집 완료! 총 {total_images}개")
    print("=" * 60)