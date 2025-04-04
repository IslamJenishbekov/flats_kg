import os
from dotenv import load_dotenv
import google.generativeai as genai

# Загружаем .zhoomarts_env из корня проекта
load_dotenv(os.path.join(os.path.dirname(__file__), r".zhoomarts_env"))


def get_gemini_response(prompt: str, flat_data: dict = None) -> str:
    """
    Получает ответ от модели Gemini на основе пользовательского запроса.

    Args:
        prompt (str): Вопрос или запрос пользователя.
        flat_data (dict, optional): Данные о конкретной квартире (для listing_chat).

    Returns:
        str: Ответ от модели Gemini.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не найден в .zhoomarts_env")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")  # Используем gemini-pro

    # Определяем системный промпт в зависимости от наличия данных о квартире
    if flat_data:
        system_prompt = f"""
        Ты наш ИИ ассистент для консультации по конкретному объявлению.
        Вот информация по объявлению:
        количество комнат - {flat_data['room_num']},
        адрес - {flat_data['address']},
        тип предложения - {flat_data['offer_type']},
        серия квартиры - {flat_data['series']},
        отопление - {flat_data['heating']},
        наличие мебели - {flat_data['furniture']},
        площадь - {flat_data['area']},
        этаж квартиры - {flat_data['floor']},
        общее количество этажей - {flat_data['total_floors']},
        год постройки дома - {flat_data['building_year']},
        город - {flat_data['city']},
        регион - {flat_data['region']},
        описание от продавца - {flat_data['description']},
        цена квартиры - {flat_data['price']}.
        Дай больший приоритет описанию от продавца.
        Будь вежлив, любезен и учтив с клиентами!
        Опираясь на эту информацию, теперь дай лаконичный ответ на вопрос клиента: 
        """
    else:
        system_prompt = (
            "Ты — эксперт по недвижимости, который отвечает на общие вопросы о квартирах: типы квартир, высота, площадь, цвет, интерьер, экстерьер и другие детали. "
            "Отвечай только на вопросы, связанные с квартирами. Если вопрос не относится к квартирам, скажи: 'Извините, я могу ответить только на вопросы о квартирах.' "
            "Отвечай на том же языке, на котором задан вопрос (русский, кыргызский или английский)."
            "Будь вежлив, любезен и учтив с клиентами!"
        )

    # Формируем запрос и получаем ответ
    try:
        response = model.generate_content(
            f"{system_prompt}\n\nПользователь: {prompt}",
            generation_config=genai.types.GenerationConfig(
                response_mime_type="text/plain"
            )
        )
        return response.text.strip()
    except Exception as e:
        return f"Ошибка при обращении к Gemini: {str(e)}"


if __name__ == "__main__":
    # Пример использования
    test_prompt = "Какие бывают типы квартир?"
    print(get_gemini_response(test_prompt))

    test_flat_data = {
        "type": "Продажа",
        "series": "105 серия",
        "heating": "Центральное",
        "condition": "Евроремонт",
        "furniture": "Частично меблирована",
        "rooms": 2,
        "area": 60,
        "floor": 3,
        "total_floors": 9,
        "year": 2015,
        "house_type": "Панельный",
        "region": "Чуйская область",
        "city": "Бишкек",
        "address": "ул. Ленина 15",
        "developer": "ЭлитСтрой",
        "description": "Светлая квартира с видом на горы, можете связаться по номеру телефона 0708135144",
        "price": 75000
    }
    print('---------------------------------------------------------')
    test_prompt_with_data = "Как связаться с владельцем?"
    print(get_gemini_response(test_prompt_with_data, test_flat_data))
