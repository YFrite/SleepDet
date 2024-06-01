import json
import os
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from scripts.converter import parse_edf

app = Flask(__name__)
app.secret_key = "Kakoy-to secret key"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'REC', 'rec'}
ITEMS = {}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/', methods=['GET', 'POST'])
def main_page():
    return render_template('index.html', items=ITEMS["dataset"])


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect("/")
    file = request.files['file']
    if file.filename == '':
        return redirect(url_for('main_page'))
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        checkbox_data = request.form.get('checkboxData')

        if checkbox_data:
            checkbox_data = json.loads(checkbox_data)
        features_to_use = []
        for key, value in checkbox_data.items():
            if value:
                features_to_use.append(key)

        arr = parse_edf(filename, features_to_use)
        print(arr)

        return checkbox_data
    return 'Invalid file format. Only .rec files are allowed.'


@app.route('/input-data', methods=['GET', 'POST'])
def input_data():
    if request.method == 'POST':
        print(request.form.get('inputBoxDatas'))
    return render_template("input_data.html", items=ITEMS["input_data"])


if __name__ == '__main__':
    with open('data.json', 'r', encoding="UTF-8") as f:
        ITEMS = json.load(f)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=False, host="0.0.0.0", port=5000)
