import json
import os
import shutil
import time
import numpy as np

from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from scripts.converter import parse_edf
from scripts.check_input_values import check_input_values, check_checkboxes
from scripts.template_report import create_docx_file
from scripts.machine_learner import get_ml_answer
from scripts.dashboard import create_dashboard, create_dashboards
from flask_app.scripts.pipeline.inference import init_models

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config["REPORT_FOLDER"] = "reports"
app.config['SAVE_IMAGES_FOLDER'] = "uploads/images"
app.config['ALLOWED_EXTENSIONS'] = {'REC', 'rec'}
FIELDS_TO_ML = ["AGE", "SEX", "HEIGHT", "WEIGHT", "PULSE", "BPSYS", "BPDIA"]
INPUT_CHARACTER = ""
DATA = np.array([])
ITEMS = {}
PARAMS = {}
CONTENT = {
    "DOCTOR_FULL_NAME": "",
    "PATIENT_FULL_NAME": "",
    "SEX": "",
    "AGE": "",
    "WEIGHT": "",
    "HEIGHT": "",
    "PULSE": "",
    "BPSYS": "",
    "BPDIA": "",
    "TIME_SOUND": "",
    "TYPES": "",
    "TIME_PROCESSING": "",
    "RESULT": "",
    "COUNT_OF_VIOLATIONS": "",
    "APNEA_COUNT": "",
    "HYPOPNEA_COUNT": "",
    "APNEA_INDEX": "",
    "HYPOPNEA_INDEX": "",
    "APNEA_HYPOPNEA_INDEX": ""
}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def checker(params, checkbox_data, filename):
    if filename == "":
        return 'Файл не выбран. Выберите файл'
    if not allowed_file(filename):
        return "Файл не является .rec"
    if not check_input_values(params):
        return "Значения не входят в диапазон"
    if not check_checkboxes(checkbox_data):
        return "Выбраны не >= 2 каналов"


def data_preparation(time_start):
    global DATA, CONTENT
    CONTENT["TIME_SOUND"] = round(DATA.shape[1] / 200 / 60, 6)
    CONTENT["APNEA_INDEX"] = CONTENT["APNEA_COUNT"] / CONTENT["TIME_SOUND"]
    CONTENT["HYPOPNEA_INDEX"] = CONTENT["HYPOPNEA_COUNT"] / CONTENT["TIME_SOUND"]
    CONTENT["APNEA_HYPOPNEA_INDEX"] = CONTENT["HYPOPNEA_INDEX"] + CONTENT["APNEA_INDEX"]
    CONTENT["TIME_PROCESSING"] = round(time.time() - time_start, 6)
    CONTENT["SEX"] = "Мужской" if CONTENT["SEX"] else "Женский"

@app.route('/', methods=['GET', 'POST'])
def main_page():
    return render_template('index.html', features=ITEMS["dataset"], params=ITEMS["params"],
                           error=request.args.get("error", ""))


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global INPUT_CHARACTER, DATA, CONTENT
    time_start = time.time()
    try:
        if 'file' not in request.files:
            return redirect(url_for("main_page", error="Файла нет"))

        file = request.files['file']
        checkbox_data = request.form.get('checkboxData')
        params = json.loads(request.form.get('paramsData'))

        if errors := checker(params, checkbox_data, file.filename):
            return redirect(url_for('main_page', error=errors))

        if checkbox_data:
            checkbox_data = json.loads(checkbox_data)

        for key, value in params.items():
            CONTENT[key.upper()] = value

        features_to_use = []
        for key, value in checkbox_data.items():
            if value:
                features_to_use.append(key)

        CONTENT["TYPES"] = str(features_to_use)
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        array = [int(CONTENT[x]) for x in FIELDS_TO_ML]
        array.append(int(CONTENT["WEIGHT"]) / int(CONTENT["HEIGHT"]))
        INPUT_CHARACTER = np.array(array, dtype="float32")
        file.save(filepath)
        try:
            DATA = parse_edf(filename, features_to_use)
        except Exception as e:
            error = (f'Error parsing file: {e}')
            return redirect(url_for('main_page', error=error))

        results = get_ml_answer(DATA, INPUT_CHARACTER)

        for key, value in results.items():
            CONTENT[key] = value

        data_preparation(time_start)

        create_dashboards(features_to_use, DATA)

        create_docx_file(app.config["REPORT_FOLDER"], CONTENT["PATIENT_FULL_NAME"].replace(" ", "_"), CONTENT)

        return redirect(url_for('download'))
    except Exception as e:
        print(f'An error occurred: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/download')
def download():
    path = (f'{app.config["REPORT_FOLDER"]}/'
            f'{CONTENT["PATIENT_FULL_NAME"].replace(" ", "_")}.docx')

    return send_file(path, as_attachment=True)


if __name__ == '__main__':
    with open('static/files/data.json', 'r', encoding="UTF-8") as f:
        ITEMS = json.load(f)
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config["REPORT_FOLDER"], exist_ok=True)
    #shutil.rmtree(app.config['SAVE_IMAGES_FOLDER'])
    os.makedirs(app.config['SAVE_IMAGES_FOLDER'], exist_ok=True)
    init_models()
    app.run(debug=False, host="0.0.0.0", port=5000)
