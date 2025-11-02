# lms/validators.py
import re
from django.core.exceptions import ValidationError


def validate_video_url(value):
    """
    Валидатор проверяет, что URL ведёт только на YouTube.
    Допустимые значения: youtube.com, youtu.be
    Пустые значения разрешены.
    """
    if value is None or not str(value).strip():
        return

    if not re.search(r"(youtube\.com|youtu\.be)", str(value), re.IGNORECASE):
        raise ValidationError(
            "Только ссылки на YouTube разрешены (youtube.com или youtu.be)."
        )
