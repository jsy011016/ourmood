# api_server.py (전체)

from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
from db_models import db, Product
import os
from werkzeug.utils import secure_filename
from datetime import datetime
import base64
import io
from PIL import Image

# ⭐ CNN 모듈 import
from predict_core import load_model, predict_from_pil, predict_from_bytes

app = Flask(__name__)
CORS(app)

# DB 설정
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ourmood.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/products'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# DB 초기화
db.init_app(app)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

with app.app_context():
    db.create_all()
    print("✅ Database initialized!")

# ⭐ CNN 모델 로드
load_model()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ==================== 상품 API ====================

@app.route('/api/products', methods=['GET'])
def get_products():
    """상품 목록 조회"""
    try:
        category = request.args.get('category', 'all')
        product_type = request.args.get('type')

        query = Product.query.filter_by(is_active=True)

        if category != 'all':
            query = query.filter_by(category=category)

        if product_type:
            query = query.filter_by(type=product_type)

        products = query.order_by(Product.created_at.desc()).all()

        return jsonify({
            'success': True,
            'count': len(products),
            'products': [p.to_dict() for p in products]
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """특정 상품 조회"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'success': True,
            'product': product.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 404


# ==================== 좋아요 API ====================

@app.route('/api/products/<int:product_id>/like', methods=['POST'])
def like_product(product_id):
    """좋아요 추가"""
    try:
        product = Product.query.get_or_404(product_id)
        product.likes += 1
        db.session.commit()

        return jsonify({
            'success': True,
            'product_id': product_id,
            'likes': product.likes
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/products/<int:product_id>/unlike', methods=['POST'])
def unlike_product(product_id):
    """좋아요 취소"""
    try:
        product = Product.query.get_or_404(product_id)
        if product.likes > 0:
            product.likes -= 1
        db.session.commit()

        return jsonify({
            'success': True,
            'product_id': product_id,
            'likes': product.likes
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ⭐ CNN 자동 분류 API ====================

@app.route('/api/classify-image', methods=['POST'])
def classify_image():
    """이미지를 받아서 AI가 코어 자동 분류"""
    try:
        # Base64 이미지
        if request.json and 'image' in request.json:
            image_base64 = request.json['image']

            if ',' in image_base64:
                image_base64 = image_base64.split(',')[1]

            image_bytes = base64.b64decode(image_base64)
            image = Image.open(io.BytesIO(image_bytes))

        # 파일 업로드
        elif 'image' in request.files:
            file = request.files['image']
            image = Image.open(file.stream)

        else:
            return jsonify({'success': False, 'error': 'No image provided'}), 400

        # ⭐ CNN 예측
        predicted_class, confidence, probs = predict_from_pil(image)

        return jsonify({
            'success': True,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'probabilities': probs
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ⭐ 관리자 - AI 자동 분류 업로드 ====================

@app.route('/api/admin/upload-product', methods=['POST'])
def upload_product():
    """관리자 상품 등록 - AI 자동 코어 분류!"""
    try:
        # 이미지 검증
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image'}), 400

        file = request.files['image']
        if not file or file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type'}), 400

        # ⭐ AI 자동 분류
        file.stream.seek(0)
        image = Image.open(file.stream)
        predicted_class, confidence, probs = predict_from_pil(image)

        print(f"🤖 AI 분류: {predicted_class} ({confidence:.2f}%)")

        # 이미지 저장
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)

        file.stream.seek(0)
        file.save(filepath)

        # 폼 데이터
        name = request.form.get('name')
        product_type = request.form.get('type')
        price = request.form.get('price')
        description = request.form.get('description', '')
        purchase_url = request.form.get('purchase_url', '')

        # 유효성 검사
        if not all([name, product_type, price]):
            return jsonify({'success': False, 'error': 'Missing fields'}), 400

        # DB 저장
        product = Product(
            name=name,
            category=predicted_class,
            confidence=confidence,
            type=product_type,
            price=price,
            description=description,
            image_url=f'/uploads/products/{unique_filename}',
            image_filename=unique_filename,
            purchase_url=purchase_url
        )

        db.session.add(product)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Product uploaded with AI classification',
            'product': product.to_dict(),
            'ai_classification': {
                'predicted_class': predicted_class,
                'confidence': confidence,
                'probabilities': probs
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/products', methods=['GET'])
def get_all_products_admin():
    """관리자 - 전체 상품"""
    try:
        products = Product.query.order_by(Product.created_at.desc()).all()
        return jsonify({
            'success': True,
            'count': len(products),
            'products': [p.to_dict() for p in products]
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """관리자 - 상품 삭제"""
    try:
        product = Product.query.get_or_404(product_id)

        # 이미지 파일 삭제
        if product.image_filename:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], product.image_filename)
            if os.path.exists(filepath):
                os.remove(filepath)

        db.session.delete(product)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Deleted'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== 정적 파일 ====================

@app.route('/uploads/products/<filename>')
def serve_product_image(filename):
    """이미지 서빙"""
    try:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        print(f"🖼️  Request: {filename}")
        print(f"📁 Full path: {filepath}")
        print(f"✅ Exists: {os.path.exists(filepath)}")

        if not os.path.exists(filepath):
            return jsonify({'error': 'File not found', 'path': filepath}), 404

        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/test-files')
def test_files():
    """업로드된 파일 목록 확인"""
    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        files = os.listdir(upload_folder)

        file_info = []
        for f in files:
            filepath = os.path.join(upload_folder, f)
            file_info.append({
                'filename': f,
                'size': os.path.getsize(filepath),
                'url': f'/uploads/products/{f}'
            })

        return jsonify({
            'success': True,
            'folder': os.path.abspath(upload_folder),
            'count': len(files),
            'files': file_info
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== 서버 실행 ====================

if __name__ == '__main__':
    upload_path = os.path.abspath(app.config['UPLOAD_FOLDER'])

    print("\n" + "=" * 60)
    print("🛍️ ourmood API 서버 시작!")
    print(f"📁 Upload folder: {upload_path}")
    print(f"📂 Folder exists: {os.path.exists(upload_path)}")

    if os.path.exists(upload_path):
        files = os.listdir(upload_path)
        print(f"📸 Images: {len(files)} files")
        if files:
            print(f"   예시: {files[0]}")

    print("📍 Server: http://localhost:5001")
    print("🤖 AI 자동 분류: 활성화")
    print("=" * 60 + "\n")

    app.run(
        host='0.0.0.0',
        port=5001,
        debug=True
    )