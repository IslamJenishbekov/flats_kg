from catboost import CatBoostRegressor
import pandas as pd
from decimal import Decimal

# Загрузка модели один раз (вне функции)
catboost_model = CatBoostRegressor()
catboost_model.load_model("listings/services/catboost_model.cbm")

# Определим список фичей в нужном порядке (как в обучении)
features = [
    'type_offer', 'series', 'heating', 'condition', 'furniture',
    'floor', 'address', 'description', 'room_num', 'area',
    'total_floors', 'wall_material', 'building_year', 'region', 'city'
]

def get_predicted_price(flat_data: dict) -> float:
    # Преобразуем поля с неправильными именами
    flat_data = {  # Переименовываем поля в соответствии с моделью
        'type_offer': flat_data.get('offer_type'),  # заменяем offer_type на type_offer
        **flat_data  # копируем остальные поля без изменений
    }

    # Проверим, если отсутствует поле description, то добавим его
    flat_data.setdefault('description', '')

    # Преобразуем Decimal в float
    for key in flat_data:
        if isinstance(flat_data[key], Decimal):
            flat_data[key] = float(flat_data[key])

    # Собираем данные в нужном порядке
    sample = [flat_data.get(f, None) for f in features]

    # Предсказание
    try:
        predicted_price = catboost_model.predict([sample])[0]
        return float(predicted_price)
    except Exception as e:
        print("[EXCEPTION] Error during prediction")
        for i, f in enumerate(features):
            print(f"{f}: {type(sample[i]).__name__} = {sample[i]}")
        raise e



