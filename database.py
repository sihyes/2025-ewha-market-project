import pyrebase
import json
import sys

class DBhandler:
    def __init__(self):
        try:
            with open('./authentication/firebase_auth.json') as f:
                config = json.load(f)
            firebase = pyrebase.initialize_app(config)
            self.db = firebase.database()
            print("✅ Firebase DB initialized successfully!")
        except FileNotFoundError:
            print("❌ Error: firebase_auth.json 파일이 없거나 경로가 잘못되었습니다.")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Error initializing Firebase: {e}")
            sys.exit(1)

    # ---------------- 상품 ----------------
    def insert_item(self, name, data, img_path):
        item_info = {
            "seller": data['seller'],
            "addr": data['addr'],
            "email": data['email'],
            "category": data['category'],
            "card": data['card'],
            "status": data['status'],
            "phone": data['phone'],
            "img_path": img_path
        }
        self.db.child("item").child(name).set(item_info)
        print(data, img_path)
        return True

    # 모든 상품 가져오기
    def get_items(self):
        items_dict = self.db.child("item").get().val()
        items_list = []
        if items_dict:
            for _, item_info in items_dict.items():
                items_list.append(item_info)
        return items_list

    # 특정 상품 조회
    def get_item_by_id(self, target_item_id):
        items_dict = self.db.child("item").get().val()
        if items_dict:
            for _, item_info in items_dict.items():
                if item_info.get('item_id') == str(target_item_id):
                    return item_info
        return None

    # 상품 등록 (products 컬렉션에 저장)
    def insert_product(self, seller_id, name, price, region, condition, description, image_path):
        try:
            # 고유 item_id 생성 (타임스탬프 기반)
            import time
            item_id = str(int(time.time() * 1000))  # 밀리초 단위 타임스탬프
            
            # 이미지 경로 처리
            if image_path and (image_path.startswith('http://') or image_path.startswith('https://')):
                # 외부 URL인 경우 그대로 사용
                image = image_path
            else:
                # 로컬 파일 경로인 경우
                if image_path:
                    if not image_path.startswith('img/'):
                        image = f'img/{image_path}'
                    else:
                        image = image_path
                else:
                    image = 'img/default.png'
            
            product_info = {
                "item_id": item_id,
                "name": name,
                "price": int(price),
                "region": region,
                "condition": condition,
                "description": description,
                "image": image,
                "seller_id": seller_id
            }
            
            # Firebase의 products 컬렉션에 저장
            self.db.child("products").child(str(item_id)).set(product_info)
            print(f"✅ Product added: {product_info}")
            return True
        except Exception as e:
            print(f"❌ Error inserting product: {e}")
            return False

    # ---------------- 회원 ----------------
    def insert_user(self, data, pw):
        user_info = {
            "id": data['id'],
            "pw": pw,
            "email": data['email'],
            "phone": data['phone']
        }
        if self.user_duplicate_check(str(data['id'])):
            self.db.child("user").push(user_info)
            print("✅ User added:", data)
            return True
        else:
            print("⚠️ Duplicate user ID:", data['id'])
            return False

    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()
        if str(users.val()) == "None":
            return True
        else:
            for res in users.each():
                if res.val().get('id') == id_string:
                    return False
            return True
        
    def find_user(self, id_, pw_):
        users = self.db.child("user").get()
        target_value=[]
        for res in users.each():
            value = res.val()
            if value['id'] == id_ and value['pw'] == pw_:
                return True
        return False

    # ---------------- 찜(Wishlist) ----------------
    def get_wishlist(self, user_id):
        items = self.db.child("wishlist").order_by_child("user_id").equal_to(user_id).get()
        return items

    def toggle_wishlist(self, user_id, item_id):
        key_combo = f"{user_id}_{item_id}"
        wishlist = self.db.child("wishlist").order_by_child("user_id_item_id").equal_to(key_combo).get()

        if wishlist.val():
            for w in wishlist.each():
                self.db.child("wishlist").child(w.key()).remove()
            return False
        product_snapshot = self.db.child("products").order_by_child("item_id").equal_to(str(item_id)).get()
        item_name = "알 수 없는 상품"
        item_price = 0
        item_img = "/static/img/default.png"

        # 상품 정보 확인 후 추가
        if product_snapshot.each():
            for p in product_snapshot.each():
                data = p.val()
                item_name = data.get("name", "이름 없음")
                item_price = data.get("price", 0)
                item_img = data.get("image", "/static/img/default.png")
                break  # 첫 번째 매칭만 사용


            # 🔹 찜 정보 Firebase에 저장
            self.db.child("wishlist").push({
                "user_id": user_id,
                "item_id": item_id,
                "item_name": item_name,
                "item_price": item_price,
                "item_img": item_img,
                "user_id_item_id": key_combo
            })

            return True
        
    # ---------------- 리뷰 ----------------
    def add_review(self, review_data):
        try:
            self.db.child("review").push(review_data)
            print("✅ 리뷰 저장 완료:", review_data)
            return True
        except Exception as e:
            print(f"❌ 리뷰 저장 실패: {e}")
            return False

    def get_all_reviews(self):
        """모든 리뷰 가져오기"""
        try:
            reviews = self.db.child("review").get().val()
            if not reviews:
                return []
            return [r for r in reviews.values()]
        except Exception as e:
            print(f"❌ 리뷰 조회 실패: {e}")
            return []

    def get_review_by_title(self, title):
        """특정 제목의 리뷰 가져오기 (상세 페이지용)"""
        try:
            all_reviews = self.get_all_reviews()
            for r in all_reviews:
                if r.get("title") == title:
                    return r
            return None
        except Exception as e:
            print(f"❌ 리뷰 상세 조회 실패: {e}")
            return None
            return True    
        
   # ---------------- 상품 상세 조회 ----------------
    def get_item_byid(self, item_id):
        """
        상품 ID(item_id)로 products 테이블에서 해당 상품 정보를 가져옴
        """
        products = self.db.child("products").get()
        target_value = None

        if products.each():
            for res in products.each():
                data = res.val()  # 각 상품의 실제 데이터 (딕셔너리 형태)
                # Firebase에 저장된 'item_id' 필드와 비교
                if str(data.get("item_id")) == str(item_id):
                    target_value = data
                    break

        return target_value

    def get_review_by_id(self, review_id):
        """특정 ID(키)의 리뷰 상세 정보를 가져오기"""
        try:
            # review_id는 Firebase의 자동 생성된 key이므로 child(review_id)로 바로 접근
            review_data = self.db.child("review").child(review_id).get().val()
            if review_data:
                # review_data 딕셔너리에 review_id도 포함하여 반환
                review_data['review_id'] = review_id
                return review_data
            return None
        except Exception as e:
            print(f"❌ 리뷰 ID 조회 실패: {e}")
            return None

    def get_heart_byname(self, uid, name):
        hearts = self.db.child("heart").child(uid).get()
        target_value=""
        if hearts.val() == None:
            return target_value
        for res in hearts.each():
            key_value = res.key()
            if key_value == name:
                target_value=res.val()
        return target_value

    def update_heart(self, user_id, isHeart, item):
        heart_info ={
            "interested": isHeart
        }
        self.db.child("heart").child(user_id).child(item).set(heart_info)
        return True
        
    def get_review_by_name(self, product_name):

        reviews_ref = self.db.child("review").get()

        if not reviews_ref.val():
            return None 

        all_reviews = []
        product_name_clean = product_name.strip() 
        
        try:
            reviews_iterator = reviews_ref.each()
            if reviews_iterator is None:
                return None

            for review in reviews_iterator:
                review_data = review.val()
                if not isinstance(review_data, dict):
                    continue
                
                db_name = review_data.get('product_name')
                
                if db_name:
                    r_name_clean = db_name.strip()
                    
                    # 상품명이 일치하는지 확인
                    if r_name_clean == product_name_clean:
                        # Pyrebase의 자동 생성 키(review ID)를 데이터에 포함
                        review_data['review_id'] = review.key() 
                        all_reviews.append(review_data)

        except Exception as e:
            print(f"❌ DB.get_review_by_name 에러 발생: {e}")
            return None

        if not all_reviews:
            return None

        # 가장 최근 리뷰 반환 (review_id 기준 내림차순 정렬)
        latest_review = sorted(
            all_reviews,
            key=lambda r: r['review_id'],
            reverse=True
        )[0]
        
        return latest_review
