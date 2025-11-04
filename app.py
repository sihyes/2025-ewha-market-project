from flask import Flask, render_template, request, flash, redirect, url_for, session
import hashlib
import sys

app = Flask(__name__)
app.config["SECRET_KEY"] = "helloosp"

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

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/signup")
def signup():
    return render_template("signup.html")

@app.route("/signup_post", methods=['POST'])
def register_user():
    data=request.form
    pw=request.form['pw']
    pw_hash = hashlib.sha256(pw.encode('utf-8')).hexdigest()
    # if DB.insert_user(data,pw_hash):
    #     return render_template("login.html")
    # else:
    #     flash("user id already exist!")
    # return rendertemplate("signup.html")

@app.route("/wishlist")
def wishlist():
    return render_template("wishlist.html")

if __name__ == '__main__':
    app.run(debug=True)
