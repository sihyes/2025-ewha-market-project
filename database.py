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
        else:
            # 상품 정보 확인 후 추가
            product = self.db.child("products").order_by_child("item_id").equal_to(str(item_id)).get()
            if product.val():
                p=product.val()
                item_name = p.get("name", "이름 없음")
                item_price = p.get("price", 0)
                item_img = p.get("image", "/static/img/default.png")
            else:
                # 혹시 product DB에 없을 경우 대비
                item_name = "알 수 없는 상품"
                item_price = 0
                item_img = "/static/img/default.png"

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

