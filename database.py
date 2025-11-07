import pyrebase
import json
import sys

class DBhandler:
    # (이전과 동일한 __init__ 함수)
    def __init__(self):
        try:
            with open('./authentication/firebase_auth.json') as f:
                config = json.load(f)
            firebase = pyrebase.initialize_app(config)
            self.db = firebase.database() 
            print("Firebase DB initialized successfully!")
        except FileNotFoundError:
            print("Error: firebase_auth.json 파일이 없거나 경로가 잘못되었습니다.")
            sys.exit(1)
        except Exception as e:
            print(f"Error initializing Firebase: {e}")
            sys.exit(1)

    # 1. 모든 상품 정보를 가져오는 함수 (리스트 페이지용)
    def get_items(self):
        items_dict = self.db.child("item").get().val()
        
        # 딕셔너리 형태로 받은 데이터를 리스트 형태로 변환합니다.
        items_list = []
        if items_dict:
            for firebase_key, item_info in items_dict.items():
                # DB의 고유 키('-OdNLRpI_2IYSQGGWroP')를 참조할 필요가 없으므로,
                # 내부 필드만 사용하여 리스트를 만듭니다.
                items_list.append(item_info)
                
        return items_list 

    # 2. item_id를 기준으로 특정 상품 정보를 가져오는 함수 (상세 페이지용)
    def get_item_by_id(self, target_item_id):
        # 'item' 노드 아래의 모든 데이터를 가져옵니다.
        items_dict = self.db.child("item").get().val()
        
        if items_dict:
            # 모든 상품을 순회하며 'item_id'가 일치하는 상품을 찾습니다.
            for firebase_key, item_info in items_dict.items():
                if item_info.get('item_id') == str(target_item_id):
                    return item_info # 일치하는 상품 정보를 반환합니다.
        
        return None # 일치하는 상품이 없으면 None을 반환합니다.