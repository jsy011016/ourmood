# icrawler_download.py

from icrawler.builtin import GoogleImageCrawler, BingImageCrawler
import os

QUERIES = {
    'balletcore': [
        'ballet dress pink fashion',
        'tutu skirt pastel',
        'ballerina outfit aesthetic',
        'pink ballet clothing'
    ],
    'angelcore': [
        'white angel dress fashion',
        'ethereal white outfit',
        'angel aesthetic clothing',
        'cream white dress'
    ],
    'y2k': [
        'y2k fashion 2000s',
        'neon butterfly top',
        'colorful y2k aesthetic',
        'retro 2000s outfit'
    ],
    'darkacademia': [
        'dark academia fashion',
        'brown blazer outfit',
        'plaid skirt academic',
        'vintage scholar fashion'
    ]
}


def download_images(core, queries, images_per_query=40):
    """이미지 다운로드"""
    save_dir = f'dataset/raw/{core}'
    os.makedirs(save_dir, exist_ok=True)

    print(f"\n{'=' * 50}")
    print(f"📸 {core.upper()} 수집")
    print(f"{'=' * 50}\n")

    total = 0

    for query in queries:
        print(f"🔍 '{query}'...")

        try:
            # Google 크롤러 사용
            google_crawler = GoogleImageCrawler(
                storage={'root_dir': save_dir}
            )

            google_crawler.crawl(
                keyword=query,
                max_num=images_per_query,
                min_size=(200, 200),  # 최소 크기
                file_idx_offset='auto'
            )

            total += images_per_query
            print(f"  ✅ {images_per_query}개 다운로드\n")

        except Exception as e:
            print(f"  ❌ 실패: {str(e)}\n")

    print(f"✅ {core} 완료! 총 {total}개\n")
    return total


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("🕷️  icrawler 이미지 수집")
    print("=" * 60)

    total_images = 0

    for core, queries in QUERIES.items():
        count = download_images(core, queries, images_per_query=40)
        total_images += count

    print("=" * 60)
    print(f"🎉 전체 완료! 총 {total_images}개")
    print("=" * 60)