import pyrebase
import json 
class DBhandler:
    def __init__(self):
        with open('./authentication/firebase_auth.json') as f: 
            config=json.load(f )
        firebase = pyrebase.initialize_app(config) 
        self.db = firebase.database()

    def insert_item(self, name, data, img_path): 
        item_info ={
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
        print(data,img_path)
        return True
    
    def insert_user(self, data, pw):
        user_info ={
            "id": data['id'],
            "pw": pw,
            "email": data['email'],
            "phone":data['phone']
        }
        if self.user_duplicate_check(str(data['id'])): 
            self.db.child("user").push(user_info) 
            print(data)
            return True 
        else:
            return False

    def user_duplicate_check(self, id_string):
        users = self.db.child("user").get()

        print("users###",users.val())
        if str(users.val()) == "None": # first registration 
            return True
        else:
            for res in users.each(): 
                value = res.val()
                if value['id'] == id_string: 
                    return False
            return True        
# ---------------- 찜 ----------------
    def get_wishlist(self, user_id):
        items = self.db.child("wishlist").order_by_child("user_id").equal_to(user_id).get()
        return items

    def toggle_wishlist(self, user_id, item_id):
        key_combo = f"{user_id}_{item_id}"
        wishlist = self.db.child("wishlist").order_by_child("user_id_item_id").equal_to(key_combo).get()

        if wishlist.val():  # 이미 찜 → 해제
            for w in wishlist.each():
                self.db.child("wishlist").child(w.key()).remove()
            return False
        else:
            # 🔹 item_id를 이용해 상품 정보 가져오기
            product = self.db.child("products").child(str(item_id)).get()
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