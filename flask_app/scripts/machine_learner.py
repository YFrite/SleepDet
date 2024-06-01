def predict(table_data, channels):

    confidence = 1
    result = 0
    hypopnea_count = 0
    apnea_count = 0
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
