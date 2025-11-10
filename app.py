from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import os # 파일 업로드를 위해 필요


app = Flask(__name__)
app.config["SECRET_KEY"] = "helloosp" 
app.config['UPLOAD_FOLDER'] = 'static/img' # 업로드 폴더 설정 통일
# DB handler 한 번만 생성
DB = DBhandler()



# 샘플 상품 목록 (위치 변경 없음)
products = [
    {'item_id': 101, 'name': '롬앤 컬러 립글로스', 'price': 9900, 'image': 'img/romn_gloss.jpeg'},
    {'item_id': 102, 'name': '맥 립스틱', 'price': 10000, 'image': 'img/lipstick.jpeg'},
    {'item_id': 103, 'name': '맨유 유니폼(호날두)', 'price': 70000, 'image': 'img/uniform.jpeg'},
    {'item_id': 104, 'name': '나이키 운동화(250)', 'price': 40000, 'image': 'img/shoes_nike.jpeg'},
    {'item_id': 105, 'name': '탁상용 선풍기', 'price': 10000, 'image': 'img/fan.jpeg'},
    {'item_id': 106, 'name': '자라 운동화(235)', 'price': 30000, 'image': 'img/shoes_zara.jpeg'},
    {'item_id': 107, 'name': '전공책(기본간호수기)', 'price': 5000, 'image': 'img/book.jpeg'},
]


@app.route('/')
def index():
    return render_template('home.html')


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

@app.route('/product-register')
def product_register():
    return render_template('product-register.html')

@app.route('/review-list')
def review_list():
    reviews = DB.get_all_reviews()
    return render_template('review-list.html', reviews=reviews) 

@app.route('/review/<title>')
def review_detail(title):
    review = DB.get_review_by_title(title)
    if review:
        return render_template('detailed-review.html', review=review) 
    else:
        return "리뷰를 찾을 수 없습니다.", 404

@app.route('/review/new', methods=['GET', 'POST'])
def review_register(): 
    if request.method == 'POST':
        # 파일 업로드 로직
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                # 💡 UPLOAD_FOLDER가 이제 정확히 정의되었으므로 작동합니다.
                filename = file.filename
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_path = f'img/{filename}' 
            else:
                image_path = 'img/default.png'
        else:
            image_path = 'img/default.png'
            
        review_data = {
            "review-id": request.form['review-id'], 
            "product_name": request.form['product_name'],
            "title": request.form['title'],
            "rating": request.form['rating'],
            "content": request.form['content'],
            "image": image_path 
        }
        DB.add_review(review_data)
        return redirect(url_for('review_list'))
    
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
    exists = not DB.user_duplicate_check(user_id)   # 중복이면 False를 반환하니까 반전
    return jsonify({"exists": exists})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        id_ = request.form['id']  # user_id 대신 id_를 사용해도 되지만 일관성을 위해 id_ 유지
        pw = request.form['pw']
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        # DBhandler의 find_user 함수를 사용하는 main 브랜치 로직 채택
        if DB.find_user(id_, pw_hash):
            session['user'] = id_  # 로그인 성공하면 세션에 저장
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
            product_ref = DB.db.child("products").order_by_child("item_id").equal_to(str(item_id)).get()
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
    wished = DB.toggle_wishlist(user_id, str(item_id))
    
    return {"success": True, "wished": wished}

@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("로그아웃 되었습니다.")
    return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    products_ref = DB.db.child("products").get()
    products = [p.val() for p in products_ref.each()] if products_ref.each() else []

    # image 경로 조정
    for p in products:
        if p.get("image", "").startswith("/static/"):
            p["image"] = p["image"].replace("/static/", "")

    # item_id 비교
    product = next((p for p in products if str(p['item_id']) == str(product_id)), None)
    
    if not product:
        return "해당 상품을 찾을 수 없습니다.", 404

    return render_template('product-detail.html', product=product)


if __name__ == '__main__':
    # 조건부 샘플 리뷰 데이터 추가
    initial_reviews = DB.get_all_reviews() 

    if not initial_reviews: 
        sample_reviews = [
            {
                "review-id": "cosmelover",          
                "product_name": "롬앤 컬러 립글로스",
                "title": "부드럽게 잘 발려요!",
                "rating": "4",
                "content": "누디한 색상도 마음에 들고 입술 주름이 펴지면서 예쁜 광택이 생겨요! 다른 색상으로 또 사볼까 합니다.",
                "image": "img/review_lipgloss.jpg"
            },
            {
                "review-id": "studyabc",            
                "product_name": "두잇 알고리즘 코딩 테스트 C++편",
                "title": "책 상태가 좋습니다.",
                "rating": "4",
                "content": "누가 사용한 흔적도 거의 보이지 않고 깨끗한 책이네요.",
                "image": "img/review_book.jpg"
            },
            {
                "review-id": "hatesummer",          
                "product_name": "Windpia 핸디 선풍기",
                "title": "꽤 시원해요!",
                "rating": "3",
                "content": "단계도 4단계나 있고 꽤 시원한데 좀만 더 조용했으면 좋았을 듯",
                "image": "img/review_fan.jpg"
            }
        ]
        
        for r in sample_reviews:
            DB.add_review(r)
        
    app.run(debug=True)