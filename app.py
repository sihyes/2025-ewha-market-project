from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

products = [
    {'id': 101, 'name': '롬앤 컬러 립글로스', 'price': 9900, 'image': 'img/romn_gloss.jpeg'},
    {'id': 102, 'name': '맥 립스틱', 'price': 10000, 'image': 'img/lipstick.jpeg'},
    {'id': 103, 'name': '맨유 유니폼(호날두)', 'price': 70000, 'image': 'img/uniform.jpeg'},
    {'id': 104, 'name': '나이키 운동화(250)', 'price': 40000, 'image': 'img/shoes_nike.jpeg'},
    {'id': 105, 'name': '탁상용 선풍기', 'price': 10000, 'image': 'img/fan.jpeg'},
    {'id': 106, 'name': '자라 운동화(235)', 'price': 30000, 'image': 'img/shoes_zara.jpeg'},
    {'id': 107, 'name': '전공책(기본간호수기)', 'price': 5000, 'image': 'img/book.jpeg'},
]

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # 업로드 파일 저장 경로
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/feature-list')
def feature_list():
    return render_template('feature-list.html', products=products)

@app.route('/review-list')
def review_list():
    return render_template('review-list.html')

@app.route('/product-register')
def product_register():
    return render_template('product-register.html')

@app.route('/review-register')
def review_register():
    return render_template('review-register.html')

@app.route('/result', methods=['POST'])
def result():
    # 폼 데이터 가져오기
    seller_id = request.form.get('seller_id')
    name = request.form.get('name')
    price = request.form.get('price')
    region = request.form.get('region')
    condition = request.form.get('condition')
    description = request.form.get('description')
    image_url = request.form.get('image_url')
    image_file = request.files.get('image_file')

    uploaded_file_path = None

    # 파일 업로드 처리
    if image_file and image_file.filename != '':
        filename = secure_filename(image_file.filename)
        uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(uploaded_file_path)
        uploaded_file_path = '/' + uploaded_file_path  # 브라우저에서 접근할 수 있도록

    # 터미널 로그 확인
    print("판매자 아이디:", seller_id)
    print("상품명:", name)
    print("가격:", price)
    print("지역:", region)
    print("상태:", condition)
    print("설명:", description)
    print("이미지 URL:", image_url)
    print("업로드 파일 경로:", uploaded_file_path)

    return render_template( 
        'result.html', 
        seller_id=seller_id, 
        name=name, 
        price=price, 
        region=region, 
        condition=condition, 
        description=description, 
        image_url=image_url if image_url else None, 
        image_file=uploaded_file_path )

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return "해당 상품을 찾을 수 없습니다.", 404

    return render_template('product-detail.html', product=product)
  
if __name__ == '__main__':
    app.run(debug=True)
