from flask import Flask, render_template
import os
from werkzeug.utils import secure_filename
from database import DBhandler


products = [
    {'id': 101, 'name': '롬앤 컬러 립글로스', 'price': 9900, 'image': 'img/romn_gloss.jpeg'},
    {'id': 102, 'name': '맥 립스틱', 'price': 10000, 'image': 'img/lipstick.jpeg'},
    {'id': 103, 'name': '맨유 유니폼(호날두)', 'price': 70000, 'image': 'img/uniform.jpeg'},
    {'id': 104, 'name': '나이키 운동화(250)', 'price': 40000, 'image': 'img/shoes_nike.jpeg'},
    {'id': 105, 'name': '탁상용 선풍기', 'price': 10000, 'image': 'img/fan.jpeg'},
    {'id': 106, 'name': '자라 운동화(235)', 'price': 30000, 'image': 'img/shoes_zara.jpeg'},
    {'id': 107, 'name': '전공책(기본간호수기)', 'price': 5000, 'image': 'img/book.jpeg'},
]

DB=DBhandler()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/feature-list')
def feature_list():
    # 1. DB에서 상품 가져오기
    products_ref = DB.db.child("products").get()
    products = [p.val() for p in products_ref.each()] if products_ref.each() else []

    # 2. image 경로 조정 (optional)
    for p in products:
        # 만약 DB에 '/static/img/파일명' 으로 저장되어 있으면 url_for용으로 변환
        if p.get("image", "").startswith("/static/"):
            p["image"] = p["image"].replace("/static/", "")

    # 3. 찜 목록 가져오기
    if 'user' in session:
        user_id = session['user']
        wishlist_data = DB.db.child("wishlist").order_by_child("user_id").equal_to(user_id).get()
        wished_item_ids = [str(item.val().get("item_id")) for item in wishlist_data.each()] if wishlist_data.each() else []
    else:
        wished_item_ids = []

    return render_template('feature-list.html', products=products, wished_item_ids=wished_item_ids)

@app.route('/review-list')
def review_list():
    return render_template('review-list.html')

@app.route('/product-register')
def product_register():
    return render_template('product-register.html')

@app.route('/review-register')
def review_register():
    return render_template('review-register.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # product_id에 해당하는 상품 찾기
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return "해당 상품을 찾을 수 없습니다.", 404

    # product-detail.html 템플릿으로 상품 데이터 전달
    return render_template('product-detail.html', product=product)

if __name__ == '__main__':
    app.run(debug=True)