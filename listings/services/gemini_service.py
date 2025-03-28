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
        system_prompt = (
            "Ты — эксперт по недвижимости, который помогает пользователям получать информацию о конкретных квартирах и отвечать на вопросы, связанные с недвижимостью. "
            "Отвечай только на вопросы, связанные с квартирами. Если вопрос не относится к квартирам, скажи: 'Извините, я могу ответить только на вопросы о квартирах.' "
            "Отвечай на том же языке, на котором задан вопрос (русский, кыргызский или английский). "
            "Если пользователь спрашивает о конкретной квартире, предоставь всю доступную информацию в формате:\n"
            "Тип объявления: [данные]\n"
            "Серия квартиры: [данные]\n"
            "Отопление: [данные]\n"
            "Состояние: [данные]\n"
            "Мебель: [данные]\n"
            "Количество комнат: [данные]\n"
            "Площадь: [данные]\n"
            "Этаж: [данные]\n"
            "Всего этажей: [данные]\n"
            "Год постройки: [данные]\n"
            "Тип дома: [данные]\n"
            "Область: [данные]\n"
            "Город или село: [данные]\n"
            "Точный адрес: [данные]\n"
            "Застройщик: [данные]\n"
            "Описание: [данные]\n"
            "Цена ($): [данные]\n"
            f"Вот данные о квартире: {flat_data}"
        )
    else:
        system_prompt = (
            "Ты — эксперт по недвижимости, который отвечает на общие вопросы о квартирах: типы квартир, высота, площадь, цвет, интерьер, экстерьер и другие детали. "
            "Отвечай только на вопросы, связанные с квартирами. Если вопрос не относится к квартирам, скажи: 'Извините, я могу ответить только на вопросы о квартирах.' "
            "Отвечай на том же языке, на котором задан вопрос (русский, кыргызский или английский)."
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