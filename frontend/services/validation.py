import re


_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_PATTERN = re.compile(r"^\+?[0-9 ()-]+$")
_PHONE_DIGITS_PATTERN = re.compile(r"[0-9]")


def validate_contact(name: str, phone: str, email: str) -> str | None:
    if not name.strip():
        return "Informe o nome."
    if not phone.strip():
        return "Informe o telefone."
    if not _PHONE_PATTERN.fullmatch(phone.strip()):
        return "Informe um telefone com apenas números e separadores válidos."
    phone_digits = _PHONE_DIGITS_PATTERN.findall(phone)
    if not 8 <= len(phone_digits) <= 15:
        return "Informe um telefone com 8 a 15 dígitos."
    if email.strip() and not _EMAIL_PATTERN.fullmatch(email.strip()):
        return "Informe um email válido ou deixe o campo vazio."
    return None
