from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import os # 파일 업로드를 위해 필요

from urllib.parse import unquote

app = Flask(__name__)
# 💡 충돌 해결: C와 D 브랜치 모두 설정이 동일하므로 하나의 코드로 통합
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


def format_price(value):
    """숫자를 받아 쉼표로 포맷팅합니다."""
    # 숫자가 아닌 값이 들어왔을 경우를 대비해 처리 (예: 문자열 "10000"도 처리)
    try:
        value = int(value)
    except (ValueError, TypeError):
        return value # 포맷 불가 시 원본 값 반환

    return "{:,}".format(value)

# Flask 앱에 필터 등록
app.jinja_env.filters['format_price'] = format_price

@app.route('/')
def index():
    return render_template('home.html')


@app.route('/feature-list')
def feature_list():
     #1. 페이지네이션 파라미터
    page = request.args.get("page", 0, type=int)
    per_page = 10   # 페이지당 상품 10개
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
                "image": data.get("image"), # <- DB image 그대로 사용
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
        if image_url:
            # 외부 URL 사용
            image_path = image_url
        elif 'image_file' in request.files:
            file = request.files['image_file']
            if file and file.filename:
                # 파일 업로드 처리 (현재는 URL만 지원, 파일은 추후 구현)
                # 일단은 기본 이미지 사용
                image_path = 'img/default.png'
        
        # Firebase에 상품 저장
        if DB.insert_product(seller_id, name, price, region, condition, description, image_path):
            flash('상품이 등록되었습니다.')
            return redirect(url_for('feature_list'))
        else:
            flash('상품 등록에 실패했습니다.')
            return redirect(url_for('product_register'))
    
    return render_template('product-register.html')

# 💡 충돌 해결: 리뷰 목록 라우트 통합 (리뷰 데이터 가져오기 + 팝업 파라미터 처리)
@app.route("/review-list")
def review_list():
    # 리뷰 데이터 가져오기
    reviews = DB.get_all_reviews()
    
    # 팝업을 위한 상품 이름 가져오기
    product_name_no_review = request.args.get("no_review_for")
    
    # 모든 데이터를 템플릿으로 전달합니다.
    return render_template("review-list.html", 
                           reviews=reviews,
                           product_name_no_review=product_name_no_review)

@app.route('/review/<title>')
def review_detail_by_title(title): # 💡 함수명 변경: 라우트 이름과 충돌 방지
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


def get_latest_review_by_product_name(product_name):
    """
    [디버깅 최종판] 
    - 함수가 받은 상품명과 DB에 있는 상품명을 터미널에 모두 출력합니다.
    """
    # 1. 함수가 상세 페이지에서 어떤 이름으로 호출되었는지 출력
    print("\n" + "="*50)
    print(f"[DEBUG] 1. 상세 페이지가 요청한 상품명: '[{product_name}]'")
    print(f"[DEBUG]    (길이: {len(product_name)})")
    print("="*50)

    reviews_ref = DB.db.child("review").get()

    if not reviews_ref.val():
        print("[DEBUG] 2. 'review' 노드를 찾을 수 없거나 비어있습니다. (DB 확인 필요)")
        return None

    all_reviews = []
    
    try:
        reviews_iterator = reviews_ref.each()
        if reviews_iterator is None:
            print("[DEBUG] 2. reviews_iterator가 None입니다. (데이터가 없는 듯합니다)")
            return None

        print("[DEBUG] 2. DB의 'review' 노드에서 모든 상품명을 검색합니다...")
        for review in reviews_iterator:
            review_data = review.val()
            if not isinstance(review_data, dict):
                continue
            
            db_name = review_data.get('product_name')
            review_data['review_id'] = review.key()
            all_reviews.append(review_data)
            
            # 3. DB에 있는 모든 리뷰의 상품명을 터미널에 출력
            if db_name:
                print(f"[DEBUG]    -> DB에 저장된 이름: '[{db_name}]' (길이: {len(db_name)})")
            else:
                print(f"[DEBUG]    -> DB에 'product_name' 필드가 없는 리뷰 발견 (ID: {review.key()})")

    except Exception as e:
        print(f"[DEBUG] 2. 리뷰 처리 중 심각한 에러 발생: {e}")
        return None

    if not all_reviews:
        print("[DEBUG] 3. all_reviews 리스트가 비었습니다. (리뷰가 0개)")
        print("="*50 + "\n")
        return None # 일치하는 리뷰가 없음

    # 4. 일치하는 리뷰 필터링 (양쪽 다 공백 제거 후 비교)
    print("[DEBUG] 3. 공백을 제거하고 이름 비교를 시작합니다...")
    product_name_clean = product_name.strip() 

    matching_reviews = []
    for r in all_reviews:
        r_name = r.get('product_name')
        if r_name:
            r_name_clean = r_name.strip()
            
            if r_name_clean == product_name_clean:
                matching_reviews.append(r)
                print(f"[DEBUG]    -> ⭐️ 일치! (ID: {r['review_id']})")
            # else:
            #    print(f"[DEBUG]    -> 불일치: '[{r_name_clean}]' != '[{product_name_clean}]'")


    if not matching_reviews:
        print("[DEBUG] 4. 최종 결과: 일치하는 리뷰를 찾지 못했습니다.")
        print("="*50 + "\n")
        return None # 일치하는 리뷰가 없음

    # 5. 성공
    latest_review = sorted(
        matching_reviews,
        key=lambda r: r['review_id'],
        reverse=True
    )[0]
    
    print(f"[DEBUG] 4. 최종 결과: ⭐️ 성공! 리뷰 ID [{latest_review['review_id']}]를 반환합니다.")
    print("="*50 + "\n")
    return latest_review['review_id']

