from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib

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
app.config["SECRET_KEY"] = "helloosp"

DB = DBhandler()
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
#------회원가입
@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup_post", methods=['POST'])
def register_user():
    data = request.form
    pw = request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data, pw_hash):
        return render_template("login.html")
    else:
        flash("user id already exist!")
        return render_template("signup.html")

@app.route('/check_duplicate')
def check_duplicate():
    user_id = request.args.get('id')
    exists = not DB.user_duplicate_check(user_id)  # 중복이면 False를 반환하니까 반전
    return jsonify({"exists": exists})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form['id']
        pw = request.form['pw']
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        users = DB.db.child("user").get()
        for u in users.each():
            value = u.val()
            if value['id'] == user_id and value['pw'] == pw_hash:
                session['user'] = user_id  # 로그인 성공하면 세션에 저장
                return redirect(url_for('index'))  # 로그인 후 원래 화면으로
        flash("ID 또는 비밀번호가 잘못되었습니다.")
        return redirect(url_for('login'))
    else:
        return render_template("login.html")
    
#--------찜
@app.route("/wishlist")
def wishlist():
    if 'user' not in session:
        flash("로그인이 필요합니다.")
        return render_template("login.html")

    user_id = session['user']
    wishlist_data = DB.db.child("wishlist").order_by_child("user_id").equal_to(user_id).get()

        # .val()을 풀어서 리스트로 변환
    wishlist_items = []
    if wishlist_data.each():
        for item in wishlist_data.each():
            data = item.val()
            item_id = data.get("item_id")

            # 🔍 product DB에서 해당 상품 정보 가져오기
            product_ref = DB.db.child("products").order_by_child("item_id").equal_to(item_id).get()
            if product_ref.each():
                product_info = product_ref.each()[0].val()
                wishlist_items.append({
                    "item_id": product_info.get("item_id"),
                    "item_name": product_info.get("name"),
                    "item_price": product_info.get("price"),
                    "item_img": product_info.get("image")
                })
            else:
                # 상품 DB에 없을 때 대비
                wishlist_items.append({
                    "item_id": item_id,
                    "item_name": "알 수 없는 상품",
                    "item_price": "정보 없음",
                    "item_img": url_for('static', filename='img/default.png')
                })

    return render_template("wishlist.html", items=wishlist_items)

@app.route("/toggle_wishlist/<item_id>", methods=["POST"])
def toggle_wishlist(item_id):
    if 'user' not in session:
        return {"success": False, "msg": "로그인이 필요합니다."}

    user_id = session['user']
    wished = DB.toggle_wishlist(user_id, item_id)
    
    return {"success": True, "wished": wished}

@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("로그아웃 되었습니다.")
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    # product_id에 해당하는 상품 찾기
    product = next((p for p in products if p['id'] == product_id), None)
    
    if not product:
        return "해당 상품을 찾을 수 없습니다.", 404
    # product-detail.html 템플릿으로 상품 데이터 전달
    return render_template('product-detail.html', product=product)

products=[] #임시 작성 코드, 변경 필요 

    
if __name__ == '__main__':
    app.run(debug=True)