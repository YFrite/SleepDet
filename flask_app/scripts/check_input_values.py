import json


def check_input_values(values_json):
    with open("static/files/accept_values.json", 'r', encoding="UTF-8") as f:
        data = json.load(f)
    for key, value in data.items():
        if not (int(value[0]) <= int(values_json[key]) <= int(value[1])):
            return False
    return True


def check_checkboxes(values_json):
    return sum(x for x in json.loads(values_json).values() if x) >= 2
