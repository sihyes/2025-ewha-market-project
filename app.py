from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feature-list')
def feature_list():
    return render_template('feature-list.html')

@app.route('/review-list')
def review_list():
    return render_template('review-list.html')

@app.route('/product-register')
def product_register():
    return render_template('product-register.html')

@app.route('/review-register')
def review_register():
    return render_template('review-register.html')

# 상품 등록 폼 제출 처리 라우트 추가
@app.route('/result', methods=['POST'])
def result():
    # 폼에서 보낸 데이터 가져오기
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    image = request.form.get('image')
    
    # 확인용 출력
    print("상품명:", name)
    print("가격:", price)
    print("설명:", description)
    print("이미지 URL:", image)
    
    # 리턴
    return f"""
    <h1>상품 등록 완료</h1>
    <p>상품명: {name}</p>
    <p>가격: {price}</p>
    <p>설명: {description}</p>
    <p>이미지: <img src="{image}" alt="상품 이미지" style="max-width:200px;"></p>
    <a href="/">홈으로 돌아가기</a>
    """

if __name__ == '__main__':
    app.run(debug=True)
