from flask_app.scripts.pipeline.inference import predict


def get_ml_answer(table_data, channels):
    data = predict(channels, table_data)
    confidence = data["CONFIDENCE"]
    result = data["RESULT"]
    hypopnea_count = data["HYPOPNEA_COUNT"]
    apnea_count = data["APNEA_COUNT"]
    return {"APNEA_COUNT": apnea_count, "HYPOPNEA_COUNT": hypopnea_count,
            "COUNT_OF_VIOLATIONS": apnea_count + hypopnea_count,
            "RESULT": "наличие" if result else "отсутствие", "CONFIDENCE": round(confidence * 100, 4) }


def get_severity(ahi):
    if ahi < 5:
        return "Пациент здоров"
    elif ahi < 15:
        return "Умеренная"
    elif ahi < 30:
        return "Средняя"
    return "Сильная"
