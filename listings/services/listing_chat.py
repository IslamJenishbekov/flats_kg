from .gemini_service import get_gemini_response

def get_response(message: str, flat_data: dict) -> str:
    return get_gemini_response(message, flat_data)