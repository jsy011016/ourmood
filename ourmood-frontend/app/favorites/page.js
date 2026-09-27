'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function FavoritesPage() {
  const router = useRouter();
  const [likedProducts, setLikedProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedProducts, setSelectedProducts] = useState(new Set());

  useEffect(() => {
    fetchLikedProducts();
  }, []);

  const fetchLikedProducts = async () => {
    setLoading(true);
    try {
      const saved = localStorage.getItem('likedProducts');
      if (!saved) {
        setLoading(false);
        return;
      }

      const likedIds = JSON.parse(saved);
      
      const response = await fetch('http://localhost:5001/api/products');
      const data = await response.json();
      
      if (data.success) {
        const filtered = data.products.filter(p => likedIds.includes(p.id));
        setLikedProducts(filtered);
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const removeLike = async (productId, e) => {
    e.stopPropagation();
    
    try {
      await fetch(`http://localhost:5001/api/products/${productId}/unlike`, {
        method: 'POST'
      });

      const saved = localStorage.getItem('likedProducts');
      const likedIds = JSON.parse(saved);
      const newLikedIds = likedIds.filter(id => id !== productId);
      localStorage.setItem('likedProducts', JSON.stringify(newLikedIds));

      setLikedProducts(likedProducts.filter(p => p.id !== productId));
      setSelectedProducts(prev => {
        const newSet = new Set(prev);
        newSet.delete(productId);
        return newSet;
      });
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const toggleSelection = (productId) => {
    setSelectedProducts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(productId)) {
        newSet.delete(productId);
      } else {
        newSet.add(productId);
      }
      return newSet;
    });
  };

  const goToFitting = () => {
    if (selectedProducts.size === 0) {
      alert('가상 피팅할 상품을 선택해주세요!');
      return;
    }
    
    const ids = Array.from(selectedProducts).join(',');
    router.push(`/fitting?clothes=${ids}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50">
      <header className="bg-white/80 backdrop-blur-lg shadow-lg sticky top-0 z-50 border-b border-purple-100">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link href="/" className="text-gray-600 hover:text-gray-800 transition-colors">
                <span className="text-2xl">←</span>
              </Link>
              <h1 className="text-2xl md:text-3xl font-black bg-gradient-to-r from-red-500 via-pink-500 to-purple-500 bg-clip-text text-transparent">
                ❤️ 찜 목록
              </h1>
            </div>
            
            <Link 
              href="/"
              className="bg-gray-200 text-gray-700 px-4 md:px-6 py-2 md:py-3 rounded-full font-bold hover:bg-gray-300 transition-all"
            >
              홈으로
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white/90 backdrop-blur-sm rounded-2xl p-8 shadow-xl border border-purple-100 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-black text-gray-800 mb-2">
                내가 찜한 상품들
              </h2>
              <p className="text-gray-600 font-medium">
                마음에 드는 옷을 선택하고 가상 피팅을 해보세요
              </p>
            </div>
            <div className="text-right">
              <p className="text-5xl font-black bg-gradient-to-r from-red-500 to-pink-600 bg-clip-text text-transparent">
                {likedProducts.length}
              </p>
              <p className="text-gray-500 text-sm font-semibold">개 상품</p>
            </div>
          </div>

          {likedProducts.length > 0 && (
            <div className="mt-6 pt-6 border-t border-gray-200 flex items-center justify-between">
              <div className="text-gray-700 font-semibold">
                {selectedProducts.size > 0 ? (
                  <span className="text-purple-600">
                    {selectedProducts.size}개 선택됨
                  </span>
                ) : (
                  <span>상품을 선택해주세요</span>
                )}
              </div>
              
              <button
                onClick={goToFitting}
                disabled={selectedProducts.size === 0}
                className={`px-8 py-3 rounded-full font-bold text-white transition-all transform hover:scale-105 ${
                  selectedProducts.size > 0
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 hover:shadow-2xl'
                    : 'bg-gray-300 cursor-not-allowed'
                }`}
              >
                👗 선택한 옷으로 가상 피팅하기
              </button>
            </div>
          )}
        </div>

        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-16 w-16 border-4 border-purple-500 border-t-transparent"></div>
            <p className="mt-4 text-gray-600 font-semibold">불러오는 중...</p>
          </div>
        )}

        {!loading && likedProducts.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            {likedProducts.map(product => (
              <div
                key={product.id}
                onClick={() => toggleSelection(product.id)}
                className={`bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all transform hover:-translate-y-2 cursor-pointer relative ${
                  selectedProducts.has(product.id) ? 'ring-4 ring-purple-500 scale-105' : ''
                }`}
              >
                {selectedProducts.has(product.id) && (
                  <div className="absolute top-3 left-3 bg-purple-600 text-white rounded-full w-10 h-10 flex items-center justify-center z-10 shadow-lg">
                    <span className="text-2xl">✓</span>
                  </div>
                )}

                <div className="relative aspect-square overflow-hidden bg-gray-100">
                  <img
                    src={`http://localhost:5001${product.image_url}`}
                    alt={product.name}
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/400x400/CCCCCC/666666?text=No+Image';
                    }}
                  />
                  
                  <button
                    onClick={(e) => removeLike(product.id, e)}
                    className="absolute top-3 right-3 bg-white/95 backdrop-blur-sm p-2.5 rounded-full hover:scale-125 transition-all shadow-lg z-10"
                  >
                    <span className="text-xl">🗑️</span>
                  </button>

                  <div className="absolute bottom-3 left-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white px-3 py-1.5 rounded-full text-xs font-bold shadow-lg">
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
                </div>
              </div>
            ))}
          </div>
        )}

        {!loading && likedProducts.length === 0 && (
          <div className="text-center py-20 bg-white/80 rounded-2xl">
            <p className="text-8xl mb-6">💔</p>
            <p className="text-2xl font-bold text-gray-800 mb-3">찜한 상품이 없습니다</p>
            <p className="text-gray-500 mb-6">마음에 드는 상품에 하트를 눌러보세요!</p>
            <Link
              href="/"
              className="inline-block bg-gradient-to-r from-purple-600 to-pink-600 text-white px-8 py-4 rounded-full font-bold hover:shadow-2xl transition-all transform hover:scale-105"
            >
              쇼핑하러 가기
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