@app.route("/redirect-to-product-review/<product_name>")
def redirect_to_latest_review(product_name):
    product_name_decoded = unquote(product_name) 
    
    latest_review_id = get_latest_review_by_product_name(product_name_decoded)

    if latest_review_id:
        # 1. 리뷰 있음: detailed-review.html로 이동 (review_id 사용)
        return redirect(url_for('review_detail', review_id=latest_review_id))
    else:
        # 2. 리뷰 없음: 팝업을 띄우기 위해 파라미터를 review_list로 전달
        return redirect(url_for('review_list', no_review_for=product_name_decoded))

@app.route("/review-detail")
def review_detail(): # URL 파라미터로 review_id를 받는 상세 페이지
    review_id = request.args.get("review_id")
    if review_id:
        # 🌟 수정한 부분: DBhandler를 사용하여 리뷰 상세 정보를 가져옵니다.
        review_data = DB.get_review_by_id(review_id) 
        
        if review_data:
            # 🌟 'review'라는 이름으로 템플릿에 전달
            return render_template("detailed-review.html", review=review_data) 
        else:
            flash(f"리뷰 ID {review_id}를 찾을 수 없습니다.")
            return redirect(url_for('review_list'))
    else:
        # ID가 없으면 리뷰 목록으로 리디렉션하거나 에러 처리
        return redirect(url_for('review_list'))

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
    exists = not DB.user_duplicate_check(user_id) # 중복이면 False를 반환하니까 반전
    return jsonify({"exists": exists})


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        id_ = request.form['id']
        pw = request.form['pw']
        pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()

        # 💡 충돌 해결: login 함수 내부의 중복된 user 조회 로직을 find_user로 통일
        if DB.find_user(id_,pw_hash): 
            session['user'] = id_ # 로그인 성공하면 세션에 저장
            return redirect(url_for('index')) # 로그인 후 원래 화면으로
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
    session.clear() #예제코드에 맞추어 변경
    return redirect(url_for('index'))

@app.route('/product/<product_id>')
def product_detail(product_id):
    try:
        # 1. Firebase 'products' 노드에서 'item_id'가 product_id와 일치하는 것을 찾습니다.
        product_ref = DB.db.child("products").order_by_child("item_id").equal_to(str(product_id)).get()

        product_data = None
        
        # 2. .val()이 비어있지 않고, .each()로 실제 데이터가 있는지 확인
        if product_ref.val(): 
            for p in product_ref.each():
                product_data = p.val()
                # item_id는 고유하므로 첫 번째 아이템만 가져오고 중단
                break 

        # 3. product_data가 None이면 (즉, 상품을 못 찾았으면) 404 에러
        if product_data is None:
            return "해당 상품을 찾을 수 없습니다.", 404
        
        # 4. (선택적) 이미지 경로 보정
        image_path = product_data.get("image", "")
        if image_path.startswith("/static/"):
            product_data["image"] = image_path.replace("/static/", "")

        # 5. 템플릿으로 product_data (딕셔너리)를 전달합니다.
        return render_template('product-detail.html', product=product_data)

    except Exception as e:
        # Firebase 연결 오류 등 예외 처리
        print(f"상품 상세 정보 로드 중 에러: {e}")
        return f"상품 정보를 불러오는 중 오류가 발생했습니다: {e}", 500

@app.route('/purchase/<int:product_id>')
def purchase(product_id):

    products_ref = DB.db.child("products").get()
    products = [p.val() for p in products_ref.each()] if products_ref.each() else []
    
    # item_id 비교하여 해당 상품 찾기
    product = next((p for p in products if str(p['item_id']) == str(product_id)), None)
    
    if not product:
        return "구매할 상품을 찾을 수 없습니다.", 404
    
    # image 경로 조정 
    if product.get("image", "").startswith("/static/"):
        product["image"] = product["image"].replace("/static/", "")
    
    try:
        product['price'] = int(product['price'])
    except ValueError:
        product['price'] = 0

    # 이제 product 변수가 정의되었으므로 템플릿에 전달할 수 있습니다.
    return render_template('purchase.html', product=product)

if __name__ == '__main__':
    # 조건부 샘플 리뷰 데이터 추가
    initial_reviews = DB.get_all_reviews() 

    # 💡 충돌 해결: C와 D 브랜치 모두 메인 실행 로직이 필요. 리뷰 샘플 추가는 D 브랜치 기능.
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