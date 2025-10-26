# lms/validators.py
from urllib.parse import urlparse
from django.core.exceptions import ValidationError


ALLOWED_DOMAINS = ("youtube.com", "youtu.be")


def validate_video_url(value):
    """
    Валидатор: разрешены только видео с youtube.com (включая www.youtube.com)
    и короткие ссылки youtu.be. Пустые значения пропускаются (null/blank).
    """
    if not value:
        return

    parsed = urlparse(value)
    netloc = (parsed.netloc or "").lower()

    # netloc может быть 'www.youtube.com', 'm.youtube.com', 'youtube.com'
    # допустим, если домен оканчивается на youtube.com или равен youtu.be
    allowed = False
    for domain in ALLOWED_DOMAINS:
        if netloc.endswith(domain):
            allowed = True
            break

    if not allowed:
        raise ValidationError("Только ссылки на YouTube разрешены (youtube.com или youtu.be).")
