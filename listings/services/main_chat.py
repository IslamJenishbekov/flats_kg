from .gemini_service import get_gemini_response

def get_response(message: str) -> str:
    return get_gemini_response(message)