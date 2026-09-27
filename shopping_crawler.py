# shopping_crawler.py

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json


class ShoppingCrawler:
    def __init__(self):
        # Selenium 설정 (JavaScript 렌더링 필요)
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 백그라운드 실행
        self.driver = webdriver.Chrome(options=options)

    def crawl_musinsa(self, product_url):
        """무신사 상품 크롤링"""
        try:
            self.driver.get(product_url)
            time.sleep(2)

            # 상품명
            name = self.driver.find_element(By.CSS_SELECTOR, 'span.product_title').text

            # 가격
            price = self.driver.find_element(By.CSS_SELECTOR, 'span.product_price').text

            # 이미지
            img_elem = self.driver.find_element(By.CSS_SELECTOR, 'div.product-img img')
            image_url = img_elem.get_attribute('src')

            # 설명
            try:
                description = self.driver.find_element(By.CSS_SELECTOR, 'div.product_article').text
            except:
                description = ""

            return {
                'name': name,
                'price': price,
                'image_url': image_url,
                'description': description,
                'source': 'musinsa',
                'url': product_url
            }

        except Exception as e:
            print(f"❌ 크롤링 실패: {str(e)}")
            return None

    def crawl_ably(self, product_url):
        """에이블리 상품 크롤링"""
        try:
            self.driver.get(product_url)
            time.sleep(2)

            # 상품명
            name = self.driver.find_element(By.CSS_SELECTOR, 'h1.product-name').text

            # 가격
            price = self.driver.find_element(By.CSS_SELECTOR, 'span.price').text

            # 이미지
            img_elem = self.driver.find_element(By.CSS_SELECTOR, 'img.product-image')
            image_url = img_elem.get_attribute('src')

            return {
                'name': name,
                'price': price,
                'image_url': image_url,
                'description': '',
                'source': 'ably',
                'url': product_url
            }

        except Exception as e:
            print(f"❌ 크롤링 실패: {str(e)}")
            return None

    def crawl_product(self, url):
        """URL에 따라 적절한 크롤러 선택"""
        if 'musinsa.com' in url:
            return self.crawl_musinsa(url)
        elif 'a-bly.com' in url:
            return self.crawl_ably(url)
        else:
            print("❌ 지원하지 않는 쇼핑몰")
            return None

    def close(self):
        self.driver.quit()


# 사용 예시
if __name__ == '__main__':
    crawler = ShoppingCrawler()

    # 테스트 URL
    test_urls = [
        'https://www.musinsa.com/products/XXXXX',  # 실제 URL로 교체
        'https://a-bly.com/goods/XXXXX'
    ]

    for url in test_urls:
        print(f"\n🔍 크롤링: {url}")
        product = crawler.crawl_product(url)

        if product:
            print(f"✅ 상품명: {product['name']}")
            print(f"💰 가격: {product['price']}")
            print(f"🖼️  이미지: {product['image_url']}")

    crawler.close()