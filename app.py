from flask import Flask, render_template

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
