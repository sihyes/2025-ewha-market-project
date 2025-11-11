from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "helloosp"
app.config['UPLOAD_FOLDER'] = 'static/img'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 허용된 파일 확장자
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """파일 확장자가 허용된 형식인지 확인"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 샘플 상품 목록
products = [
    {'item_id': 101, 'name': '롬앤 컬러 립글로스', 'price': 9900, 'image': 'img/romn_gloss.jpeg'},
    {'item_id': 102, 'name': '맥 립스틱', 'price': 10000, 'image': 'img/lipstick.jpeg'},
    {'item_id': 103, 'name': '맨유 유니폼(호날두)', 'price': 70000, 'image': 'img/uniform.jpeg'},
    {'item_id': 104, 'name': '나이키 운동화(250)', 'price': 40000, 'image': 'img/shoes_nike.jpeg'},
    {'item_id': 105, 'name': '탁상용 선풍기', 'price': 10000, 'image': 'img/fan.jpeg'},
    {'item_id': 106, 'name': '자라 운동화(235)', 'price': 30000, 'image': 'img/shoes_zara.jpeg'},
    {'item_id': 107, 'name': '전공책(기본간호수기)', 'price': 5000, 'image': 'img/book.jpeg'},
]

DB = DBhandler()

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/feature-list')
def feature_list():
     #1. 페이지네이션 파라미터
    page = request.args.get("page", 0, type=int)
    per_page = 10  # 한 페이지당 상품 10개
    per_row = 5

    # 2. DB에서 상품 가져오기
    products_ref = DB.db.child("products").get()
    products = []
    if products_ref.each():
        for p in products_ref.each():
            data = p.val()
            products.append({
                "item_id": data.get("item_id"),
                "name": data.get("name"),
                "price": data.get("price"),
                "region": data.get("region"),
                "condition": data.get("condition"),
                "description": data.get("description"),
                "image": data.get("image"),  # <- DB image 그대로 사용
                "seller_id": data.get("seller_id")
            })

    item_counts = len(products)

    # 3. 페이지별로 나누기 
    start_idx = page * per_page
    end_idx = start_idx + per_page
    products = products[start_idx:end_idx]

    # 4. image 경로 조정 (optional)
    for p in products:
        image = p.get("image", "")
        # 만약 DB에 '/static/img/파일명' 으로 저장되어 있으면 url_for용으로 변환
        if image.startswith("/static/"):
            p["image"] = image.replace("/static/", "")
        # 외부 URL인 경우 그대로 사용 (템플릿에서 처리)

    # 5. 찜 목록 가져오기
    if 'user' in session:
        user_id = session['user']
        wishlist_data = DB.db.child("wishlist").order_by_child("user_id").equal_to(user_id).get()
        wished_item_ids = [str(item.val().get("item_id")) for item in wishlist_data.each()] if wishlist_data.each() else []
    else:
        wished_item_ids = []
    
    # 6. 페이지 수 계산 
    page_count = (item_counts + per_page - 1) // per_page
    print("총 상품 개수:", item_counts, "페이지 수:", page_count)

    return render_template('feature-list.html', 
                           products=products, 
                           wished_item_ids=wished_item_ids,
                           page=page,
                           page_count=page_count,
                           total=item_counts)

@app.route('/product-register', methods=['GET', 'POST'])
def product_register():
    if request.method == 'POST':
        # 폼 데이터 받기
        seller_id = request.form.get('seller_id')
        name = request.form.get('name')
        price = request.form.get('price')
        region = request.form.get('region')
        condition = request.form.get('condition')
        description = request.form.get('description')
        image_url = request.form.get('image_url', '').strip()
        
        # 이미지 경로 처리
        image_path = ''
        
        # 1. 외부 URL이 제공된 경우
        if image_url:
            image_path = image_url
        # 2. 파일 업로드가 있는 경우
        elif 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename and allowed_file(file.filename):
                try:
                    # 안전한 파일명으로 변환
                    filename = secure_filename(file.filename)
                    # 고유한 파일명 생성 (타임스탬프 + 원본 파일명)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
                    file_ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'
                    unique_filename = f"{timestamp}_{filename}"
                    
                    # 업로드 폴더가 없으면 생성
                    upload_folder = app.config['UPLOAD_FOLDER']
                    if not os.path.exists(upload_folder):
                        os.makedirs(upload_folder)
                    
                    # 파일 저장
                    file_path = os.path.join(upload_folder, unique_filename)
                    file.save(file_path)
                    
                    # 데이터베이스에 저장할 경로 형식: 'img/파일명'
                    image_path = f'img/{unique_filename}'
                    flash(f'이미지가 성공적으로 업로드되었습니다: {unique_filename}')
                except Exception as e:
                    flash(f'이미지 업로드 중 오류가 발생했습니다: {str(e)}')
                    image_path = ''  # 업로드 실패 시 빈 문자열
            elif file and file.filename and not allowed_file(file.filename):
                flash('지원하지 않는 파일 형식입니다. (png, jpg, jpeg, gif, webp만 가능)')
                return redirect(url_for('product_register'))
        
        # 이미지가 없으면 기본값 사용하지 않고 경고 (선택사항으로 변경 가능)
        if not image_path:
            flash('이미지를 업로드하거나 URL을 입력해주세요.')
            return redirect(url_for('product_register'))
        
        # Firebase에 상품 저장
        if DB.insert_product(seller_id, name, price, region, condition, description, image_path):
            flash('상품이 등록되었습니다.')
            return redirect(url_for('feature_list'))
        else:
            flash('상품 등록에 실패했습니다.')
            return redirect(url_for('product_register'))
    
    return render_template('product-register.html')

@app.route("/review-list")
def review_list():
    return render_template("review-list.html") 

@app.route("/review-register")
def review_register():
    return render_template('review-register.html')

@app.route("/review-detail")
def simple_review_detail():
    """
    모든 리뷰 카드가 연결될 하드코딩된 상세 페이지 엔드포인트입니다.
    ID를 받지 않고, 단순히 템플릿만 렌더링합니다.
    """
    return render_template("detailed-review.html")

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
            product_ref = DB.db.child("products").order_by_child("item_id").equal_to(str(item_id)).get() 
            if product_ref.each(): 
                product_info = product_ref.each()[0].val() 
                wishlist_items.append({ 
                    "item_id": product_info.get("item_id"), 
                    "item_name": product_info.get("name"), 
                    "item_price": product_info.get("price"), 
                    "item_img": product_info.get("image") })
            else:
                # 상품 DB에 없을 때 대비
                wishlist_items.append({
                    "item_id": item_id,
                    "item_name": "알 수 없는 상품",
                    "item_price": "정보 없음",
                    "item_img": url_for('static', filename='img/default.png').replace('/static','')
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

@app.route('/product/<product_id>')
def product_detail(product_id):
    product = DB.get_item_byid(product_id)
    if not product:
        return "해당 상품을 찾을 수 없습니다.", 404
    return render_template('product-detail.html', product=product)


if __name__ == '__main__':
    app.run(debug=True)
