'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

const CATEGORIES = {
  all: { 
    name: '전체', 
    emoji: '🛍️', 
    color: 'from-gray-600 to-gray-800',
    description: '모든 스타일'
  },
  balletcore: { 
    name: '발레코어', 
    emoji: '🩰', 
    color: 'from-pink-400 via-pink-300 to-purple-300',
    description: '우아한 발레리나 감성'
  },
  angelcore: { 
    name: '엔젤코어', 
    emoji: '👼', 
    color: 'from-blue-50 via-white to-purple-50',
    textColor: 'text-gray-800',
    description: '천사처럼 순수한 화이트'
  },
  y2k: { 
    name: 'Y2K', 
    emoji: '🌈', 
    color: 'from-pink-500 via-purple-500 to-indigo-500',
    description: '2000년대 감성 네온'
  },
  darkacademia: { 
    name: '다크 아카데미아', 
    emoji: '📚', 
    color: 'from-amber-900 via-amber-800 to-stone-800',
    description: '클래식한 학구적 분위기'
  },
};

export default function Home() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [likedProducts, setLikedProducts] = useState(new Set());

  useEffect(() => {
    fetchProducts();
  }, [selectedCategory]);

  useEffect(() => {
    const saved = localStorage.getItem('likedProducts');
    if (saved) {
      setLikedProducts(new Set(JSON.parse(saved)));
    }
  }, []);

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

  const toggleLike = async (productId, e) => {
    e.stopPropagation();
    const isLiked = likedProducts.has(productId);
    const endpoint = isLiked ? 'unlike' : 'like';

    try {
      const response = await fetch(`http://localhost:5001/api/products/${productId}/${endpoint}`, {
        method: 'POST'
      });

      const data = await response.json();
      if (data.success) {
        const newLiked = new Set(likedProducts);
        if (isLiked) {
          newLiked.delete(productId);
        } else {
          newLiked.add(productId);
        }
        setLikedProducts(newLiked);
        localStorage.setItem('likedProducts', JSON.stringify([...newLiked]));

        setProducts(products.map(p =>
          p.id === productId ? { ...p, likes: data.likes } : p
        ));
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const likedCount = likedProducts.size;

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      {/* 헤더 */}
      <header className="bg-white/80 backdrop-blur-lg shadow-lg sticky top-0 z-50 border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/">
                <h1 className="text-3xl md:text-4xl font-black bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-clip-text text-transparent hover:scale-105 transition-transform cursor-pointer">
                  ourmood
                </h1>
              </Link>
              <div className="hidden md:flex items-center gap-2 bg-gradient-to-r from-purple-500 to-pink-500 text-white px-4 py-2 rounded-full shadow-md">
                <span className="font-bold text-sm">🤖 AI 자동 분류</span>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <Link 
                href="/favorites"
                className="relative bg-white border-2 border-purple-300 text-purple-700 px-4 md:px-6 py-2 md:py-3 rounded-full font-bold hover:bg-purple-50 transition-all flex items-center gap-2 group"
              >
                <span className="text-xl group-hover:scale-125 transition-transform">❤️</span>
                <span className="text-sm md:text-base">찜 목록</span>
                {likedCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs font-bold rounded-full w-6 h-6 flex items-center justify-center">
                    {likedCount}
                  </span>
                )}
              </Link>

              <Link 
                href="/fitting"
                className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-4 md:px-6 py-2 md:py-3 rounded-full font-bold hover:shadow-2xl transition-all transform hover:scale-105 flex items-center gap-2"
              >
                <span className="text-xl">👗</span>
                <span className="text-sm md:text-base">가상 피팅</span>
              </Link>
              
              <Link 
                href="/admin"
                className="bg-gray-800 text-white px-4 md:px-6 py-2 md:py-3 rounded-full font-bold hover:bg-gray-900 transition-all"
              >
                🔐
              </Link>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* 카테고리 필터 */}
        <div className="mb-8">
          <div className="flex items-center gap-3 overflow-x-auto pb-4 scrollbar-hide">
            {Object.entries(CATEGORIES).map(([key, cat]) => (
              <button
                key={key}
                onClick={() => setSelectedCategory(key)}
                className={`px-6 py-3 rounded-2xl font-bold whitespace-nowrap transition-all transform hover:scale-105 shadow-lg ${
                  selectedCategory === key
                    ? `bg-gradient-to-r ${cat.color} ${cat.textColor || 'text-white'} scale-105 shadow-2xl`
                    : 'bg-white text-gray-700 hover:bg-gray-50'
                }`}
              >
                <span className="mr-2 text-xl">{cat.emoji}</span>
                {cat.name}
              </button>
            ))}
          </div>

          <div className="mt-6 bg-white/90 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-purple-100">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-3xl font-black text-gray-800 mb-2 flex items-center gap-3">
                  <span>{CATEGORIES[selectedCategory].emoji}</span>
                  {CATEGORIES[selectedCategory].name}
                </h2>
                <p className="text-gray-600 font-medium">
                  {CATEGORIES[selectedCategory].description}
                </p>
              </div>
              <div className="text-right">
                <p className="text-5xl font-black bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  {products.length}
                </p>
                <p className="text-gray-500 text-sm font-semibold">개 상품</p>
              </div>
            </div>
          </div>
        </div>

        {/* 로딩 */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600 font-semibold">상품 불러오는 중...</p>
          </div>
        )}

        {/* 상품 그리드 */}
        {!loading && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {products.map(product => (
              <div
                key={product.id}
                className="bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-2 cursor-pointer group"
              >
                <div className="relative aspect-square overflow-hidden bg-gray-100">
                  <img
                    src={`http://localhost:5001${product.image_url}`}
                    alt={product.name}
                    className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/400x400/CCCCCC/666666?text=No+Image';
                    }}
                  />
                  
                  {/* 좋아요 버튼 */}
                  <button
                    onClick={(e) => toggleLike(product.id, e)}
                    className="absolute top-3 right-3 bg-white/95 backdrop-blur-sm p-2.5 rounded-full hover:scale-125 transition-all shadow-lg z-10"
                  >
                    {likedProducts.has(product.id) ? (
                      <span className="text-2xl animate-pulse">❤️</span>
                    ) : (
                      <span className="text-2xl">🤍</span>
                    )}
                  </button>

                  {/* 가상 피팅 버튼 */}
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-center pb-8">
                    <Link
                      href={`/fitting?cloth=${product.id}`}
                      className="bg-white text-gray-800 px-6 py-3 rounded-full font-bold text-sm hover:scale-110 transition-all shadow-xl"
                    >
                      👗 가상 피팅 해보기
                    </Link>
                  </div>

                  {/* 타입 뱃지 */}
                  <div className="absolute top-3 left-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-3 py-1.5 rounded-full text-xs font-bold shadow-lg">
                    {product.type === 'tops' ? '상의' : product.type === 'bottoms' ? '하의' : '원피스'}
                  </div>
                </div>

                <div className="p-5">
                  <h3 className="font-bold text-gray-800 mb-2 truncate text-lg">
                    {product.name}
                  </h3>
                  <div className="flex items-center justify-between">
                    <p className="text-xl font-black text-gray-900">
                      {product.price}
                    </p>
                    <div className="flex items-center gap-1.5 text-sm text-gray-500">
                      <span>❤️</span>
                      <span className="font-bold">{product.likes || 0}</span>
                    </div>
                  </div>
{product.purchase_url && (
    <a
      href={product.purchase_url}
      target="_blank"
      rel="noopener noreferrer"
      onClick={(e) => e.stopPropagation()}
      className="block w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white text-center py-2.5 rounded-xl font-bold hover:shadow-lg transition-all hover:scale-105"
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
          <div className="text-center py-20 bg-white/80 rounded-2xl">
            <p className="text-8xl mb-6">📦</p>
            <p className="text-2xl font-bold text-gray-800 mb-3">등록된 상품이 없습니다</p>
            <p className="text-gray-500 mb-6">관리자 페이지에서 상품을 추가해주세요</p>
            <Link
              href="/admin"
              className="inline-block bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-full font-bold hover:shadow-2xl transition-all transform hover:scale-105"
            >
              🔐 관리자 페이지로 가기
            </Link>
          </div>
        )}
      </div>

      <footer className="bg-white/80 backdrop-blur-lg mt-20 py-12 border-t border-purple-100">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="text-xl font-black bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-3">
            © 2025 ourmood
          </p>
          <p className="text-gray-600 font-semibold">
            🤖 AI 기반 패션 코어 자동 분류 시스템
          </p>
        </div>
      </footer>
    </div>
  );
}