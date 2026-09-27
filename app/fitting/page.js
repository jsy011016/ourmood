// app/page.js

'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

const CATEGORIES = {
  all: { name: '전체', emoji: '🛍️', color: 'bg-gray-700' },
  balletcore: { name: '발레코어', emoji: '🩰', color: 'bg-gradient-to-r from-pink-300 to-purple-200' },
  angelcore: { name: '엔젤코어', emoji: '👼', color: 'bg-gradient-to-r from-white to-blue-100', textColor: 'text-gray-700' },
  y2k: { name: 'Y2K', emoji: '🌈', color: 'bg-gradient-to-r from-pink-500 to-purple-500' },
  darkacademia: { name: '다크 아카데미아', emoji: '📚', color: 'bg-gradient-to-r from-amber-800 to-stone-700' },
};

export default function Home() {
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [likedProducts, setLikedProducts] = useState(new Set());

  // ⭐ 상품 불러오기 (API에서)
  useEffect(() => {
    fetchProducts();
  }, [selectedCategory]);

  // ⭐ LocalStorage에서 좋아요 불러오기
  useEffect(() => {
    const saved = localStorage.getItem('likedProducts');
    if (saved) {
      setLikedProducts(new Set(JSON.parse(saved)));
    }
  }, []);

  // ⭐ API에서 상품 가져오기
  const fetchProducts = async () => {
    setLoading(true);
    try {
      const url = selectedCategory === 'all' 
        ? 'http://localhost:5001/api/products'
        : `http://localhost:5001/api/products?category=${selectedCategory}`;
      
      const response = await fetch(url);
      const data = await response.json();
      
      if (data.success) {
        setProducts(data.products);
      }
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  // ⭐ 좋아요 토글
  const toggleLike = async (productId) => {
    const isLiked = likedProducts.has(productId);
    const endpoint = isLiked ? 'unlike' : 'like';

    try {
      const response = await fetch(`http://localhost:5001/api/products/${productId}/${endpoint}`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        // LocalStorage 업데이트
        const newLiked = new Set(likedProducts);
        if (isLiked) {
          newLiked.delete(productId);
        } else {
          newLiked.add(productId);
        }
        setLikedProducts(newLiked);
        localStorage.setItem('likedProducts', JSON.stringify([...newLiked]));

        // 상품 목록 업데이트
        setProducts(products.map(p =>
          p.id === productId ? { ...p, likes: data.likes } : p
        ));
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 헤더 */}
      <header className="bg-white shadow-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              ourmood
            </h1>
            <div className="hidden md:flex items-center gap-2 bg-purple-50 px-4 py-2 rounded-full">
              <span className="text-purple-600 font-semibold text-sm">🤖 AI 코어 자동 분류</span>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <Link 
              href="/fitting"
              className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 md:px-6 py-2 md:py-3 rounded-full font-semibold hover:shadow-xl transition-all transform hover:scale-105 flex items-center gap-2"
            >
              <span className="text-xl">👗</span>
              <span className="text-sm md:text-base">가상 피팅</span>
            </Link>
            
            <Link 
              href="/admin"
              className="bg-gray-200 text-gray-700 px-4 md:px-6 py-2 md:py-3 rounded-full font-semibold hover:bg-gray-300 transition-all"
            >
              🔐 관리자
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 카테고리 필터 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 overflow-x-auto pb-4">
            {Object.entries(CATEGORIES).map(([key, cat]) => (
              <button
                key={key}
                onClick={() => setSelectedCategory(key)}
                className={`px-6 py-3 rounded-full font-semibold whitespace-nowrap transition-all transform hover:scale-105 shadow-lg ${
                  selectedCategory === key
                    ? `${cat.color} ${cat.textColor || 'text-white'} scale-105`
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <span className="mr-2">{cat.emoji}</span>
                {cat.name}
              </button>
            ))}
          </div>

          <div className="mt-4 bg-white rounded-xl p-6 shadow-md">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-800">
                {CATEGORIES[selectedCategory].emoji} {CATEGORIES[selectedCategory].name}
              </h2>
              <p className="text-gray-500">
                {products.length}개 상품
              </p>
            </div>
          </div>
        </div>

        {/* 로딩 */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600">상품 불러오는 중...</p>
          </div>
        )}

        {/* 상품 그리드 */}
        {!loading && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map(product => (
              <div
                key={product.id}
                className="bg-white rounded-xl overflow-hidden shadow-md hover:shadow-2xl transition-all transform hover:scale-105 cursor-pointer group"
              >
                <div className="relative aspect-square overflow-hidden bg-gray-100">
                  <img
                    src={`http://localhost:5001${product.image_url}`}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/400x400/CCCCCC/666666?text=No+Image';
                    }}
                  />
                  
                  {/* 좋아요 버튼 */}
                  <button
                    onClick={() => toggleLike(product.id)}
                    className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm p-2 rounded-full hover:bg-white transition-colors shadow-lg z-10"
                  >
                    {likedProducts.has(product.id) ? (
                      <span className="text-2xl">❤️</span>
                    ) : (
                      <span className="text-2xl">🤍</span>
                    )}
                  </button>

                  {/* 가상 피팅 버튼 */}
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                    <Link
                      href={`/fitting?cloth=${product.id}`}
                      className="bg-white text-gray-800 px-4 py-2 rounded-full font-semibold text-sm hover:bg-gray-100"
                    >
                      가상 피팅 해보기
                    </Link>
                  </div>

                  {/* 타입 뱃지 */}
                  <div className="absolute top-2 left-2 bg-black/70 text-white px-3 py-1 rounded-full text-xs font-semibold">
                    {product.type === 'tops' ? '상의' : product.type === 'bottoms' ? '하의' : '원피스'}
                  </div>
                </div>

                <div className="p-4">
                  <h3 className="font-semibold text-gray-800 mb-2 truncate">
                    {product.name}
                  </h3>
                  <div className="flex items-center justify-between">
                    <p className="text-lg font-bold text-gray-900">
                      {product.price}
                    </p>
                    <div className="flex items-center gap-1 text-sm text-gray-500">
                      <span>❤️</span>
                      <span>{product.likes || 0}</span>
                    </div>
                  </div>

                  {/* 구매 링크 */}
                  {product.purchase_url && (
                    
                      href={product.purchase_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="mt-3 block w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white text-center py-2 rounded-lg font-semibold text-sm hover:shadow-lg transition-all"
                      onClick={(e) => e.stopPropagation()}
                    >
                      🛒 구매하러 가기
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 상품 없을 때 */}
        {!loading && products.length === 0 && (
          <div className="text-center py-12">
            <p className="text-6xl mb-4">📦</p>
            <p className="text-xl text-gray-600 mb-2">등록된 상품이 없습니다</p>
            <p className="text-gray-500">관리자 페이지에서 상품을 추가해주세요</p>
            <Link
              href="/admin"
              className="inline-block mt-4 bg-purple-600 text-white px-6 py-3 rounded-full font-semibold hover:bg-purple-700"
            >
              🔐 관리자 페이지로 가기
            </Link>
          </div>
        )}
      </div>

      <footer className="bg-white mt-16 py-12 border-t">
        <div className="max-w-7xl mx-auto px-4 text-center text-gray-500 text-sm">
          <p className="font-semibold">© 2025 ourmood</p>
          <p className="mt-2">🤖 AI 기반 패션 코어 자동 분류 시스템</p>
        </div>
      </footer>
    </div>
  );
}