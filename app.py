from flask import Flask, request, jsonify, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import string
import random

load_dotenv()

app = Flask(__name__)

# Connection parameters
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class ShortenedURL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    short_url = db.Column(db.String(6), unique=True, nullable=False)
    original_url = db.Column(db.String(2048), nullable=False)
    count = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<ShortenedURL {self.short_url}>'

with app.app_context():
    db.create_all()

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for i in range(6))
    return short_url

@app.route('/', methods=['GET', 'POST'])
def index():
    shortened_url = None
    if request.method == 'POST':
        original_url = request.form['url']
        entry = ShortenedURL.query.filter_by(original_url=original_url).first()

        if entry:
            shortened_url = request.url_root + entry.short_url
        else:
            short_url = generate_short_url()
            while ShortenedURL.query.filter_by(short_url=short_url).first() is not None:
                short_url = generate_short_url()

            new_entry = ShortenedURL(short_url=short_url, original_url=original_url)
            db.session.add(new_entry)
            db.session.commit()
            shortened_url = request.url_root + short_url

    return render_template('index.html', shortened_url=shortened_url)

@app.route('/<short_url>', methods=['GET'])
def redirect_to_url(short_url):
    entry = ShortenedURL.query.filter_by(short_url=short_url).first()
    if entry:
        entry.count += 1
        db.session.commit()
        return redirect(entry.original_url)
    return "URL not found", 404

if __name__ == "__main__":
    app.run(debug=True)




# from flask import Flask, render_template
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.exc import OperationalError
# from sqlalchemy.sql import text
#
# app = Flask(__name__)
#
# # Connection parameters
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:ZRo5QZs9Qku0hgO@bitter-smoke-5766-db.internal:5432/bitter_smoke_5766'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#
# db = SQLAlchemy(app)
#
# def test_db_connection():
#     try:
#         result = db.session.execute(text('SELECT 1'))  # This will try to run a simple SELECT statement
#         return True, "Connected successfully."
#     except OperationalError as e:
#         return False, str(e)
#
# @app.route('/')
# def index():
#     status, message = test_db_connection()
#     return render_template('index.html', status=status, message=message)
#
# if __name__ == '__main__':
#     app.run(debug=True)