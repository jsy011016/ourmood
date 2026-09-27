# auto_register.py

import requests
from shopping_crawler import ShoppingCrawler
from predict import predict_from_url
import time

API_URL = "http://localhost:5001/api/admin/upload-product-from-url"


def auto_register_product(product_url):
    """
    쇼핑몰 URL → 크롤링 → AI 분류 → DB 등록
    """
    print(f"\n{'=' * 60}")
    print(f"🤖 자동 등록 시작: {product_url}")
    print(f"{'=' * 60}\n")

    # 1. 쇼핑몰 크롤링
    print("📥 Step 1: 상품 정보 크롤링...")
    crawler = ShoppingCrawler()
    product_info = crawler.crawl_product(product_url)
    crawler.close()

    if not product_info:
        print("❌ 크롤링 실패!")
        return False

    print(f"  ✅ 상품명: {product_info['name']}")
    print(f"  💰 가격: {product_info['price']}")
    print(f"  🖼️  이미지: {product_info['image_url']}\n")

    # 2. AI 코어 분류
    print("🤖 Step 2: AI 코어 자동 분류...")
    predicted_core, confidence, probs = predict_from_url(product_info['image_url'])

    if not predicted_core:
        print("❌ AI 분류 실패!")
        return False

    print(f"  ✅ 분류 결과: {predicted_core}")
    print(f"  📊 신뢰도: {confidence:.2f}%\n")

    # 3. DB에 등록
    print("💾 Step 3: 데이터베이스 등록...")

    data = {
        'name': product_info['name'],
        'category': predicted_core,  # AI 자동 분류!
        'confidence': confidence,
        'type': 'tops',  # TODO: 상의/하의 자동 분류도 추가 가능
        'price': product_info['price'],
        'description': product_info.get('description', ''),
        'purchase_url': product_url,
        'image_url': product_info['image_url']
    }

    try:
        response = requests.post(API_URL, json=data)
        result = response.json()

        if result['success']:
            print("  ✅ 등록 완료!\n")
            print(f"{'=' * 60}")
            print(f"🎉 자동 등록 성공!")
            print(f"   상품 ID: {result['product']['id']}")
            print(f"   코어: {predicted_core} ({confidence:.1f}%)")
            print(f"{'=' * 60}\n")
            return True
        else:
            print(f"  ❌ 등록 실패: {result.get('error')}")
            return False

    except Exception as e:
        print(f"  ❌ API 에러: {str(e)}")
        return False


def batch_register(url_list):
    """여러 상품 일괄 등록"""
    print(f"\n🚀 일괄 등록 시작! ({len(url_list)}개 상품)\n")

    success_count = 0

    for i, url in enumerate(url_list, 1):
        print(f"[{i}/{len(url_list)}]")

        if auto_register_product(url):
            success_count += 1

        time.sleep(2)  # 쇼핑몰 서버 부하 방지

    print(f"\n{'=' * 60}")
    print(f"📊 일괄 등록 완료!")
    print(f"   성공: {success_count}/{len(url_list)}")
    print(f"   실패: {len(url_list) - success_count}/{len(url_list)}")
    print(f"{'=' * 60}\n")


if __name__ == '__main__':
    # 테스트: 단일 상품 등록
    test_url = "https://www.musinsa.com/products/XXXXX"  # 실제 URL로 교체
    auto_register_product(test_url)

    # 테스트: 여러 상품 일괄 등록
    # url_list = [
    #     "https://www.musinsa.com/products/XXXXX",
    #     "https://www.musinsa.com/products/YYYYY",
    #     "https://a-bly.com/goods/ZZZZZ"
    # ]
    # batch_register(url_list)