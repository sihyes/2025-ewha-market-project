from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # 업로드 파일 저장 경로
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

products=[]

@app.route('/')
def index():
    return render_template('index.html')

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

    product = {
        'id': len(products)+1,
        'seller_id': seller_id,
        'name': name,
        'price': int(price),
        'region': region,
        'condition': condition,
        'description': description,
        'image': uploaded_file_path if uploaded_file_path else image_url
    }
    products.append(product)

    return render_template('feature-list.html', products=products)
    
if __name__ == '__main__':
    app.run(debug=True)
