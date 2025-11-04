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
        """
        user_id와 item_id 조합으로 찜 상태를 토글.
        True → 찜 완료, False → 찜 해제
        """
        key_combo = f"{user_id}_{item_id}"
        wishlist = self.db.child("wishlist").order_by_child("user_id_item_id").equal_to(key_combo).get()
        
        if wishlist.val():  # 이미 찜 → 해제
            for w in wishlist.each():
                self.db.child("wishlist").child(w.key()).remove()
            return False
        else:  # 찜 안됨 → 등록
            self.db.child("wishlist").push({
                "user_id": user_id,
                "item_id": item_id,
                "user_id_item_id": key_combo
            })
            return True