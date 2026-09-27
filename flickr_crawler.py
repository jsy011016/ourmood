# flickr_crawler.py

import flickrapi
import urllib.request
import os
import time

# Flickr API 키 받기 (2분!)
# https://www.flickr.com/services/apps/create/apply
FLICKR_KEY = "YOUR_API_KEY"
FLICKR_SECRET = "YOUR_SECRET"

flickr = flickrapi.FlickrAPI(FLICKR_KEY, FLICKR_SECRET, format='parsed-json')

QUERIES = {
    'balletcore': [
        'ballet dress pink',
        'tutu skirt',
        'ballerina fashion',
        'pink ballet'
    ],
    'angelcore': [
        'white angel dress',
        'ethereal fashion',
        'white lace dress',
        'angel aesthetic'
    ],
    'y2k': [
        'y2k fashion',
        '2000s aesthetic',
        'neon outfit',
        'retro fashion'
    ],
    'darkacademia': [
        'dark academia',
        'brown blazer',
        'vintage fashion',
        'plaid skirt'
    ]
}


def download_flickr(core, queries, per_query=50):
    """Flickr에서 다운로드"""
    save_dir = f'dataset/raw/{core}'
    os.makedirs(save_dir, exist_ok=True)

    print(f"\n{'=' * 50}")
    print(f"📸 {core.upper()} 수집")
    print(f"{'=' * 50}\n")

    total = 0

    for query in queries:
        print(f"🔍 '{query}'...")

        try:
            photos = flickr.photos.search(
                text=query,
                per_page=per_query,
                media='photos',
                sort='relevance'
            )

            for i, photo in enumerate(photos['photos']['photo']):
                try:
                    # URL 생성
                    url = f"https://live.staticflickr.com/{photo['server']}/{photo['id']}_{photo['secret']}_b.jpg"

                    filename = f"{core}_{query.replace(' ', '_')}_{i}.jpg"
                    filepath = os.path.join(save_dir, filename)

                    urllib.request.urlretrieve(url, filepath)
                    total += 1
                    print(f"  ✅ {filename}")

                    time.sleep(0.1)

                except Exception as e:
                    continue

            time.sleep(1)

        except Exception as e:
            print(f"  ❌ 실패: {str(e)}")

    print(f"\n✅ {core} 완료! {total}개\n")
    return total


if __name__ == '__main__':
    print("🕷️  Flickr 크롤링 시작!\n")

    total = 0
    for core, queries in QUERIES.items():
        count = download_flickr(core, queries, per_query=50)
        total += count

    print(f"\n🎉 완료! 총 {total}개")