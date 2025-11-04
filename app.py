from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from database import DBhandler
import hashlib
import sys

app = Flask(__name__)
app.config["SECRET_KEY"] = "helloosp"

DB = DBhandler()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/feature-list')
def feature_list():
    return render_template('feature-list.html')

@app.route('/review-list')
def review_list():
    return render_template('review-list.html')

@app.route('/product-register')
def product_register():
    return render_template('product-register.html')

@app.route('/review-register')
def review_register():
    return render_template('review-register.html')

    # @app.route("/login")
    # def login():
    #     return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route('/check_duplicate')
def check_duplicate():
    user_id = request.args.get('id')
    exists = not DB.user_duplicate_check(user_id)  # 중복이면 False를 반환하니까 반전
    return jsonify({"exists": exists})

@app.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    if DB.insert_user(data,pw_hash):
        return render_template("login.html")
    else:
        flash("user id already exist!")
        return render_template("signup.html")

@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")

@app.route("/submit_item_post", methods=['POST'])
def reg_item_submit_post(): 
    image_file=request.files["file"]
    image_file.save("static/image/{}".format(image_file.filename))
    data=request.form
    DB.insert_item(data['name'], data, image_file.filename)
    return render_template("submit_item_result.html", data=data, img_path= "static/images/{}".format(image_file.filename))

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('index'))

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


@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("로그아웃 되었습니다.")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
