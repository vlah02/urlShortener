from flask import Flask, request, jsonify, redirect, render_template
import json
import os
import string
import random

app = Flask(__name__)

DATA_FILE = "urls/shortened_urls.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        formatted_items = []
        for key, value in data.items():
            formatted_item = f'    "{key}": {{\n        "url": "{value["url"]}",\n        "count": {value["count"]}\n    }}'
            formatted_items.append(formatted_item)
        formatted_content = '{\n' + ',\n'.join(formatted_items) + '\n}'
        f.write(formatted_content)

def generate_short_url():
    characters = string.ascii_letters + string.digits
    short_url = ''.join(random.choice(characters) for i in range(6))
    return short_url

@app.route('/', methods=['GET', 'POST'])
def index():
    shortened_url = None
    if request.method == 'POST':
        original_url = request.form['url']
        data = load_data()

        for key, value in data.items():
            if value["url"] == original_url:
                shortened_url = request.url_root + key
                break

        if not shortened_url:
            short_url = generate_short_url()
            while short_url in data:
                short_url = generate_short_url()

            data[short_url] = {"url": original_url, "count": 0}
            save_data(data)
            shortened_url = request.url_root + short_url

    return render_template('index.html', shortened_url=shortened_url)

@app.route('/<short_url>', methods=['GET'])
def redirect_to_url(short_url):
    data = load_data()
    entry = data.get(short_url)
    if entry:
        entry["count"] += 1  # Increment the counter
        save_data(data)
        return redirect(entry["url"])
    return "URL not found", 404

if __name__ == "__main__":
    app.run(debug=True)
